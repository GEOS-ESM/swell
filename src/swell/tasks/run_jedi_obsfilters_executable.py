# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.swell_path import get_swell_path
from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable

# --------------------------------------------------------------------------------------------------

class RunJediObsfiltersExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'thinobs'

        # Parse configuration
        # -------------------
        print(f'bf win type')
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        # Compute data assimilation window parameters
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_iso = self.da_window_params.window_begin_iso(window_offset)
        window_end_iso = self.da_window_params.window_end_iso(window_offset, window_length)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)

        # Observations
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
        jedi_config_dict = self.jedi_rendering.render_oops_file('qc_thinning')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type, observations)

#        # Assemble localizations
#        # ----------------------
#
#        # Include ensemble localizations and halo types with each observation
#        # -------------------------------------------------------------------
#        swell_path = get_swell_path()
#        localization_path = os.path.join(swell_path,
#                                         f'configuration/jedi/interfaces/geos_atmosphere'
#                                         f'/observations/localization')
#        if self.config.local_ensemble_use_linear_observer():
#            for index, observation in enumerate(observations):
#                # Get pointer to observer (ref to list)
#                observer = jedi_config_dict['observations']['observers'][index]
#                print('ob=', observation)
#                config_file = os.path.join(localization_path, f'{observation}.yaml')
#                with open(config_file, 'r') as f:
#                    loc_list = yaml.safe_load(f)
#                    horizLoc = loc_list['obs localizations']
#                localization = [horizLoc]
#                observer.update({'obs localizations': localization})
#                observer['obs space'].update(
#                    {'distribution': {'name': 'Halo', 'halo size': 5000.e3}})
                
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

        jedi_executable = model_component_meta['executables'][f'{jedi_application}']
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
