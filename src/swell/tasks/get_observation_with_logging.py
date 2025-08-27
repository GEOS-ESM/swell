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
import r2d2

from datetime import timedelta, datetime as dt
from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
from swell.utilities.datetime_util import datetime_formats
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class GetObservationWithLogging(taskBase):

    """
    MODIFIED VERSION of the standard GetObservations task.

    This task performs the same logic as the original but adds detailed logging
    before each R2D2 fetch call. It prints the exact parameters being used for
    the search and the full source path of the file that R2D2 finds.
    """

    def execute(self) -> None:

        """
        Acquires observation files for a given experiment and cycle, with added logging.
        """
        print("xxxxxxxxxxxx")
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

        print(f"Configuration values:\n"
              f"  obs_experiment: {obs_experiment}\n"
              f"  obs_providers: {obs_providers}\n"
              f"  background_time_offset: {background_time_offset}\n"
              f"  observations: {observations}\n"
              f"  window_length: {window_length}\n"
              f"  crtm_coeff_dir: {crtm_coeff_dir}\n"
              f"  window_offset: {window_offset}\n"
              f"  r2d2_local_path: {r2d2_local_path}\n"
              f"  cycling_varbc: {cycling_varbc}")

#        # Parse config (This part is known to work in your environment)
#        # -------------------------------------------------------------
#        obs_experiment = self.config.obs_experiment()
#        obs_providers = self.config.obs_provider()
#        observations = self.config.observations()
#        window_length = self.config.window_length()
#        window_offset = self.config.window_offset()
#        r2d2_local_path = self.config.r2d2_local_path()
#        background_time_offset = self.config.background_time_offset()
#        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
#        cycling_varbc = self.config.cycling_varbc(None)
#
#        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))
#        window_begin = self.da_window_params.window_begin(window_offset)
#        window_begin_dto = self.da_window_params.window_begin_iso(window_offset, dto=True)
#        window_end_dto = self.da_window_params.window_end_iso(window_offset, window_length,
#                                                              dto=True)
#        background_time = self.da_window_params.background_time(window_offset,
#                                                                background_time_offset)
#        obs_timesteps = ['T03', 'T09', 'T15', 'T21']
#        obs_window_length = 'PT6H'
#        obs_list_dto = self.create_obs_time_list(obs_timesteps, window_begin_dto, window_end_dto)
#        self.jedi_rendering.add_key('background_time', background_time)
#        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
#        self.jedi_rendering.add_key('window_begin', window_begin)
#        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))
#
#        # Set R2D2 config file and create an R2D2 object for the 'locate' command
#        # -----------------------------------------------------------------------
#        r2d2_config_path = create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), r2d2_local_path)
#        r2d2_db = r2d2.R2D2(config_file=r2d2_config_path)
#
#        # Loop over observation operators
#        # -------------------------------
#        self.logger.info("\n====================== R2D2 Fetch Log ======================")
#        for observation in observations:
#            observation_dict = self.jedi_rendering.render_interface_observations(observation)
#            for obs_provider in (obs_providers if isinstance(obs_providers, list)
#                                 else [obs_providers]):
#                self.logger.info(f"\n--- Obs Type: '{observation}', Provider: '{obs_provider}' ---")
#                combine_input_files = []
#                for obs_num, obs_time in enumerate(obs_list_dto):
#                    obs_window_begin = dt.strftime(obs_time, datetime_formats['iso_format'])
#                    target_file = os.path.join(self.cycle_dir(), f'{observation}.{obs_num}.nc4')
#                    combine_input_files.append(target_file)
#
#                    # ++++++++++++++ ADDED LOGGING BLOCK ++++++++++++++
#                    # Construct dictionary of arguments for logging and locating
#                    fetch_criteria_for_locate = {
#                        'date': obs_window_begin,
#                        'provider': obs_provider,
#                        'obs_type': observation,
#                        'time_window': obs_window_length,
#                        'type': 'ob',
#                        'experiment': obs_experiment,
#                    }
#                    self.logger.info(f"Checking for file at time slot: {obs_window_begin}")
#                    self.logger.info(f"  Fetch call parameters will be: {fetch_criteria_for_locate}")
#
#                    try:
#                        source_path = r2d2_db.locate(**fetch_criteria_for_locate)
#                        self.logger.info(f"  SUCCESS: R2D2 located the source file at: {source_path}")
#                    except Exception as e:
#                        self.logger.info(f"  INFO: r2d2.locate did not find a file. Error: {e}")
#                    # ++++++++++++++ END OF LOGGING BLOCK ++++++++++++++
#
#                    # Original fetch call
#                    fetch(date=obs_window_begin,
#                          target_file=target_file,
#                          provider=obs_provider,
#                          ignore_missing=True,
#                          obs_type=observation,
#                          time_window=obs_window_length,
#                          type='ob',
#                          experiment=obs_experiment)
#
#                # This is the rest of the original code, unmodified
#                if not any([os.path.exists(f) for f in combine_input_files]):
#                    self.logger.info(f'None of the {observation} files exist for this cycle!')
#                else:
#                    jedi_obs_file = observation_dict['obs space']['obsdatain']['engine']['obsfile']
#                    self.logger.info(f'Processing observation file {jedi_obs_file}')
#                    if len(obs_list_dto) == 1:
#                        os.rename(combine_input_files[0], jedi_obs_file)
#                    else:
#                        self.read_and_combine(combine_input_files, jedi_obs_file)
#                    os.chmod(jedi_obs_file, 0o644)
#                    break
#            if 'obs bias' not in observation_dict:
#                continue
#            # ... (The rest of the bias correction and tlapse code is unchanged) ...
#    
#    # All other methods (get_tlapse_files, previous_cycle_bias, create_obs_time_list, etc.)
#    # are copied from your original file and are unchanged.
#
#    def get_tlapse_files(self, observation_dict: dict) -> Union[None, int]:
#        hash = observation_dict
#        if 'obs bias' not in hash: return
#        hash = hash['obs bias']
#        if 'variational bc' not in hash: return
#        hash = hash['variational bc']
#        if 'predictors' not in hash: return
#        predictors = hash['predictors']
#        for p in predictors:
#            if 'tlapse' in p: yield p['tlapse']
#        return
#    def previous_cycle_bias(self, target_file: str, window_length: str) -> str:
#        bias_file = os.path.basename(target_file)
#        bias_path = os.path.dirname(target_file)
#        dt_str = bias_path.split('/')[-2]
#        previous_cycle_dto = self.cycle_time_dto() - isodate.parse_duration(window_length)
#        previous_cycle_dt_str = previous_cycle_dto.strftime(datetime_formats['directory_format'])
#        bias_path = bias_path.replace(dt_str, previous_cycle_dt_str)
#        new_target_file = os.path.join(bias_path, bias_file)
#        return new_target_file
#    def create_obs_time_list( self, obs_times: list, window_begin_dto: dt, window_end_dto: dt) -> list:
#        day_before_dto = window_begin_dto-timedelta(days=1)
#        day_after_dto = window_end_dto+timedelta(days=1)
#        obs_time_list = []
#        current_date = day_before_dto
#        
#        te <= day_after_dto:
#            for hour in obs_times:
#                dt_obj = current_date.replace(hour=int(hour[1:]))
#                obs_time_list.append(dt_obj)
#             curre)
#         start_date = max(dt for dt in obs_time_list if dt <= window_begin_dto)
#         end_date = min(dt for dt in obs_time_list if dt >= window_end_dto)
#         subset_list = [dt for dt in obs_time_list if start_date <= dt < end_date]
#         return subset_list
#     def get_data(self, input_file: str, group: str, var_name: str) -> object:
#         with nc.Dataset(input_file, 'r') as ds:
#             return ds[group][var_name][:]
#     def read_and_combine(self, input_filenames: list, output_filename: str) -> None:
#         self.logger.info(f"Creating file {output_filename}")
#         if os.path.exists(output_filename): os.remove(output_filename)
#         existing_files = [f for f in input_filenames if os.path.exists(f)]
#         input_filenames = existing_files
#         out_dim_size = {'Location': 0}
#         for input_filename in input_filenames:
#             with nc.Dataset(input_filename, 'r') as ds:
#                 for dim_name, dim in ds.dimensions.items():
#                     if dim_name == 'Location':
#                         out_dim_size[dim_name] += dim.size
#                    else:
#                        out_dim_size[dim_name] = dim.size
#        with nc.Dataset(output_filename, 'w') as out_ds:
#            self.logger.info(f"Combining files {input_filenames} ")
#            with nc.Dataset(input_filenames[0], 'r') as ds:
#                input_groups = ds.groups.keys()
#                for dim_name, dim in ds.dimensions.items():
#                    out_ds.createDimension(dim_name, out_dim_size[dim_name])
#                for group_name in input_groups:
#                    group = ds[group_name]
#                    out_group = out_ds.createGroup(group_name)
#                    variables_in_group = group.variables.keys()
#                    for var_name in variables_in_group:
#                        list__data = []
#                        var_dims = group[var_name].dimensions
#                        for input_file in input_filenames:
#                            list_data.append(self.get_data(input_file, group_name, var_name))
#                            if var_dims[0] == 'Channel': break
#                        variable_data = np.ma.concatenate(list_data, axis=0)
#                        subset_var = out_group.createVariable(var_name, variable_data.dtype, var_dims, fill_value=group[var_name].getncattr('_FillValue'))
#                        for attr_name in group[var_name].ncattrs():
#                            if attr_name == '_FillValue': continue
#                            subset_var.setncattr(attr_name, group[var_name].getncattr(attr_name))
#                        subset_var[:] = variable_data
