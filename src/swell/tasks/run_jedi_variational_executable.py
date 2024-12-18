# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from collections import OrderedDict
import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable


# --------------------------------------------------------------------------------------------------


class RunJediVariationalExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'variational'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        number_of_iterations = self.config.number_of_iterations()
        observations = self.config.observations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        npx_proc = self.config.npx_proc(None)
        npy_proc = self.config.npy_proc(None)

        # Compute data assimilation window parameters
        # --------------------------------------------
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_iso = self.da_window_params.window_begin_iso(window_offset)
        window_end_iso = self.da_window_params.window_end_iso(window_offset, window_length)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('minimizer', self.config.minimizer())
        self.jedi_rendering.add_key('number_of_iterations', number_of_iterations[0])
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())
        self.jedi_rendering.add_key('gradient_norm_reduction',
                                    self.config.gradient_norm_reduction())

        # Background
        # ----------
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        # --------
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        # ------------
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Atmosphere background error model
        # ---------------------------------
        if npx_proc is not None and npy_proc is not None:
            self.jedi_rendering.add_key('gsibec_configuration', self.config.gsibec_configuration())
            self.jedi_rendering.add_key('gsibec_npx_proc', npx_proc)
            self.jedi_rendering.add_key('gsibec_npy_proc', 6*npy_proc)

        # Model
        # -----
        if window_type == '4D':
            self.jedi_rendering.add_key('background_frequency', self.config.background_frequency())

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_log.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}{window_type}')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type, observations,
                                 self.cycle_time_dto(), jedi_forecast_model)

        def represent_ordereddict(dumper, data):
            # Serialize an OrderedDict as a YAML mapping
            return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

        def construct_ordereddict(loader, node):
            # Construct an OrderedDict from a YAML mapping
            return OrderedDict(loader.construct_pairs(node))

        # Recursive conversion, dictionary to an OrderedDict
        def dict_to_ordereddict(d):
            if isinstance(d, dict):
                return OrderedDict((k, dict_to_ordereddict(v)) for k, v in d.items())
            elif isinstance(d, list):
                return [dict_to_ordereddict(v) for v in d]
            else:
                return d

        yaml.add_representer(OrderedDict, represent_ordereddict)
        yaml.add_constructor('tag:yaml.org,2002:map', construct_ordereddict)

        # Assuming jedi_config_dict is your original dictionary
        ordered_dict = dict_to_ordereddict(jedi_config_dict)

        # Write the ordered dictionary to YAML file
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(ordered_dict, jedi_config_file_open, default_flow_style=False)

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Compute number of processors
        # ----------------------------
        np = eval(str(model_component_meta['total_processors']))

        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables'][f'{jedi_application}{window_type}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)

        # Run the JEDI executable
        # -----------------------
        if not generate_yaml_and_exit:
            self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')
            run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                           jedi_config_file, output_log_file)
        else:
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
