# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import yaml
from typing import Optional

from swell.tasks.base.task_base import taskBase
from swell.utilities.netcdf_files import combine_files_without_groups
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable


# --------------------------------------------------------------------------------------------------


class RunJediHofxExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, ensemble_members: Optional[list] = None) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'hofx'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        save_geovals = self.config.save_geovals(False)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

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
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)

        # Background
        # ----------
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        # --------
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc(None))
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc(None))
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        # ------------
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Model
        # -----
        if window_type == '4D':
            self.jedi_rendering.add_key('background_frequency', self.config.background_frequency())

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Compute number of processors
        # ----------------------------
        np = eval(str(model_component_meta['total_processors']))

        # Run the JEDI executable - or render hofx templates for each ensemble member
        # ---------------------------------------------------------------------------
        if ensemble_members is None:

            # Jedi configuration file
            # -----------------------
            jedi_config_file = os.path.join(self.cycle_dir(),
                                            f'jedi_{jedi_application}_config.yaml')

            # Output log file
            # ---------------
            output_log_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_log.log')

            # Open the JEDI config file and fill initial templates
            # ----------------------------------------------------
            jedi_config_dict = \
                self.jedi_rendering.render_oops_file(f'{jedi_application}{window_type}')

            # Perform complete template rendering
            # -----------------------------------
            jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type,
                                     observations, self.cycle_time_dto(), jedi_forecast_model)

            # If window type is 4D add time interpolation to each observer
            # ------------------------------------------------------------
            if window_type == '4D':
                for observer in jedi_config_dict['observations']['observers']:
                    observer['get values'] = {
                        'time interpolation': 'linear'
                    }

            # Update config filters to save the GeoVaLs from the model interface.
            # Add GOMsaver to either obs filters OR obs prior filters, if neither
            # exists then create obs prior filters and add GOMsaver
            # ------------------------------------------------------------------
            if save_geovals:
                self.append_gomsaver(observations, jedi_config_dict, window_begin)

            # Write the expanded dictionary to YAML file
            # ------------------------------------------
            with open(jedi_config_file, 'w') as jedi_config_file_open:
                yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

            # Jedi executable name
            # --------------------
            jedi_executable = \
                model_component_meta['executables'][f'{jedi_application}{window_type}']
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

            # If saving the geovals they need to be combined
            # ----------------------------------------------
            if save_geovals:

                # Combine the GeoVaLs
                # -------------------
                for observation in observations:

                    self.logger.info(f'Combining GeoVaLs files for {observation}')

                    # List of GeoVaLs input files
                    input_files = f'{observation}-geovals.{window_begin}_*.nc4'
                    output_file = \
                        f'{self.experiment_id()}.{observation}-geovals.{window_begin}.nc4'
                    output_file = os.path.join(self.cycle_dir(), output_file)

                    # Build list of input files
                    geovals_files = sorted(glob.glob(os.path.join(self.cycle_dir(), input_files)))

                    # Assert that there are np files
                    self.logger.assert_abort(len(geovals_files) == np, f'Number of GeoVaLs' +
                                             f' for observtion type {observation}:\n' +
                                             f' does not match number of processors:\n' +
                                             f' np={np}, len(geovals_files) = {len(geovals_files)}')

                    # Write the concatenated dataset to a new file
                    combine_files_without_groups(self.logger, geovals_files, output_file, 'nlocs',
                                                 True)

        else:
            for mem in ensemble_members:
                # Jedi configuration file
                # -----------------------
                jedi_config_file = os.path.join(self.cycle_dir(),
                                                f'jedi_{jedi_application}_mem{mem}_config.yaml')

                # Output log file
                # ---------------
                output_log_file = os.path.join(self.cycle_dir(),
                                               f'jedi_{jedi_application}_mem{mem}_log.log')

                # Open the JEDI config file and fill initial templates
                # ----------------------------------------------------
                jedi_config_dict = \
                    self.jedi_rendering.render_oops_file(f'{jedi_application}{window_type}')

                # Perform complete template rendering
                # -----------------------------------
                jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type,
                                         observations, self.cycle_time_dto(), jedi_forecast_model)

                # Continue with the yaml edits below some of which need to be
                # done for each observation and ensemble member

                # If window type is 4D add time interpolation to each observer
                # ------------------------------------------------------------
                if window_type == '4D':
                    for observer in jedi_config_dict['observations']['observers']:
                        observer['get values'] = {
                            'time interpolation': 'linear'
                        }

                # For each observation, add the ensemble member to the output
                # filename to create seperate files for each ensemble member
                # ------------------------------------------------------------
                for index, observation in enumerate(observations):

                    # Get pointer to observer
                    observer = jedi_config_dict['observations']['observers'][index]

                    # Get the output file string
                    outfile = observer['obs space']['obsdataout']['engine']['obsfile']

                    # Replace '.nc4' with '_mem.nc4' and update the 'obsfile' string in the observer
                    observer['obs space']['obsdataout']['engine']['obsfile'] = \
                        outfile.replace('.nc4', f'_{mem:02}.nc4')

                # Update config filters to save the GeoVaLs from the model interface.
                # Add GOMsaver to either obs filters OR obs prior filters, if neither
                # exists then create obs prior filters and add GOMsaver
                # ------------------------------------------------------------------
                if save_geovals:
                    self.append_gomsaver(observations, jedi_config_dict, window_begin, mem=mem)

                # Write the expanded dictionary to YAML file
                # ------------------------------------------
                with open(jedi_config_file, 'w') as jedi_config_file_open:
                    yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

    # ----------------------------------------------------------------------------------------------

    def append_gomsaver(
        self,
        observations: list,
        jedi_config_dict: dict,
        window_begin: str,
        mem: Optional[str] = None
    ) -> None:

        # We may need to save the GeoVaLs for ensemble members. This will
        # prevent code repetition.
        # ----------------------------------------------------------------------

        # Add mem to the filename if it is not None
        mem_str = f'_mem{mem}' if mem is not None else ''

        for index, observation in enumerate(observations):

            # Define the GeoVaLs saver dictionary
            gom_saver_dict = {
                'filter': 'GOMsaver',
                'filename': os.path.join(self.cycle_dir(),
                                         f'{observation}-geovals.{window_begin}{mem_str}.nc4')
            }

            # Get pointer to observer
            observer = jedi_config_dict['observations']['observers'][index]

            # Check if observer has obs filters and if so add them to the jedi_config_dict
            if 'obs filters' in observer:
                filter_dict = 'obs filters'
            elif 'obs prior filters' in observer:
                filter_dict = 'obs prior filters'
            else:
                # Create some prior filters
                observer['obs prior filters'] = []
                filter_dict = 'obs prior filters'

            # Append the GOMsaver dictionary to the observer filters
            observer[filter_dict].append(gom_saver_dict)
# --------------------------------------------------------------------------------------------------
