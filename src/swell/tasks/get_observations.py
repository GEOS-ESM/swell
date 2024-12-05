# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import isodate
import numpy as np
import os
import netCDF4 as nc
from typing import Union

from datetime import timedelta, datetime as dt
from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
from swell.utilities.datetime_util import datetime_formats
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class GetObservations(taskBase):

    def execute(self) -> None:

        """
        Acquires observation files for a given experiment and cycle.

        To have additional flexibility in terms of R2D2 files, this task combines
        observation files that are organized under sub-windows. Currently, this
        combination can only handle Location and Channel dimensions.

        First, it finds the observation files that encompass the desired
        time window. For example, if the file time window is 6 hours and the middle
        of the DA window is 9Z, it needs to find the first observation file
        that starts at or before 6Z and the last observation file that ends at or
        after 12Z.

        For simplicity, we expect R2D2 obs files to have PT6H windows and
        that they were organized by start dates: 21Z, 03Z, 09Z, and 15Z (which
        may likely change in the future).

        Hence, you would have two scenarios where this task will create a list of
        the input files, fetch, and combine:

        1) The DA window matches the observation file window. (fetch a single file)

        2) The DA window is larger than the observation file window. Fetch AND
        combine all observation files that cover the full DA window. This could
        happen in two ways (examples are given for inputs (PT6H) to output (P1D)
        conversion).

        a) The DA window is perfectly covered by multiple observation files.

            Note for the few people that might actually care about this part:
            If you are considering using MERRA2 replay with GEOS, this is what
            you should be aiming for. R2D2 observations times (PT6H) are adjusted
            for that type of compatibility pertaining model and obs start times.

        inputs:       FILE1          FILE2           FILE3            FILE4
                ------------------------------------------------------------------
                        |              |               |                |
                       21Z            03Z             09Z              15Z
                        |              |               |                |
                ------------------------------------------------------------------
        output:                                      FILE1

        b) The DA window falls outside of observation file boundaries. There
        will be extra observations in the combined file but JEDI can handle that.

        inputs:       FILE1           FILE2           FILE3             FILE4           FILE5
                ------------------------------------------------------------------------------------
                        |       !       |               |        !        |               |        !
                       21Z      !      03Z             09Z      12Z      15Z             21Z       !
                        |       !       |               |        !        |               |        !
                ------------------------------------------------------------------------------------
        output:                                                FILE1

        Parameters
        ----------
        All inputs are extracted from the JEDI experiment file configuration.
        See the taskBase constructor for more information.

        Work Remaining
        --------------
        "tlapse" files need to be fetched.
        """

        # Parse config
        # ------------
        obs_experiment = self.config.obs_experiment()
        obs_providers = self.config.obs_provider()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        window_length = self.config.window_length()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        window_offset = self.config.window_offset()
        r2d2_local_path = self.config.r2d2_local_path()
        cycling_varbc = self.config.cycling_varbc(None)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        # Get window begin time
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_dto = self.da_window_params.window_begin_iso(window_offset, dto=True)
        window_end_dto = self.da_window_params.window_end_iso(window_offset, window_length,
                                                              dto=True)
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)

        # Determine the input observation files to be fetched, this mainly depends on
        # the observation file organization in R2D2. In other words, they could be
        # organized by hourly subsets instead of 6-hourly subsets.
        # Since there are R2D2 local and shared options using glob would not be
        # feasible and this helps user to have more flexibility in terms R2D2 structure
        # -----------------------------------------------------------------------
        obs_timesteps = ['T03', 'T09', 'T15', 'T21']
        obs_window_length = 'PT6H'

        obs_list_dto = self.create_obs_time_list(obs_timesteps, window_begin_dto, window_end_dto)
        # Add to JEDI template rendering dictionary
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Set R2D2 config file
        # --------------------
        create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), r2d2_local_path)

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Open the observation operator dictionary
            # ----------------------------------------
            observation_dict = self.jedi_rendering.render_interface_observations(observation)

            # Until R2D2v3 is fully implemented we will assume there could be multiple
            # observation providers for a given observation type.
            # We have to ensure obs_providers is a list for this loop to work
            for obs_provider in (obs_providers if isinstance(obs_providers, list)
                                 else [obs_providers]):
                # Fetch observation files
                # -----------------------
                combine_input_files = []
                # Here, we are fetching
                for obs_num, obs_time in enumerate(obs_list_dto):
                    obs_window_begin = dt.strftime(obs_time, datetime_formats['iso_format'])
                    target_file = os.path.join(self.cycle_dir(), f'{observation}.{obs_num}.nc4')
                    combine_input_files.append(target_file)
                    fetch(date=obs_window_begin,
                          target_file=target_file,
                          provider=obs_provider,
                          ignore_missing=True,
                          obs_type=observation,
                          time_window=obs_window_length,
                          type='ob',
                          experiment=obs_experiment)

                # Check how many of the combine_input_files exist in the cycle directory.
                # If all of them are missing proceed without creating an observation input
                # file since bias correction files still need to be propagated to the next cycle
                # for cycling VarBC.
                # -----------------------------------------------------------------------
                if not any([os.path.exists(f) for f in combine_input_files]):
                    self.logger.info(f'None of the {observation} files exist for this cycle!')
                    # continue
                else:
                    jedi_obs_file = observation_dict['obs space']['obsdatain']['engine']['obsfile']
                    self.logger.info(f'Processing observation file {jedi_obs_file}')

                    # If obs_list_dto has one member, then just rename the file
                    # ---------------------------------------------------------
                    if len(obs_list_dto) == 1:
                        os.rename(combine_input_files[0], jedi_obs_file)
                    else:
                        self.read_and_combine(combine_input_files, jedi_obs_file)

                    # Change permission
                    os.chmod(jedi_obs_file, 0o644)

                    # Observations were found for this provider, so we can break
                    # the provider loop
                    break

            # TODO: This part is not tested yet for cycling VarBC
            # Aircraft bias correction files
            # ------------------------------
            if observation == 'aircraft':

                # Aircraft bias correction files
                target_file_types = [
                    f'aircraft_abias_air_ascent',
                    f'aircraft_abias_air_ascentSquared',
                    f'aircraft_abias_air_constant',
                ]

                for target_file_type in target_file_types:

                    target_file = os.path.join(self.cycle_dir(),
                                               f'{target_file_type}.{background_time}.csv')

                    self.logger.info(f'Processing aircraft bias file {target_file}')

                    fetch(date=background_time,
                          target_file=target_file,
                          provider='gsi',
                          obs_type=target_file_type,
                          type='bc',
                          experiment=obs_experiment,
                          file_type='csv')

                    # Change permission
                    os.chmod(target_file, 0o644)

            # Otherwise there is only work to do if the observation operator has bias correction
            # ----------------------------------------------------------------------------------
            if 'obs bias' not in observation_dict:
                continue

            # Satellite bias correction (coeff and cov) files
            # -----------------------------------------------
            target_sbccoef = observation_dict['obs bias']['input file']
            target_sbccovr = observation_dict['obs bias']['covariance']['prior']['input file']

            # We assume fetch is required unless we are cycling VarBC
            fetch_required = True

            if cycling_varbc:
                if self.cycle_time_dto() == self.first_cycle_time_dto():
                    self.logger.info(f'Process satellite file {target_sbccoef} for the first cycle')
                    self.logger.info(f'Process satellite file {target_sbccovr} for the first cycle')

                else:
                    self.logger.info(f'Using satellite bias files from the previous cycle')
                    previous_bias_coef = self.previous_cycle_bias(target_sbccoef, window_length)
                    previous_bias_covr = self.previous_cycle_bias(target_sbccovr, window_length)

                    # Link the previous bias file to the current cycle directory
                    # -----------------------------------------------------------
                    self.logger.info(f'Linking {previous_bias_coef} to {target_sbccoef}')
                    self.geos.linker(previous_bias_coef, target_sbccoef, dst_dir=self.cycle_dir())
                    self.logger.info(f'Linking {previous_bias_covr} to {target_sbccovr}')
                    self.geos.linker(previous_bias_covr, target_sbccovr, dst_dir=self.cycle_dir())

                    fetch_required = False

            # This will skip the fetch if we are cycling VarBC
            if fetch_required:
                self.logger.info(f'Processing satellite bias file {target_sbccoef}')
                fetch(date=background_time,
                      target_file=target_sbccoef,
                      provider='gsi',
                      obs_type=observation,
                      type='bc',
                      experiment=obs_experiment,
                      file_type='satbias')

                self.logger.info(f'Processing satellite bias file {target_sbccovr}')
                fetch(date=background_time,
                      target_file=target_sbccovr,
                      provider='gsi',
                      obs_type=observation,
                      type='bc',
                      experiment=obs_experiment,
                      file_type='satbias_cov')

            # Change permission
            os.chmod(target_sbccoef, 0o644)
            os.chmod(target_sbccovr, 0o644)

            # Satellite time lapse
            # --------------------
            for target_file in self.get_tlapse_files(observation_dict):

                self.logger.info(f'Processing time lapse file {target_file}')

                fetch(date=background_time,
                      target_file=target_file,
                      provider='gsi',
                      obs_type=observation,
                      type='bc',
                      experiment=obs_experiment,
                      file_type='tlapse')

                # Change permission
                os.chmod(target_file, 0o644)

    # ----------------------------------------------------------------------------------------------

    def get_tlapse_files(self, observation_dict: dict) -> Union[None, int]:

        # Function to locate instances of tlapse in the obs operator config

        hash = observation_dict
        if 'obs bias' not in hash:
            return

        hash = hash['obs bias']
        if 'variational bc' not in hash:
            return

        hash = hash['variational bc']
        if 'predictors' not in hash:
            return

        predictors = hash['predictors']
        for p in predictors:
            if 'tlapse' in p:
                yield p['tlapse']

        return
    # ----------------------------------------------------------------------------------------------

    def previous_cycle_bias(self,
                            target_file: str,
                            window_length: str
                            ) -> str:

        # This requires two modifications, one in the directory and one in the filename.
        # Start with the changing the bias filename
        # -----------------------------------------------------------------
        bias_file = os.path.basename(target_file)

        # Get the date bit from the target file
        bias_path = os.path.dirname(target_file)
        dt_str = bias_path.split('/')[-2]

        # Get the previous cycle datetime string and replace it in the bias path
        previous_cycle_dto = self.cycle_time_dto() - isodate.parse_duration(window_length)
        previous_cycle_dt_str = previous_cycle_dto.strftime(datetime_formats['directory_format'])

        bias_path = bias_path.replace(dt_str, previous_cycle_dt_str)

        # Combine the new bias path and the file name
        # ---------------------------------------------
        new_target_file = os.path.join(bias_path, bias_file)

        return new_target_file

    # ----------------------------------------------------------------------------------------------

    # Read and combine variable data from multiple files
    # --------------------------------------------------

    def create_obs_time_list(
        self,
        obs_times: list,
        window_begin_dto: dt,
        window_end_dto: dt
    ) -> list:

        day_before_dto = window_begin_dto-timedelta(days=1)
        day_after_dto = window_end_dto+timedelta(days=1)

        # Create a full list of all the observation times that starts from day_before_dto
        # and ends at day_after_dto using obs_times
        # -----------------------------------------------------------------------
        obs_time_list = []

        current_date = day_before_dto
        while current_date <= day_after_dto:
            for hour in obs_times:
                # create a datetime object for the current date and hour
                dt = current_date.replace(hour=int(hour[1:]))
                # add the datetime object to the list
                obs_time_list.append(dt)
            current_date += timedelta(days=1)

        # Within obs_time_list, subset the list starting from the first time right before
        # window_begin_dto and ending just after window_end_dto
        # -----------------------------------------------------------------------
        # find the latest datetime in obs_time_list that is less than or equal to window_begin_dto
        start_date = max(dt for dt in obs_time_list if dt <= window_begin_dto)

        # find the earliest datetime in obs_time_list that is greater or equal to window_end_dto
        end_date = min(dt for dt in obs_time_list if dt >= window_end_dto)

        # create a list from obs_time_list that falls between start date and end date
        # Note 1: Making end_date inclusive inflates the number of observations
        # sent to JEDI unnecessarily.
        # Note 2: this assumes that the list is sorted
        # -----------------------------------------------------------------------
        subset_list = [dt for dt in obs_time_list if start_date <= dt < end_date]

        return subset_list
    # ----------------------------------------------------------------------------------------------

    # Get the target data from the netcdf file
    # ----------------------------------------
    def get_data(self, input_file: str, group: str, var_name: str) -> object:
        with nc.Dataset(input_file, 'r') as ds:
            return ds[group][var_name][:]

    # ----------------------------------------------------------------------------------------------

    def read_and_combine(self, input_filenames: list, output_filename: str) -> None:
        '''
        Combines multiple IODA v3 netcdf input files into a single output.
        Combining multiple files require final (total) location dimension size to be
        calculated in advance.

        Basically, this function creates an output file that duplicates the first
        input file's attributes and then fills with appended data from the input files.

        Channel dimension shows up as a second dimension and sometimes as a single
        dimension. Both cases require special handling and introduces additional
        exceptions to the code. Final channel dimension size remains the same.
        '''

        # Create a new file for writing, remove the file if it already exists
        # --------------------------------------------------------------------------
        self.logger.info(f"Creating file {output_filename}")
        if os.path.exists(output_filename):
            os.remove(output_filename)

        # Reduce the list of input files to only those that exist
        # -------------------------------------------------------------
        existing_files = [f for f in input_filenames if os.path.exists(f)]
        input_filenames = existing_files

        # Loop through the input files and get the total dimension size for each dimension
        # Location requires special handling to get the cumulative sum of the dimension size
        # ---------------------------------------------------------------------------------
        out_dim_size = {'Location': 0}
        for input_filename in input_filenames:
            with nc.Dataset(input_filename, 'r') as ds:
                for dim_name, dim in ds.dimensions.items():
                    if dim_name == 'Location':
                        out_dim_size[dim_name] += dim.size
                    else:
                        out_dim_size[dim_name] = dim.size

        with nc.Dataset(output_filename, 'w') as out_ds:
            # Open the input NetCDF files for reading
            # ---------------------------------------
            self.logger.info(f"Combining files {input_filenames} ")

            # Create an output file template based on the first input file
            # ------------------------------------------------------------
            with nc.Dataset(input_filenames[0], 'r') as ds:
                # Access groups and create dimensions
                # -----------------------------------
                input_groups = ds.groups.keys()

                for dim_name, dim in ds.dimensions.items():
                    out_ds.createDimension(dim_name, out_dim_size[dim_name])

                # Loop through groups and process variables
                # -----------------------------------------
                for group_name in input_groups:
                    group = ds[group_name]

                    # Create the groups in output file
                    # --------------------------------
                    out_group = out_ds.createGroup(group_name)

                    # Access variables within a group
                    # -------------------------------
                    variables_in_group = group.variables.keys()

                    # Loop over variables from input files, combine, and write to the new file
                    # ------------------------------------------------------------------------
                    for var_name in variables_in_group:
                        list_data = []

                        # Get the dimensions of the variable
                        # ----------------------------------
                        var_dims = group[var_name].dimensions

                        # Loop over all the files and combine the variable data into a list
                        # Channel dimensions remain the same, so we can break the loop
                        # ----------------------------------------------------------------
                        for input_file in input_filenames:
                            list_data.append(self.get_data(input_file, group_name, var_name))
                            # Only break if the first dimension is Channel
                            if var_dims[0] == 'Channel':
                                break

                        # Concatenate the masked arrays along the first dimension
                        # --------------------------------------------------------
                        variable_data = np.ma.concatenate(list_data, axis=0)

                        # Fill value needs to be assigned while creating variables
                        # --------------------------------------------------------
                        subset_var = out_group.createVariable(var_name,
                                                              variable_data.dtype,
                                                              var_dims,
                                                              fill_value=group[var_name].
                                                              getncattr('_FillValue'))
                        for attr_name in group[var_name].ncattrs():
                            if attr_name == '_FillValue':
                                continue
                            subset_var.setncattr(attr_name, group[var_name].getncattr(attr_name))

                        # Write subset data to the new file
                        # --------------------------------
                        subset_var[:] = variable_data

# ----------------------------------------------------------------------------------------------
