# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import isodate
import os
from r2d2 import store

from swell.tasks.base.task_base import taskBase
# from swell.utilities.datetime_util import datetime_formats
# from swell.utilities.file_system_operations import copy_to_dst_dir
from swell.utilities.r2d2 import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------


class SaveRestart(taskBase):

    def execute(self):

        """
        Store GEOS-CF checkpoint restart files to R2D2 as symlinks or actual files.
        Saves checkpoint files that are valid at the beginning of the next DA window so they
        can be retrieved by GetRestart in the subsequent cycle.
 
        For other models skip (old code for the other models can be removed)
        """

        model = self.__model__
        if model == 'geos_cf':
                    
            # Load R2D2 credentials
            # ---------------------
            load_r2d2_credentials(self.logger, self.platform())

            # Parse config
            # ------------
            window_length = self.config.window_length()
            expid = self.config.r2d2_experiment_id()
            horizontal_resolution = self.config.horizontal_resolution()

            cycle_dir = self.cycle_dir()
            scratch_dir = os.path.join(cycle_dir, 'scratch')

            # Window begin for the current cycle
            # ------------------------------------
            window_begin = self.da_window_params.window_begin(window_length, dto=True)

            # Checkpoint files are valid at the start of the next window
            # -----------------------------------------------------------
            next_window_begin = window_begin + isodate.parse_duration(window_length)
            checkpoint_time_str = next_window_begin.strftime('%Y%m%d_%H%Mz')

            rst_file_types = self.config.rst_file_types()
            rst_store_interval = self.config.rst_store_interval(None)

            # Determine whether to store as a symlink for this cycle
            # --------------------------------------------------------
            store_as_symlink = True
            if rst_store_interval is not None:
                cycle_duration = isodate.parse_duration(window_length)
                elapsed = window_begin - self.start_cycle_point_dto()
                cycle_number = round(elapsed / cycle_duration) + 1
                store_as_symlink = (cycle_number % rst_store_interval != 0)
                self.logger.info(f'Cycle number: {cycle_number}, rst_store_interval: '
                                 f'{rst_store_interval}, store_as_symlink: {store_as_symlink}')

            for file_type in rst_file_types:
                fname = f'{file_type}_checkpoint.{checkpoint_time_str}.nc4'
                source_file = os.path.join(scratch_dir, fname)

                if not os.path.isfile(source_file):
                    self.logger.abort(f'Expected checkpoint file not found: {source_file}')

                self.logger.info(f'Storing {fname}')

                store(
                    model=model,
                    item='forecast',
                    step=window_length,
                    experiment=expid,
                    resolution=horizontal_resolution,
                    date=window_begin.strftime('%Y%m%dT%H%M%S%z'),
                    source_file=source_file,
                    file_extension='nc',
                    file_type=file_type,
                    store_as_symlink=store_as_symlink,
                )


        else:
            self.logger.info('Skipping this task as R2D2v3 restart storage is not implemented ' +
                             'for coupled models yet')
            return
    
            # Load R2D2 credentials
            # ---------------------
            load_r2d2_credentials(self.logger, self.platform())
    
            # Parse config
            window_type = self.config.window_type()
            window_length = self.config.window_length()
            forecast_duration = self.config.forecast_duration()
            self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))
    
            # Position relative to center of the window where forecast starts
            background_time_offset = self.config.background_time_offset()
            forecast_start_time = self.cycle_time_dto() - isodate.parse_duration(background_time_offset)
    
            # Convert to datetime durations
            local_background_time = self.da_window_params.local_background_time(window_length,
                                                                                window_type)
            local_background_time_iso = self.da_window_params.local_background_time_iso(window_length,
                                                                                        window_type)
            analysis_time_iso = self.da_window_params.analysis_time_iso()
            self.jedi_rendering.add_key('local_background_time', local_background_time)
            self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
            self.jedi_rendering.add_key('analysis_time_iso', analysis_time_iso)
    
            # Get r2d2 dictionary
            r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')
    
            # Loop over fc
            for fc in r2d2_dict['store']['fc']:
                store(date=forecast_start_time,
                      source_file=fc['filename'],
                      model='mom6_cice6_UFS',
                      file_type=fc['file_type'],
                      fc_date_rendering='analysis',
                      step=window_length,
                      resolution=self.config.horizontal_resolution(),
                      type='fc',
                      experiment=self.config.r2d2_experiment_id())
    
            # Loop over an
            for an in r2d2_dict['store']['an']:
                store(date=self.cycle_time_dto(),
                      source_file=an['filename'],
                      model='mom6_cice6_UFS',
                      file_type=an['file_type'],
                      fc_date_rendering='analysis',
                      resolution=self.config.horizontal_resolution(),
                      type='an',
                      experiment=self.config.r2d2_experiment_id())
    
            # Oceanstats needs special handling from the forecast folder. It is produced at the end of
            # the forecast and could be saved as a good metric. We are replicating the same structure as
            # the R2D2 files.
            mainf = os.path.join(r2d2_local_path, 'mom6_cice6_UFS',
                                 'fc',
                                 self.experiment_id(),
                                 'global',
                                 self.config.horizontal_resolution())
    
            dst_date = dt.strftime(forecast_start_time, datetime_formats['iso_format'])
    
            # Oceanstats is produced at the end of the forecast
            src_stats = self.forecast_dir(['scratch', 'ocean.stats.nc'])
            dst_stats = os.path.join(mainf, forecast_start_time.strftime('%Y-%m-%d'),
                                     f'mom6_cice6_UFS.{self.experiment_id()}.fc.global.MOM.oceanstats.'
                                     + dst_date + '.' + forecast_duration + '.nc')
    
            copy_to_dst_dir(self.logger, src_stats, dst_stats)
    
# --------------------------------------------------------------------------------------------------
