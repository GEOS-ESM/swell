# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator

from swell.utilities.run_jedi_executables import run_executable
from swell.tasks.run_jedi_hofx_executable import RunJediHofxExecutable

# --------------------------------------------------------------------------------------------------


class RunJediHofxEnsembleExecutable(RunJediHofxExecutable, taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'ensemblehofx'

        # The packet and selected members of ensemble
        # -------------------------------------------
        this_packet = self.get_ensemble_packet()
        packet_ensemble_members = None

        # Parse configuration ... despite same block in RunJediHofxExecutable
        # -------------------------------------------------------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

        # Compute data assimilation window parameters
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_iso = self.da_window_params.window_begin_iso(window_offset)
        window_end_iso = self.da_window_params.window_end_iso(window_offset, window_length)

        # Ensemble hofx components
        # ------------------------
        ensemble_hofx_packets = self.config.ensemble_hofx_packets()
        ensemble_hofx_strategy = self.config.ensemble_hofx_strategy()
        ensemble_num_members = self.config.ensemble_num_members()

        # Force packets of equal size (i.e., members handled)
        # ---------------------------------------------------
        if ensemble_num_members % ensemble_hofx_packets != 0:
            raise ValueError('Number of ensemble packets must evenly ' +
                             'divide number of ensemble members!')

        # Report strategy and packet (if defined)
        # ---------------------------------------
        if this_packet is None:
            self.logger.info('  Running ensemble hofx via %s strategy' %
                             ensemble_hofx_strategy.upper())
        else:
            # Determine ensemble members
            _q = int(ensemble_num_members/ensemble_hofx_packets)
            packet_ensemble_members = [int(this_packet)*_q+i for i in range(_q)]
            self.logger.info('  Running ensemble hofx via %s strategy' %
                             ensemble_hofx_strategy.upper())
            self.logger.info('     - this packet     = %s' % this_packet)
            self.logger.info(f'     - selects members = {packet_ensemble_members}')

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)

        # Background
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc(None))
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc(None))
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Model
        if window_type == '4D':
            self.jedi_rendering.add_key('background_frequency', self.config.background_frequency())

        # Populate remaining entries of jedi interface templates dictionary
        # -----------------------------------------------------------------
        self.jedi_rendering.add_key('ensemble_hofx_packets', ensemble_hofx_packets)
        self.jedi_rendering.add_key('packet_ensemble_members', packet_ensemble_members)

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(),
                                        f'jedi_{jedi_application}_pack{this_packet}_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(),
                                       f'jedi_{jedi_application}_pack{this_packet}_log.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        print('enhx: {jedi_application} {window_type}', jedi_application, window_type)

        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}{window_type}')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type, observations,
                                 self.cycle_time_dto(), jedi_forecast_model)

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Call execute of RunJediHofxExecutable to render hofx templates for each member 
        # -----------------------------------------------------------------------------
        print('ensemble_num_members, ensemble_hofx_packets', ensemble_num_members, ensemble_hofx_packets)
        print('packet_ensemble_members', packet_ensemble_members)

        super().execute(ensemble_members=packet_ensemble_members)

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Compute number of processors while considering packet ensemble members
        # -----------------------------------------------------------------------
        np = _q * eval(str(model_component_meta['total_processors']))

        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables'][f'{jedi_application}{window_type}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)
        print('enhx: {jedi_executable}', jedi_executable)

        # Run the JEDI executable
        # -----------------------
        if not generate_yaml_and_exit:
            self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')
            run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                           jedi_config_file, output_log_file)

        # TODO: save_geovals combination, if ever needed
        else:
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
