# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import subprocess

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import previous_bias_file


# --------------------------------------------------------------------------------------------------


class GetObsNotInR2d2(taskBase):

    def execute(self) -> None:

        # Get the cycle string
        # --------------------
        cycle_date = self.__datetime__.string_directory()

        # Get the path and pattern for the observation files
        # -------------------------------------------------
        existing_path = self.config.ioda_locations_not_in_r2d2()

        # Point to the model directory
        # ----------------------------
        existing_path = os.path.join(existing_path, cycle_date, self.__model__)

        # Create the list containing the files to process
        # -----------------------------------------------
        existing_path_files = []

        # Set the file patterns to search for
        # -----------------------------------
        file_patterns = ['*nc4', '*txt', '*acftbias', '*acftbias_cov']

        for file_pattern in file_patterns:

            # Get the full paths of all files
            # -------------------------------
            existing_path_files.extend(glob.glob(os.path.join(existing_path, file_pattern)))

        # Assert that some files were found
        # ---------------------------------
        self.logger.assert_abort(len(existing_path_files) > 0, f'No observation '
                                 'files matching cycle in observation directory.')

        # Loop over all the files
        # -----------------------
        for existing_path_file in existing_path_files:

            # Get filename from full path
            # ---------------------------
            existing_file = os.path.basename(existing_path_file)

            # Set the target file
            # -------------------
            existing_path_file_target = os.path.join(self.cycle_dir(), existing_file)

            # Remove the file if it exists
            # ----------------------------
            if os.path.exists(existing_path_file_target):
                os.remove(existing_path_file_target)

            # Build the copy command
            # ----------------------
            command = ['ln', '-s', existing_path_file, existing_path_file_target]

            self.logger.info(f'Linking {existing_path_file} '
                             f'to {existing_path_file_target}')

            # Copy the file
            # -------------
            subprocess.run(command)

        # Handling for cycling_varbc experiments, handle linking previous cycle bias files
        # --------------------------------------------------------------------------------
        if self.config.cycling_varbc(False):

            # Get information needed to fill out obs yamls
            # --------------------------------------------
            window_length = self.config.window_length()
            window_begin = self.da_window_params.window_begin(window_length)
            crtm_coeff_dir = self.config.crtm_coeff_dir()

            background_time_offset = self.config.background_time_offset()
            background_time = self.da_window_params.background_time(background_time_offset)

            self.jedi_rendering.add_key('background_time', background_time)
            self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
            self.jedi_rendering.add_key('window_begin', window_begin)

            self.jedi_rendering.set_obs_records_path(
                    self.config.observing_system_records_path(None))

            # Iterate through each observation
            # --------------------------------
            for observation in self.config.observations():
                observation_dict = \
                        self.jedi_rendering.render_interface_observations(observation)

                # Skip if bias not needed
                # -----------------------
                if 'obs bias' not in observation_dict:
                    continue

                # Satellite and aircraft bias correction (coeff and cov) files
                # -----------------------------------------------
                target_bccoef = observation_dict['obs bias']['input file']
                target_bccovr = observation_dict['obs bias']['covariance']['prior']['input file']

                if self.cycle_time_dto() == self.start_cycle_point_dto():
                    self.logger.info(f'Process bias file {target_bccoef} for the first cycle')
                    self.logger.info(f'Process bias file {target_bccovr} for the first cycle')
                else:
                    self.logger.info(f'Using bias files from the previous cycle')
                    previous_bias_coef = previous_bias_file(self.cycle_time_dto(), target_bccoef,
                                                            window_length, background_time_offset)
                    previous_bias_covr = previous_bias_file(self.cycle_time_dto(), target_bccovr,
                                                            window_length, background_time_offset)
                    # Link the previous bias file to the current cycle directory
                    self.logger.info(f'Linking {previous_bias_coef} to {target_bccoef}')
                    self.geos.linker(previous_bias_coef, target_bccoef, dst_dir=self.cycle_dir())
                    self.logger.info(f'Linking {previous_bias_covr} to {target_bccovr}')
                    self.geos.linker(previous_bias_covr, target_bccovr, dst_dir=self.cycle_dir())

# --------------------------------------------------------------------------------------------------
