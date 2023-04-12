# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.run_jedi_executable_base import RunJediExecutableBase


# --------------------------------------------------------------------------------------------------


class RunJediTestObsFiltersExecutable(RunJediExecutableBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Path to executable being run
        # ----------------------------
        cycle_dir = self.config_get('cycle_dir')
        experiment_dir = self.config_get('experiment_dir')
        observations = self.config_get('observations')
        window_begin = self.config_get('window_begin')

        # Make cycle dir
        # --------------
        os.makedirs(cycle_dir, 0o755, exist_ok=True)

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(cycle_dir, 'jedi_test_obs_filters.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(cycle_dir, 'jedi_test_obs_filters.log')

        # Generate the JEDI configuration file for running the executable
        # ---------------------------------------------------------------
        jedi_config_dict = self.generate_jedi_config('TestObsFilters')

        # Make modifications needed for testing
        # -------------------------------------

        conventional_types = ['aircraft']

        # Loop over the observations
        for index in range(len(observations)):

            # Remove GetValues if present
            if 'get values' in jedi_config_dict['observations'][index]:
                del jedi_config_dict['observations'][index]['get values']

            # Create GeoVaLs dictionary
            geovals = {}
            geovals['filename'] = os.path.join(cycle_dir,
                                               f'{observations[index]}_geovals.{window_begin}.nc4')
            # For conventional add the GeoVaLs flip
            if observations[index] in conventional_types:
                geovals['levels_are_top_down'] = True

            jedi_config_dict['observations'][index]['geovals'] = geovals

            # Need to insert at least one benchmark, but we do not really want to check anything
            # so check that some made up variable does not exist
            jedi_config_dict['observations'][index]['expectVariablesNotToExist'] = \
                                                                        [{'name': 'Fake/Group/Var'}]

        # Write executable configuration to file
        # --------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Jedi executable name
        # --------------------
        jedi_executable_path = os.path.join(experiment_dir, 'jedi_bundle', 'build', 'bin',
                                            'test_ObsFilters.x')

        # Run the JEDI executable
        # -----------------------
        self.run_executable(cycle_dir, 1, jedi_executable_path, jedi_config_file, output_log_file)

# --------------------------------------------------------------------------------------------------
