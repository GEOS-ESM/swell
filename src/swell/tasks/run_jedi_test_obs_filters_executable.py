# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable


# --------------------------------------------------------------------------------------------------


class RunJediHofxExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Jedi application name
        # ---------------------
        jedi_application = 'test_obs_filters'

        # Parse configuration
        # -------------------
        window_offset = self.config.window_offset()
        window_length = self.config.window_length()
        bkg_time_offset = self.config.background_time_offset()
        observations = self.config.observations()

        # Compute data assimilation window parameters
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_iso = self.da_window_params.window_begin_iso(window_offset)
        window_end_iso = self.da_window_params.window_end_iso(window_offset, window_length)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        background_time = self.da_window_params.background_time(window_offset, bkg_time_offset)
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)

        # Observations
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_log.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, '3D', observations)

        # Make modifications needed for testing
        # -------------------------------------
        conventional_types = ['aircraft']

        # Loop over the observations
        for index in range(len(observations)):

            # Remove GetValues if present
            if 'get values' in jedi_config_dict['observations'][index]:
                del jedi_config_dict['observations'][index]['get values']

            # GeoVaLs filename
            geo_va_ls_fname = os.path.join(self.cycle_dir(),
                                           f'{observations[index]}_geovals.{window_begin}.nc4')

            # Create GeoVaLs dictionary
            geo_va_ls_dict = {}
            geo_va_ls_dict['filename'] = geo_va_ls_fname

            # For conventional add the GeoVaLs flip
            if observations[index] in conventional_types:
                geo_va_ls_dict['levels_are_top_down'] = True

            jedi_config_dict['observations'][index]['geovals'] = geo_va_ls_dict

            # Need to insert at least one benchmark, but we do not really want to check anything
            # so check that some made up variable does not exist
            dummy_search = [{'name': 'Dummy/Group/Var'}]
            jedi_config_dict['observations'][index]['expectVariablesNotToExist'] = dummy_search

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Jedi executable name
        # --------------------
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            'test_ObsFilters.x')

        # Run the JEDI executable
        # -----------------------
        run_executable(self.logger, self.cycle_dir(), 1, jedi_executable_path, jedi_config_file,
                       output_log_file)
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')

# --------------------------------------------------------------------------------------------------
