# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import datetime
import glob
import h5py
import isodate
import numpy as np
import os
import re
import shutil

# Ioda converters
import gsi_ncdiag.gsi_ncdiag as gsid
from gsi_ncdiag.combine_obsspace import combine_obsspace

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess
from swell.utilities.datetime import datetime_formats

# --------------------------------------------------------------------------------------------------


class GsiNcdiagToIoda(taskBase):

    def execute(self):

        # Parse configuration
        # -------------------
        observations = self.config.observations()
        produce_geovals = self.config.produce_geovals()
        window_offset = self.config.window_offset()

        # Get window beginning time
        window_begin = self.da_window_params.window_begin(window_offset)

        # Keep copy of the
        observations_orig = observations.copy()

        # If pibal is in the observations then remove it and make sure sonde is there
        if 'pibal' in observations:
            if 'sondes' not in observations:
                observations.append('sondes')
            observations.remove('pibal')

        # Directory containing the ncdiags
        gsi_diag_dir = os.path.join(self.cycle_dir(), 'gsi_ncdiags')

        # Assemble all conventional types that ioda considers
        # ---------------------------------------------------
        gsi_to_ioda_dict = copy.copy(gsid.conv_platforms)

        # Remove aircraft from the lists and add new dictionaries for aircraft
        # --------------------------------------------------------------------
        aircraft_is_in_prof_files = True

        if aircraft_is_in_prof_files:
            for key, value in gsi_to_ioda_dict.items():
                gsi_to_ioda_dict[key] = [x for x in value if x not in ['aircraft']]

            if 'aircraft' in observations:
                gsi_to_ioda_dict['conv_prof_t'] = ['aircraft']
                gsi_to_ioda_dict['conv_prof_uv'] = ['aircraft']

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
        gsi_types_to_process = sorted(gsi_types_to_process)

        # Remove conv_platforms_to_process from the total observations list, leaving rad and ozn
        for needed_ioda_type in needed_ioda_types:
            observations.remove(needed_ioda_type)

        # Convert cycle time datetime object to string with format yyyymmdd_hhz
        gsi_datetime_str = datetime.datetime.strftime(self.cycle_time_dto(),
                                                      datetime_formats['gsi_nc_diag_format'])

        short_datetime_str = datetime.datetime.strftime(self.cycle_time_dto(),
                                                        datetime_formats['short_date'])

        # Clean up any files that are the end result of this program, in case of multiple runs
        # ------------------------------------------------------------------------------------
        for observation in observations_orig:

            obs_file = f'{observation}_obs.{window_begin}.nc4'
            geo_file = f'{observation}_geovals.{window_begin}.nc4'

            # If obs_file exists remove it
            if os.path.exists(os.path.join(self.cycle_dir(), obs_file)):
                os.remove(os.path.join(self.cycle_dir(), obs_file))

            # If geo exists remove it
            if produce_geovals:
                if os.path.exists(os.path.join(self.cycle_dir(), geo_file)):
                    os.remove(os.path.join(self.cycle_dir(), geo_file))

        # First process the conventional data (if needed)
        # -----------------------------------------------
        for gsi_type_to_process in gsi_types_to_process:

            log_str = f'Processing GSI file {gsi_type_to_process}'
            self.logger.info('', wrap=False)
            self.logger.info(log_str)
            self.logger.info('-'*len(log_str))

            # If prof in the name then it is aircraft data. Adjust path and rename
            if 'prof' in gsi_type_to_process:
                gsi_type_to_process_actual = gsi_type_to_process.replace('_prof', '')
                extra_path = 'aircraft'
            else:
                gsi_type_to_process_actual = gsi_type_to_process
                extra_path = ''

            # Path to search to GSI ncdiag files
            path_to_search = os.path.join(gsi_diag_dir, extra_path,
                                          f'*{gsi_type_to_process_actual}_*{gsi_datetime_str}*')

            # Get the list of files
            gsi_conv_file = glob.glob(path_to_search)

            # Check that some files where found
            self.logger.assert_abort(len(gsi_conv_file) != 0, 'The search for GSI ncdiags files ' +
                                     f'returned no files. Search path: \'{path_to_search}\'')

            # Check that only one file was found
            self.logger.assert_abort(len(gsi_conv_file) == 1, 'The search for GSI ncdiags files ' +
                                     f'returned more than one file. Files: \'{gsi_conv_file}\'')

            # Open the file
            Diag = gsid.Conv(gsi_conv_file[0])
            Diag.read()

            # Assemble list of needed platforms
            needed_platforms = []
            for platform in gsid.conv_platforms[gsi_type_to_process_actual]:
                if platform in needed_ioda_types:
                    needed_platforms.append(platform)

            # Extract data
            Diag.toIODAobs(self.cycle_dir(), platforms=needed_platforms)

            if produce_geovals:
                self.logger.info('', wrap=False)
                self.logger.info(f'Processing GeoVaLs from {gsi_type_to_process_actual}')
                Diag.toGeovals(self.cycle_dir())

            Diag.close()

        # Rename gps files from gps_bend if they exist
        if 'gps' in observations_orig:
            gps_files = glob.glob(os.path.join(self.cycle_dir(), 'gps_bend*'))
            for gps_file in gps_files:
                gps_file_newname = os.path.basename(gps_file).replace('gps_bend', 'gps')
                os.rename(gps_file, os.path.join(self.cycle_dir(), gps_file_newname))

        # Copy uv sonde files to pibal
        if 'pibal' in observations_orig:
            # Copy the uv obs file to pibal
            shutil.copy(os.path.join(self.cycle_dir(),
                                     f'sondes_uv_obs_{short_datetime_str}.nc4'),
                        os.path.join(self.cycle_dir(),
                                     f'pibal_obs_{short_datetime_str}.nc4'))

            # Copy the geovals file to pibal
            if produce_geovals:
                shutil.copy(os.path.join(self.cycle_dir(),
                                         f'sondes_uv_geoval_{short_datetime_str}.nc4'),
                            os.path.join(self.cycle_dir(),
                                         f'pibal_geoval_{short_datetime_str}.nc4'))

        # Combine the conventional data
        # -----------------------------
        for needed_ioda_type in needed_ioda_types:

            # Logging
            log_str = f'Combining IODA files for {needed_ioda_type}'
            self.logger.info('', wrap=False)
            self.logger.info(log_str)
            self.logger.info('-'*len(log_str))

            # Check the number of files that are found
            ioda_type_pattern = f'{needed_ioda_type}*_obs_*'  # Pattern, e.g.: *aircraft*_obs_*

            # List of files for that instrument
            ioda_path_files = glob.glob(os.path.join(self.cycle_dir(), ioda_type_pattern))

            # For sfc make sure there are no surface ship files
            if needed_ioda_type == 'sfc':
                ioda_path_files = [x for x in ioda_path_files if 'sfcship' not in x]

            # Show files that will be combined
            self.logger.info(f'Files to combine:')
            for ioda_path_file in ioda_path_files:
                self.logger.info(f' - {os.path.basename(ioda_path_file)}')

            # Check that there are some files to combine
            self.logger.assert_abort(len(ioda_path_files) > 0, f'In combine of ' +
                                     f'{needed_ioda_type} no files where found. Ensure that ' +
                                     f'the converter worked as expected.')

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
                new_name = os.path.join(self.cycle_dir(), '_'.join(new_name_split))

                # Check if new file already exists and remove if so
                if os.path.exists(new_name):
                    os.remove(new_name)
                    if new_name in ioda_path_files:
                        ioda_path_files.remove(new_name)

                # Run the combine step
                geo_dir = None
                if produce_geovals:
                    geo_dir = self.cycle_dir()

                    # Remove wind_reduction_factor_at_10m from non-uv geoval files
                    geoval_files = glob.glob(os.path.join(self.cycle_dir(),
                                                          f'{needed_ioda_type}_*_geoval_*.nc4'))
                    for geoval_file in geoval_files:
                        if f'{needed_ioda_type}_uv_geoval_' not in geoval_file:
                            var_remove_command = ['ncks', '-O', '-x', '-v',
                                                  'wind_reduction_factor_at_10m',
                                                  geoval_file, geoval_file]
                            run_track_log_subprocess(self.logger, var_remove_command)

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

        # Transform radiances and ozone
        # -----------------------------
        for observation in observations:

            self.logger.info(f'Converting {observation} to IODA format')

            observation_search_name = copy.copy(observation)

            # For avhrr replace the search with just avhrr
            if 'avhrr3' in observation_search_name:
                observation_search_name = observation_search_name.replace('avhrr3', 'avhrr')

            gsi_obs_file = glob.glob(os.path.join(gsi_diag_dir, f'*{observation_search_name}*'))

            # Skip this observation if not files were found
            if len(gsi_obs_file) == 0:
                self.logger.info(f'No observation files found for {observation}. Skipping convert')
                continue

            if observation not in ozone_observations:

                # Radiances
                Diag = gsid.Radiances(gsi_obs_file[0])
                Diag.read()
                Diag.toIODAobs(self.cycle_dir(), False, False, False)

            else:

                # Ozone
                Diag = gsid.Ozone(gsi_obs_file[0])
                Diag.read()
                Diag.toIODAobs(self.cycle_dir())

            # GeoVaLs call
            if produce_geovals:
                Diag.toGeovals(self.cycle_dir())

            if observation not in ozone_observations:
                Diag.close()

        # Rename avhrr files to avhrr3
        # ----------------------------
        gsi_datetime = re.sub('\D', '', self.cycle_time())[0:10]  # noqa
        if any('avhrr' in item for item in observations):
            avhrr_files = glob.glob(os.path.join(self.cycle_dir(),
                                                 f'avhrr_*_obs_{gsi_datetime}.nc4'))
            # Add geovals files
            avhrr_files = avhrr_files + glob.glob(os.path.join(self.cycle_dir(),
                                                  f'avhrr_*_geoval_{gsi_datetime}.nc4'))
            for avhrr_file in avhrr_files:
                avhrr_file_newname = os.path.basename(avhrr_file).replace('avhrr_', 'avhrr3_')
                os.rename(avhrr_file, os.path.join(self.cycle_dir(), avhrr_file_newname))

        # Rename files to be swell compliant
        # ----------------------------------
        for observation in observations_orig:

            self.logger.info(f'Renaming \'{observation}\' to be swell compliant')

            # Change to gps_bend
            search_name = observation

            # Input filename
            ioda_obs_in_pattern = f'{search_name}_obs_*nc*'

            ioda_obs_in_found = glob.glob(os.path.join(self.cycle_dir(), ioda_obs_in_pattern))

            # If nothing found then skipt this observation
            if len(ioda_obs_in_found) == 0:
                self.logger.info(f'No observation files found for {observation}. Skipping rename')
                continue

            ioda_obs_in = ioda_obs_in_found[0]

            ioda_obs_out = f'{search_name}.{window_begin}.nc4'

            os.rename(ioda_obs_in, os.path.join(self.cycle_dir(), ioda_obs_out))

            # Rename GeoVaLs file if need be
            if produce_geovals:
                ioda_geoval_in_pattern = f'{search_name}_geoval_*.nc*'
                ioda_geoval_in = glob.glob(os.path.join(self.cycle_dir(),
                                                        ioda_geoval_in_pattern))[0]

                ioda_geoval_out = f'{search_name}_geovals.{window_begin}.nc4'

                os.rename(ioda_geoval_in, os.path.join(self.cycle_dir(), ioda_geoval_out))

        # Bump the time in the satellite wind files by 1 second
        # (because JEDI does not include observations equal to
        # the beginning of the window where there are a lot of
        # satellite wind observations). IODA wrote the files in
        # such a way that h5py needs to be used not netcdf4
        # -----------------------------------------------------
        wind_begin = self.cycle_time_dto() - isodate.parse_duration(window_offset)
        ioda_begin = datetime.datetime(1970, 1, 1)
        seconds_to_window_begin = (wind_begin - ioda_begin).total_seconds()

        for observation in observations_orig:
            obs_file = os.path.join(self.cycle_dir(), f'{observation}.{window_begin}.nc4')
            self.logger.info(f'One second bump for obs at window beg for ({observation})')
            with h5py.File(obs_file, 'a') as fh:
                variable = fh['MetaData']['dateTime']
                window_begin_ind = np.where(variable[:] == seconds_to_window_begin)
                variable[window_begin_ind] += 1

        # Remove left over files
        # ------------------------------
        self.logger.info('Removing residual files...')

        patterns = [
            '*_geoval_*',
        ]

        for pattern in patterns:
            geoval_files = glob.glob(os.path.join(self.cycle_dir(), pattern))
            for geoval_file in geoval_files:
                self.logger.info(f' - Removing {os.path.basename(geoval_file)}')
                os.remove(geoval_file)

# --------------------------------------------------------------------------------------------------
