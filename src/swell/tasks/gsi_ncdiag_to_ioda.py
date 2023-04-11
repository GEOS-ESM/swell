# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import shutil
import netCDF4 as nc

# Ioda converters
import gsi_ncdiag.gsi_ncdiag as gsid
from gsi_ncdiag.combine_obsspace import combine_obsspace

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess

# --------------------------------------------------------------------------------------------------


class GsiNcdiagToIoda(taskBase):

    def execute(self):

        # Parse configuration
        # -------------------
        experiment_root = self.config_get('experiment_root')
        experiment_id = self.config_get('experiment_id')
        cycle_dir = self.config_get('cycle_dir')
        observations = self.config_get('observations')
        produce_geovals = self.config_get('produce_geovals')
        window_begin = self.config_get('window_begin')

        # Keep copy of the
        observations_orig = observations.copy()

        # Directory containing the ncdiags
        gsi_diag_dir = os.path.join(cycle_dir, 'gsi_ncdiags')

        # Assemble all conventional types that ioda considers
        # ---------------------------------------------------
        gsi_to_ioda_dict = gsid.conv_platforms
        ioda_types = []
        for key in gsi_to_ioda_dict:
            ioda_types += gsi_to_ioda_dict[key]

        # Remove duplicates
        ioda_types = list(set(ioda_types))

        # Invert the dictionary so for each ioda type we know the gsi files that provide data
        ioda_to_gsi_dict = {}
        for ioda_type in ioda_types:
            ioda_to_gsi_dict[ioda_type] = []
            for key in gsi_to_ioda_dict:
                if ioda_type in gsi_to_ioda_dict[key]:
                    ioda_to_gsi_dict[ioda_type].append(key)

        # Get all the elements that are in both observations and ioda_types
        needed_ioda_types = [elem for elem in observations if elem in ioda_types]

        # Determine which gsi files need to be processed
        gsi_types_to_process = []
        for needed_ioda_type in needed_ioda_types:
            gsi_types_to_process += ioda_to_gsi_dict[needed_ioda_type]
        gsi_types_to_process = list(set(gsi_types_to_process))  # Unique values only

        # Remove conv_platforms_to_process from the total observations list, leaving rad and ozn
        for needed_ioda_type in needed_ioda_types:
            observations.remove(needed_ioda_type)

        # First process the conventional data (if needed)
        # -----------------------------------------------
        for gsi_type_to_process in gsi_types_to_process:

            log_str = f'Processing GSI file {gsi_type_to_process}'
            self.logger.info('', wrap=False)
            self.logger.info(log_str)
            self.logger.info('-'*len(log_str))

            gsi_conv_file = glob.glob(os.path.join(gsi_diag_dir, f'*{gsi_type_to_process}*'))[0]

            # Open the file
            Diag = gsid.Conv(gsi_conv_file)
            Diag.read()

            # Assemble list of needed platforms
            needed_platforms = []
            for platform in gsid.conv_platforms[gsi_type_to_process]:
                if platform in needed_ioda_types:
                    needed_platforms.append(platform)

            # Extract data
            Diag.toIODAobs(cycle_dir, platforms=needed_platforms)

            if produce_geovals:
                self.logger.info('', wrap=False)
                self.logger.info(f'Processing GeoVaLs from {gsi_type_to_process}')
                Diag.toGeovals(cycle_dir)

            Diag.close()

        # Combine the conventional data
        # -----------------------------
        for needed_ioda_type in needed_ioda_types:

            # Logging
            log_str = f'Combining IODA files for {needed_ioda_type}'
            self.logger.info('', wrap=False)
            self.logger.info(log_str)
            self.logger.info('-'*len(log_str))

            # Check dictionary for number of gsi files that were needed
            gsi_sources = ioda_to_gsi_dict[needed_ioda_type]

            # Check the number of files that are found
            ioda_type_pattern = f'*{needed_ioda_type}*_obs_*'  # Pattern, e.g.: *aircraft*_obs_*

            # List of files for that instrument
            ioda_path_files = glob.glob(os.path.join(cycle_dir, ioda_type_pattern))

            # Get last file (first could be type_obs_ if the code already ran)
            ioda_file_0 = os.path.basename(ioda_path_files[-1])

            # Split by underscore
            ioda_file_0_ = ioda_file_0.split('_')

            # Logic fails for gps so skip
            if needed_ioda_type == 'gps':
                ioda_file_0_ = ['gps', 'is', 'skipped']

            # Only combine if the split name has 4 elements
            if len(ioda_file_0_) == 4:

                # If we are here there should be more than one file associated with the ioda type.
                # i.e. files with *_uv_*, *_tsen_* for aircraft.
                if len(ioda_path_files) == 1:
                    self.logger.abort(f'Combine issue for {needed_ioda_type}, not multiple files.')

                # Create new file name
                new_name_split = ioda_file_0_
                del new_name_split[1]
                new_name = os.path.join(cycle_dir, '_'.join(new_name_split))

                # Check if new file already exists and remove if so
                if os.path.exists(new_name):
                    os.remove(new_name)
                    if new_name in ioda_path_files:
                        ioda_path_files.remove(new_name)

                # Run the combine step
                geo_dir = None
                if produce_geovals:
                    geo_dir = cycle_dir
                combine_obsspace(ioda_path_files, new_name, geo_dir)

                # Remove input files
                for ioda_path_file in ioda_path_files:
                    os.remove(ioda_path_file)

            elif len(ioda_file_0_) == 3:
                self.logger.info(f'Skipping combine for {needed_ioda_type}, single file already.')
            else:
                self.logger.abort(f'Combine failed for {needed_ioda_type}, file name issue.')


        # Get list of the observations that are ozone observations
        # --------------------------------------------------------
        ozone_sensors = gsid.oz_lay_sensors + gsid.oz_lev_sensors
        ozone_observations = []
        for observation in observations:
            for ozone_sensor in ozone_sensors:
                if ozone_sensor in observation:
                    ozone_observations.append(observation)

        # Copy all the files into the cycle directory
        # -------------------------------------------
        for observation in observations:

            self.logger.info(f'Converting {observation} to IODA format')

            gsi_obs_file = glob.glob(os.path.join(gsi_diag_dir, f'*{observation}*'))

            if observation not in ozone_observations:

                # Radiances
                Diag = gsid.Radiances(gsi_obs_file[0])
                Diag.read()
                Diag.toIODAobs(cycle_dir, False, False, False)

            else:

                # Ozone
                Diag = gsid.Ozone(gsi_obs_file[0])
                Diag.read()
                Diag.toIODAobs(cycle_dir)

            # GeoVaLs call
            if produce_geovals:
                Diag.toGeovals(cycle_dir)

            if observation not in ozone_observations:
                Diag.close()

        # Rename files to be swell compliant
        # ----------------------------------
        for observation in observations_orig:

            # Input filename
            ioda_file_in_pattern = f'{observation}_obs_*nc*'
            ioda_file_in = glob.glob(os.path.join(cycle_dir, ioda_file_in_pattern))[0]

            ioda_file_out = f'{observation}.{window_begin}.nc4'

            os.rename(ioda_file_in, os.path.join(cycle_dir, ioda_file_out))

# --------------------------------------------------------------------------------------------------
