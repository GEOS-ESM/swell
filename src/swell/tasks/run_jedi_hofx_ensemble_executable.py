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

from swell.tasks.run_jedi_hofx_executable import RunJediHofxExecutable

# --------------------------------------------------------------------------------------------------

# Watch out for MRO!!!
class RunJediHofxEnsembleExecutable(RunJediHofxExecutable, taskBase):
# class RunJediHofxEnsembleExecutable(taskBase, RunJediHofxExecutable):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Jedi application name
        # ---------------------
        jedi_application = 'ensemblehofx'

        # Parse configuration ... for window_type
        # ---------------------------------------
        window_type = self.config.window_type()

        # Ensemble hofx components
        # -------------------
        ensemble_hofx_packets = self.config.ensemble_hofx_packets()
        ensemble_hofx_strategy = self.config.ensemble_hofx_strategy()
        ensemble_num_members = self.config.ensemble_num_members()

        if ensemble_num_members%ensemble_hofx_packets != 0:
            raise ValueError("Number of ensemble packets must evenly divide number of ensemble members!")

        self.logger.info('Running ensemble hofx strategy %s in %i packets'%
                         (ensemble_hofx_strategy, ensemble_hofx_packets))
        self.logger.info('Calling RunJediHofxExecutable execute!')

        # Call execute of RunJediHofxExecutable
        super().execute(ensemble=True)

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
                                 jedi_forecast_model)

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

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
#            run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
 #                          jedi_config_file, output_log_file)
        else:
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
