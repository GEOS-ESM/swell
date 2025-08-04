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
import datetime
# --------------------------------------------------------------------------------------------------
import r2d2
import datetime


class GetObservationsR2d2(taskBase):

# ----------------------------------------------
    def execute(self) -> None:

         # Parse config -- from experiment.yaml
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
         
        # print(f"Configuration values:\n"
        #       f"  obs_experiment: {obs_experiment}\n"
        #       f"  obs_providers: {obs_providers}\n"
        #       f"  background_time_offset: {background_time_offset}\n"
        #       f"  observations: {observations}\n"
        #       f"  window_length: {window_length}\n"
        #       f"  crtm_coeff_dir: {crtm_coeff_dir}\n"
        #       f"  window_offset: {window_offset}\n"
        #       f"  r2d2_local_path: {r2d2_local_path}\n"
        #       f"  cycling_varbc: {cycling_varbc}")


         now = "2023-10-10T00:00:00Z"
         
         fetch_criteria = {
             'item': 'observation',
             'provider': 'gmao-test',
             'observation_type': 'dummy_data',
             'file_extension': 'txt',
             'window_length': 'PT6H',
             'window_start': '20250701T023120Z',#now, 20250701T023120Z
         }

         # move target file to current working directory
         target_file_path = os.path.join(os.getcwd(), "fetched_file.txt")
         fetch_criteria["target_file"] = target_file_path

         print(f"Searching for file with criteria: {fetch_criteria}")
         r2d2.fetch(**fetch_criteria)






         exit()
         ################################################
         # Use a unique timestamp for a clean test
         now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
         
         # Metadata for the file we want to store
         # Note: 'experiment' is NOT included
         test_file_metadata = {
             'item': 'observation',
             'provider': 'gmao-test',
             'observation_type': 'dummy_data',
             'file_extension': 'txt',
             'data_store': 'r2d2-experiments-nccs-gmao',
             'window_start': now,
             'window_length': 'PT6H',
         }
        


         # Create a dummy source file
         # change with /discover/nobackup/projects/gmao/swell/r2d2-experiments-nccs-gmao/observation
         base_dir = '.'
         test_data_dir = os.path.join(base_dir, 'r2d2_test_data')
         os.makedirs(test_data_dir, exist_ok=True)
         source_file_path = os.path.join(test_data_dir, 'my_test_file.txt')
         with open(source_file_path, 'w') as f:
             f.write(f"This is a test for timestamp {now} using r2d2.store()\n")
         
         test_file_metadata['source_file'] = source_file_path
         
         print(source_file_path)
         
         # --- STORE the file using r2d2.store() ---
         print(f"Storing file with metadata: {test_file_metadata}")
         try:
             # THIS IS THE CORRECTED LINE
             r2d2.store(**test_file_metadata)
             print("SUCCESS!! File stored in R2D2\n\n")
         except Exception as e:
             print(f"ERROR: Could not store file. Error: {e}")
         exit()


         #Create a dummy source file
         # change with /discover/nobackup/projects/gmao/swell/r2d2-experiments-nccs-gmao/observation
        # base_dir = '.'
        # test_data_dir = os.path.join(base_dir, 'r2d2_test_data')
        # os.makedirs(test_data_dir, exist_ok=True)
        # source_file_path = os.path.join(test_data_dir, 'my_test_file.txt')
        # with open(source_file_path, 'w') as f:
        #     f.write(f"GET_OBS_R2D2 : This is a test for timestamp {now} using r2d2.store()\n")
        # 
        # test_file_metadata['source_file'] = source_file_path
        # print(source_file_path)
        # # --- STORE the file using r2d2.store() ---
        # print(f"Storing file with metadata: {test_file_metadata}")
        # try:
        #     # THIS IS THE CORRECTED LINE
        #     r2d2.store(**test_file_metadata)
        #     print("SUCCESS!! File stored in R2D2\n\n")
        # except Exception as e:
        #     print(f"ERROR: Could not store file. Error: {e}")
        #

         exit()

         fetch_criteria = {
             'item': 'observation',
             'provider': 'gmao-test',
             'observation_type': 'dummy_data',
             'file_extension': 'txt',
             'window_length': 'PT6H',
             'window_start': '20250701T023120Z',#now, 20250701T023120Z
         }

         # move target file to current working directory 
         target_file_path = os.path.join(os.getcwd(), "fetched_file.txt")
         fetch_criteria["target_file"] = target_file_path
         
         print(f"Searching for file with criteria: {fetch_criteria}")
         r2d2.fetch(**fetch_criteria)

        # try:
        #     r2d2.fetch(**fetch_criteria)
        #     if os.path.exists(target_file_path):
        #         print("SUCCESS! Fetched the file")
        #         with open(target_file_path, 'r') as f:
        #             print(f"File content: {f.read()}")
        #     else:
        #         print("\nFile was not found in R2D2 or couldn't be fetched")
        # except Exception as e:
        #     print(f"\nERROR during fetch: {e}")
         
         # 20250701T023120Z
         ######################################
         # old r2d2
         ############

        # fetch(date=obs_window_begin,
        #                  target_file=target_file,
        #                  provider=obs_provider,
        #                  ignore_missing=True,
        #                  obs_type=observation,
        #                  time_window=obs_window_length,
        #                  type='ob',
        #                  experiment=obs_experiment)
         exit()

        
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
         self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

         # Set R2D2 config file
         # --------------------
         create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), r2d2_local_path)


        # Add this after line 133
         
         # ADD DEBUG PRINTS HERE:
         r2d2_config_file = os.path.join(self.cycle_dir(), 'r2d2_config.yaml')
         self.logger.info(f"DEBUG: R2D2 config file: {r2d2_config_file}")
         
         if os.path.exists(r2d2_config_file):
             with open(r2d2_config_file, 'r') as f:
                 config_content = f.read()
                 self.logger.info(f"DEBUG: R2D2 config content:\n{config_content}")
             
             import yaml
             with open(r2d2_config_file, 'r') as f:
                 config_data = yaml.safe_load(f)
             
             if 'databases' in config_data:
                 for db_name, db_config in config_data['databases'].items():
                     db_root = db_config.get('root', 'Unknown')
                     self.logger.info(f"DEBUG: Database '{db_name}' -> {db_root}")
                     if os.path.exists(db_root):
                         self.logger.info(f"DEBUG: ✓ {db_root} exists!!")
                     else:
                         self.logger.info(f"DEBUG: X {db_root} does not exist")





         print("\nObservations:")
         print(observations)

         print("\nObs_list_dto")
         print(obs_list_dto)

         observation = observations[0]

         for obs_num, obs_time in enumerate(obs_list_dto):
             obs_window_begin = dt.strftime(obs_time, datetime_formats['iso_format'])
             target_file = os.path.join(self.cycle_dir(), f'{observation}.{obs_num}.nc4')

             print(target_file)






         #observation = observations[0]
         #target_file = os.path.join(self.cycle_dir(), f'{observation}.{obs_num}.nc4')
         #print(target_file)
### Loop over observation operators
#        # -------------------------------
#        for observation in observations:
#
#            # Open the observation operator dictionary
#            # ----------------------------------------
#            observation_dict = self.jedi_rendering.render_interface_observations(observation)
#
#            # Until R2D2v3 is fully implemented we will assume there could be multiple
#            # observation providers for a given observation type.
#            # We have to ensure obs_providers is a list for this loop to work
#            for obs_provider in (obs_providers if isinstance(obs_providers, list)
#                                 else [obs_providers]):
#                # Fetch observation files
#                # -----------------------
#                combine_input_files = []
#                # Here, we are fetching
#                for obs_num, obs_time in enumerate(obs_list_dto):
#                    obs_window_begin = dt.strftime(obs_time, datetime_formats['iso_format'])
#                    target_file = os.path.join(self.cycle_dir(), f'{observation}.{obs_num}.nc4')
#                    combine_input_files.append(target_file)
#                    fetch(date=obs_window_begin,
#                          target_file=target_file,
#                          provider=obs_provider,
#                          ignore_missing=True,
#                          obs_type=observation,
#                          time_window=obs_window_length,
#                          type='ob',
#                          experiment=obs_experiment)


    # ----------------------------------------------------------------------------------------------

#    def get_tlapse_files(self, observation_dict: dict) -> Union[None, int]:
#
#        # Function to locate instances of tlapse in the obs operator config
#
#        hash = observation_dict
#        if 'obs bias' not in hash:
#            return
#
#        hash = hash['obs bias']
#        if 'variational bc' not in hash:
#            return
#
#        hash = hash['variational bc']
#        if 'predictors' not in hash:
#            return
#
#        predictors = hash['predictors']
#        for p in predictors:
#            if 'tlapse' in p:
#                yield p['tlapse']
#
#        return
#    # ----------------------------------------------------------------------------------------------
#
#    def previous_cycle_bias(self,
#                            target_file: str,
#                            window_length: str
#                            ) -> str:
#
#        # This requires two modifications, one in the directory and one in the filename.
#        # Start with the changing the bias filename
#        # -----------------------------------------------------------------
#        bias_file = os.path.basename(target_file)
#
#        # Get the date bit from the target file
#        bias_path = os.path.dirname(target_file)
#        dt_str = bias_path.split('/')[-2]
#
#        # Get the previous cycle datetime string and replace it in the bias path
#        previous_cycle_dto = self.cycle_time_dto() - isodate.parse_duration(window_length)
#        previous_cycle_dt_str = previous_cycle_dto.strftime(datetime_formats['directory_format'])
#
#        bias_path = bias_path.replace(dt_str, previous_cycle_dt_str)
#
#        # Combine the new bias path and the file name
#        # ---------------------------------------------
#        new_target_file = os.path.join(bias_path, bias_file)
#
#        return new_target_file
#
#    # ----------------------------------------------------------------------------------------------
#
#    # Read and combine variable data from multiple files
#    # --------------------------------------------------
#
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
#    # ----------------------------------------------------------------------------------------------
#
#    # Get the target data from the netcdf file
#    # ----------------------------------------
#    def get_data(self, input_file: str, group: str, var_name: str) -> object:
#        with nc.Dataset(input_file, 'r') as ds:
#            return ds[group][var_name][:]
#
#    # ----------------------------------------------------------------------------------------------
#
#    def read_and_combine(self, input_filenames: list, output_filename: str) -> None:
#        '''
#        Combines multiple IODA v3 netcdf input files into a single output.
#        Combining multiple files require final (total) location dimension size to be
#        calculated in advance.
#
#        Basically, this function creates an output file that duplicates the first
#        input file's attributes and then fills with appended data from the input files.
#
#        Channel dimension shows up as a second dimension and sometimes as a single
#        dimension. Both cases require special handling and introduces additional
#        exceptions to the code. Final channel dimension size remains the same.
#        '''
#
#        # Create a new file for writing, remove the file if it already exists
#        # --------------------------------------------------------------------------
#        self.logger.info(f"Creating file {output_filename}")
#        if os.path.exists(output_filename):
#            os.remove(output_filename)
#
#        # Reduce the list of input files to only those that exist
#        # -------------------------------------------------------------
#        existing_files = [f for f in input_filenames if os.path.exists(f)]
#        input_filenames = existing_files
#
#        # Loop through the input files and get the total dimension size for each dimension
#        # Location requires special handling to get the cumulative sum of the dimension size
#        # ---------------------------------------------------------------------------------
#        out_dim_size = {'Location': 0}
#        for input_filename in input_filenames:
#            with nc.Dataset(input_filename, 'r') as ds:
#                for dim_name, dim in ds.dimensions.items():
#                    if dim_name == 'Location':
#                        out_dim_size[dim_name] += dim.size
#                    else:
#                        out_dim_size[dim_name] = dim.size
#
#        with nc.Dataset(output_filename, 'w') as out_ds:
#            # Open the input NetCDF files for reading
#            # ---------------------------------------
#            self.logger.info(f"Combining files {input_filenames} ")
#
#            # Create an output file template based on the first input file
#            # ------------------------------------------------------------
#            with nc.Dataset(input_filenames[0], 'r') as ds:
#                # Access groups and create dimensions
#                # -----------------------------------
#                input_groups = ds.groups.keys()
#
#                for dim_name, dim in ds.dimensions.items():
#                    out_ds.createDimension(dim_name, out_dim_size[dim_name])
#
#                # Loop through groups and process variables
#                # -----------------------------------------
#                for group_name in input_groups:
#                    group = ds[group_name]
#
#                    # Create the groups in output file
#                    # --------------------------------
#                    out_group = out_ds.createGroup(group_name)
#
#                    # Access variables within a group
#                    # -------------------------------
#                    variables_in_group = group.variables.keys()
#
#                    # Loop over variables from input files, combine, and write to the new file
#                    # ------------------------------------------------------------------------
#                    for var_name in variables_in_group:
#                        list_data = []
#
#                        # Get the dimensions of the variable
#                        # ----------------------------------
#                        var_dims = group[var_name].dimensions
#
#                        # Loop over all the files and combine the variable data into a list
#                        # Channel dimensions remain the same, so we can break the loop
#                        # ----------------------------------------------------------------
#                        for input_file in input_filenames:
#                            list_data.append(self.get_data(input_file, group_name, var_name))
#                            # Only break if the first dimension is Channel
#                            if var_dims[0] == 'Channel':
#                                break
#
#                        # Concatenate the masked arrays along the first dimension
#                        # --------------------------------------------------------
#                        variable_data = np.ma.concatenate(list_data, axis=0)
#
#                        # Fill value needs to be assigned while creating variables
#                        # --------------------------------------------------------
#                        subset_var = out_group.createVariable(var_name,
#                                                              variable_data.dtype,
#                                                              var_dims,
#                                                              fill_value=group[var_name].
#                                                              getncattr('_FillValue'))
#                        for attr_name in group[var_name].ncattrs():
#                            if attr_name == '_FillValue':
#                                continue
#                            subset_var.setncattr(attr_name, group[var_name].getncattr(attr_name))
#
#                        # Write subset data to the new file
#                        # --------------------------------
#                        subset_var[:] = variable_data

# ----------------------------------------------------------------------------------------------
        


       # now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
       # 
       # # Metadata for the file we want to store
       # test_file_metadata = {
       #     'item': 'observation',
       #     'provider': 'gmao-test',
       #     'observation_type': 'dummy_data',
       #     'file_extension': 'txt',
       #     'data_store': 'r2d2-experiments-nccs-gmao',
       #     'window_start': now,
       #     'window_length': 'PT6H',
       # }
       # 
       # test_file_metadata['source_file'] = source_file_path
       # 
       # ##### FETCH from R2D2
       # fetch_criteria = {
       #     'item': 'observation',
       #     'provider': 'gmao-test',
       #     'observation_type': 'dummy_data',
       #     'file_extension': 'txt',
       #     'window_length': 'PT6H',
       #     'window_start': now,
       # }
       # 
       # target_file_path = os.path.join(os.getcwd(), "fetched_file.txt")
       # fetch_criteria["target_file"] = target_file_path
       # 
       # print(f"Searching for file with criteria: {fetch_criteria}")
       # try:
       #     r2d2.fetch(**fetch_criteria)
       #     if os.path.exists(target_file_path):
       #         print("SUCCESS! Fetched the file")
       #         with open(target_file_path, 'r') as f:
       #             print(f"File content: {f.read()}")
       #     else:
       #         print("\nFile was not found in R2D2 or couldn't be fetched")
       # except Exception as e:
       #     print(f"\nERROR during fetch: {e}")
