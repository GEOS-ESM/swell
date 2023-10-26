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

    def execute(self):

        # Jedi application name
        # ---------------------
        jedi_application = 'convert_state_soca2cice'

        # Parse configuration
        # -------------------
        cice6_domains = self.config.cice6_domains()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        observations = self.config.observations(None)
        window_type = self.config.window_type()
        window_offset = self.config.window_offset()

        # Compute data assimilation window parameters
        # --------------------------------------------
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())

        # Background
        # ----------
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

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

            # Compute number of processors
            # TODO: For now this task can only run serial (SOCA limitation)
            # so for now using 1 processor only
            # ----------------------------------------------------------------
            np = 1

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
