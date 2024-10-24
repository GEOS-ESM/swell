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


class RunJediConvertStateSoca2ciceExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Number of processors for JEDI executable
        # ----------------------------------------
        N_PROCESSORS = 36

        # Jedi application name
        # ---------------------
        jedi_application = 'convert_state_soca2cice'

        # Parse configuration
        # -------------------
        marine_models = self.config.marine_models()
        self.jedi_rendering.add_key('marine_models', marine_models)

        # Fail-safe
        # ---------
        if 'cice6' not in marine_models:
            self.logger.info('Skipping Soca2cice as CICE6 analysis is not enabled.')
            return

        # cice6_domains = self.config.cice6_domains()
        cice6_domains = ['arctic', 'antarctic']
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        observations = self.config.observations(None)
        window_type = self.config.window_type()
        window_offset = self.config.window_offset()

        # Compute data assimilation window parameters
        # --------------------------------------------
        analysis_time = self.da_window_params.analysis_time(window_type, self.suite_name())
        analysis_time_iso = self.da_window_params.analysis_time_iso(window_type, self.suite_name())
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())

        # Background and analysis times
        # -----------------------------
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('analysis_time', analysis_time)
        self.jedi_rendering.add_key('analysis_time_iso', analysis_time_iso)

        # Geometry
        # --------
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Loop over active CICE6 DA domains
        # ---------------------------------
        for cice6_domain in cice6_domains:

            # Add CICE6 domain to templates dictionary
            # ----------------------------------------
            self.jedi_rendering.add_key('cice6_domain', cice6_domain)

            # Jedi configuration file
            # -----------------------
            jedi_config_file = os.path.join(self.cycle_dir(),
                                            f'jedi_{jedi_application}_{cice6_domain}_config.yaml')

            # Output log file
            # ---------------
            output_log_file = os.path.join(self.cycle_dir(),
                                           f'jedi_{jedi_application}_{cice6_domain}_log.log')

            # Open the JEDI config file and fill initial templates
            # ----------------------------------------------------
            jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}')

            # Perform complete template rendering
            # -----------------------------------
            jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type,
                                     observations, jedi_forecast_model)

            # Write the expanded dictionary to YAML file
            # ------------------------------------------
            with open(jedi_config_file, 'w') as jedi_config_file_open:
                yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

            # Get the JEDI interface metadata
            # -------------------------------
            model_component_meta = self.jedi_rendering.render_interface_meta()

            # Compute number of processors (only requires a single node and fails
            # for multiple nodes, so we set it to 36 processors for now)
            # ----------------------------------------------------------
            np = N_PROCESSORS

            # Jedi executable name
            # --------------------
            jedi_executable = model_component_meta['executables'][f'{jedi_application}']
            jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                                'build', 'bin', jedi_executable)

            # Run the JEDI executable
            # -----------------------
            if not generate_yaml_and_exit:
                self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')
                run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                               jedi_config_file, output_log_file)
            else:
                self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
