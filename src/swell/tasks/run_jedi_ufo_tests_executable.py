# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.dictionary import update_dict
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable


# --------------------------------------------------------------------------------------------------


class RunJediUfoTestsExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Jedi application name
        # ---------------------
        jedi_application = 'ufo_tests'

        # Parse configuration
        # -------------------
        window_offset = self.config.window_offset()
        window_length = self.config.window_length()
        bkg_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        single_observations = self.config.single_observations()
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        observing_system_records_path = self.config.observing_system_records_path()
        cycle_dir = self.cycle_dir()
        if observing_system_records_path == 'None':
            observing_system_records_path = os.path.join(cycle_dir, 'observing_system_records')
        cycle_time = os.path.normpath(cycle_dir).split('/')[-2]

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

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, '3D', observations,
                                 observing_system_records_path, cycle_time)

        # Make modifications needed for testing
        # -------------------------------------
        conventional_types = [
            'aircraft',
            'pibal',
            'satwind',
            'scatwind',
            'sfcship',
            'sfc',
            'sondes'
        ]

        # Open the ufo_tests config file
        # ------------------------------
        ufo_tests_dict = self.jedi_rendering.render_interface_ufo_test()
        ufo_tests_default = ufo_tests_dict['default']

        # Insert the GeoVaLs section
        # --------------------------

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
                geo_va_ls_dict['levels_are_top_down'] = False

            jedi_config_dict['observations'][index]['geovals'] = geo_va_ls_dict

        # Copies for each kind of test
        # ----------------------------
        # jedi_operator_dict = copy.deepcopy(jedi_config_dict)
        jedi_filter_dict = copy.deepcopy(jedi_config_dict)

        # Loop through observations and moderate based on test needs
        # ----------------------------------------------------------
        for index in range(len(observations)):
            if not single_observations:
                # Overwrite the defaults with the values in ufo_tests_obs
                ufo_tests_obs = ufo_tests_dict[observations[index]]
                ufo_tests_obs = update_dict(ufo_tests_default, ufo_tests_obs)
            else:
                # Not to do any benchmark validation
                ufo_tests_obs = {'filter_test': {"expectVariablesNotToExist":
                                 [{"name": "Some/DummyVariable"}]}}

            # Merge the ufo_tests_obs dictionary with the observation dictionary
            # jedi_operator_dict['observations'][index].update(ufo_tests_obs['operator_test'])
            jedi_filter_dict['observations'][index].update(ufo_tests_obs['filter_test'])

            # # Remove filters from operator test
            # if 'obs filters' in jedi_operator_dict['observations'][index]:
            #     del jedi_operator_dict['observations'][index]['obs filters']

        # Write configuration files for the tests
        # ---------------------------------------
        # file = os.path.join(self.cycle_dir(), 'jedi_test_ObsOperator_config.yaml')
        # with open(file, 'w') as jedi_config_file_open:
        #     yaml.dump(jedi_operator_dict, jedi_config_file_open, default_flow_style=False)

        # file = os.path.join(self.cycle_dir(), 'jedi_test_ObsOperatorTLAD_config.yaml')
        # with open(file, 'w') as jedi_config_file_open:
        #     yaml.dump(jedi_operator_dict, jedi_config_file_open, default_flow_style=False)

        file = os.path.join(self.cycle_dir(), 'jedi_test_ObsFilters_config.yaml')
        with open(file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_filter_dict, jedi_config_file_open, default_flow_style=False)

        # Tests to run
        # ------------
        # tests = ['test_ObsOperator', 'test_ObsOperatorTLAD', 'test_ObsFilters']
        tests = ['test_ObsFilters']

        # Loop over the tests
        # -------------------
        for test in tests:

            # Output log file
            # ---------------
            jedi_config_file = os.path.join(self.cycle_dir(), f'jedi_{test}_config.yaml')
            output_log_file = os.path.join(self.cycle_dir(), f'jedi_{test}_log.log')

            # Jedi executable name
            # --------------------
            jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build',
                                                'bin', f'{test}.x')

            # Run the Test Obs Filters executable
            # -----------------------------------
            if not generate_yaml_and_exit:
                run_executable(self.logger, self.cycle_dir(), 36, jedi_executable_path,
                               jedi_config_file, output_log_file)
            else:
                self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
