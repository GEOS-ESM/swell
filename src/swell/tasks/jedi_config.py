# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase
from swell.configuration.configuration import return_configuration_path
from swell.utilities.sat_db_utils import run_sat_db_process

import os
import re
import yaml
import itertools
from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------


def ranges(i):
    for _, group in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        group = list(group)
        yield group[0][1], group[-1][1]


# --------------------------------------------------------------------------------------------------


class JediConfig(taskBase):

    def execute(self):

        """Generates the yaml configuration needed to run the JEDI executable.

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.

        """

        # Parse config
        # ------------
        time_window = self.config.get('current_cycle')
        update_channels = self.config.get('update channels from database')
        use_geos_sat_db = self.config.get('use geos satellite channel database')
        obs = self.config.get('OBSERVATIONS')

        sat_db_yaml_loc = os.path.join(return_configuration_path(), 'satellite_channels')

        print(sat_db_yaml_loc)

        cycle_dt = dt.strptime(time_window, '%Y-%m-%dT%H:%M:%SZ')

        if update_channels:

            # Manage satellite database preparation
            # -------------------------------------
            if use_geos_sat_db:

                # Clone GEOSana_GridComp and generate database data frame
                sat_db = run_sat_db_process(self.config.get('geos_dir'), self.logger)

            # Loop over observation operators to update instrument channels in loaded config
            # ------------------------------------------------------------------------------
            for ob in obs:

                name = ob['obs space']['name']

                # Delete obs filters
                # ------------------
                del ob['obs filters']

                if '_' in name:
                    sat_instr_list = name.split('_')
                    instr = sat_instr_list[0]
                    sat = sat_instr_list[1]

                    try:
                        if not use_geos_sat_db:

                            # Open observation yaml file
                            # --------------------------
                            with open(sat_db_yaml_loc + sat + '.yaml', 'r') as file:
                                sat_dict = yaml.full_load(file)
                                instr_dict = sat_dict[instr]

                            # Find instrument channel ranges for given cycle time
                            # ---------------------------------------------------
                            instr_ind = 999
                            for ind in range(len(instr_dict)):
                                begin = dt.strptime(instr_dict[ind]['begin date'],
                                                    '%Y-%m-%dT%H:%M:%S')
                                end = dt.strptime(instr_dict[ind]['end date'], '%Y-%m-%dT%H:%M:%S')
                                if((cycle_dt >= begin) and (cycle_dt < end)):
                                    instr_ind = ind
                            assert(instr_ind != 999)
                            instr_ch_list = instr_dict[ind]['channels']

                        else:

                            # Extract instrument dataframe from loaded satellite database
                            # -----------------------------------------------------------
                            sat_df = sat_db.loc[sat_db['sat'] == sat]
                            instr_df = sat_df.loc[sat_df['instr'] == instr]

                            # Find instrument channel ranges for given cycle time
                            # ---------------------------------------------------
                            instr_ind = 999
                            for ind in range(len(instr_df)):
                                begin = dt.strptime(instr_df['start'][ind], '%Y%m%d%H%M%S')
                                end = dt.strptime(instr_df['end'][ind], '%Y%m%d%H%M%S')
                                if((cycle_dt >= begin) and (cycle_dt < end)):
                                    instr_ind = ind
                            assert(instr_ind != 999)
                            instr_ch_list = instr_df['channels'][ind]

                        # Process instrument channel list into ranges
                        # -------------------------------------------
                        instr_ch_list = [int(i) for i in instr_ch_list]
                        ch_ranges = list(ranges(instr_ch_list))
                        new_ch_str = ''
                        for ch_range in ch_ranges:
                            if(ch_range[0] != ch_range[1]):
                                new_ch_str = new_ch_str + str(ch_range[0]) + '-' + \
                                             str(ch_range[1]) + ','
                            else:
                                new_ch_str += str(ch_range[0]) + ','
                        new_ch_str = new_ch_str[0:-1]

                        # Update channel range directly in loaded config
                        # ----------------------------------------------
                        ob['obs space']['channels'] = new_ch_str

                    except AssertionError:
                        self.logger.info('sat {} and instr {} are not in the sat database'.
                                         format(sat, instr))
                        continue

        # Set full path to the templated config file
        # ------------------------------------------
        jedi_conf_path = os.path.join(self.config.get("suite_dir"), "jedi_config.yaml")

        # Open the template file to dictionary
        # ------------------------------------
        with open(jedi_conf_path, 'r') as ymlfile:
            jedi_conf = yaml.safe_load(ymlfile)

        # Loop over the dictionary and replace elements
        # ---------------------------------------------
        for key in jedi_conf:

            # Strip special characters from element
            element = jedi_conf[key]
            element = element.replace("$", "")
            element = element.replace("{", "")
            element = element.replace("}", "")

            # Replace with element from filled config
            jedi_conf[key] = self.config.get(element)

        # Remove some keys that do not pass yaml validation
        # -------------------------------------------------
        del jedi_conf['initial condition']['filename']

        # Filename for output yaml
        # ------------------------
        cycle_dir = self.config.get("cycle_dir")
        if not os.path.exists(cycle_dir):
            os.makedirs(cycle_dir, 0o755, exist_ok=True)

        jedi_conf_output = os.path.join(cycle_dir, "jedi_config.yaml")

        # Write out the final yaml file
        # -----------------------------
        with open(jedi_conf_output, 'w') as outfile:
            yaml.dump(jedi_conf, outfile, default_flow_style=False)
