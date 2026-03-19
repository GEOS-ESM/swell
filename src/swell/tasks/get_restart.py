# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import load_r2d2_credentials

import isodate
import os
import r2d2

# --------------------------------------------------------------------------------------------------

r2d2_model_dict = {
    'geos_cf': 'geos_cf',
}


# --------------------------------------------------------------------------------------------------

class GetRestart(taskBase):

    def execute(self) -> None:
        """Fetches rst files for a given experiment and cycle from R2D2

        """

        # TODO: user input
        rst_file_types = ['achem_internal', 'aiau_import', 'cabc_internal', 'cabr_internal', 'caoc_internal', 'catch_internal', 'du_internal', 'fvcore_internal', 'geoschemchem_import', 'geoschemchem_internal', 'gocart_import', 'gocart_internal', 'gwd_import', 'hemco_import', 'hemco_internal', 'irrad_internal', 'lake_internal', 'landice_internal', 'moist_import', 'moist_internal', 'ni_internal', 'openwater_internal', 'pchem_internal', 'saltwater_import', 'seaicethermo_internal', 'solar_internal', 'ss_internal', 'su_internal', 'surf_import', 'tr_import', 'tr_internal', 'turb_import', 'turb_internal']


        cycle_dir = self.cycle_dir()
        scratch_dir = os.path.join(cycle_dir, 'scratch')
        model = self.__model__

        #print(self.config)
        #for k, v in vars(self.config).items():
        #    print(k, v)


        horizontal_resolution = self.config.horizontal_resolution()

        window_length = self.config.window_length()
        window_begin = self.da_window_params.window_begin(window_length, dto=True)
        print(window_begin)
        print(isodate.parse_duration(window_length))

        window_begin_prev = window_begin - isodate.parse_duration(window_length)
        rst_step = window_length

        # Use rst_experiment for first cycle
        if self.cycle_time_dto() == self.start_cycle_point_dto():
            rst_exp = self.config.rst_experiment()
            #rst_exp = 'swell_test'
        else:
            rst_exp = self.config.r2d2_experiment_id()

        self.logger.info(f'Fetching rst from experiment {rst_exp}')         
 
        for file_type in rst_file_types:
            base =  os.path.join(scratch_dir,file_type)
            target_file=f'{base}_rst'
            print(target_file)
            r2d2.fetch(
                model=model,
                item='forecast',
                experiment=rst_exp,
                step=rst_step,
                resolution=horizontal_resolution,
                date=window_begin_prev.strftime('%Y-%m-%dT%H:%M:%SZ'),
                target_file=target_file,
                file_extension='nc',
                file_type=file_type,
                )

            # Change permission
            os.chmod(target_file, 0o644)

# --------------------------------------------------------------------------------------------------
