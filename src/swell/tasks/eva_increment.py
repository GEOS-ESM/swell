# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from eva.eva_driver import eva

from swell.tasks.base.task_base import taskBase
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------


class EvaIncrement(taskBase):

    def execute(self):

        # Get the model
        # -------------
        model = self.get_model()

        # Read Eva template file into dictionary
        # --------------------------------------
        eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_config_file = os.path.join(eva_path, f'increment-{model}.yaml')
        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_str_template = eva_config_file_open.read()

        # Info to task log
        info_string = 'Running Eva to plot from the increment file'
        self.logger.info('')
        self.logger.info(info_string)
        self.logger.info('-'*len(info_string))

        # Create time strings for eva_override directory
        cycle_time_reformat = self.cycle_time_dto().strftime('%Y%m%d_%H%M%Sz')
        window_begin_dto = self.da_window_params.window_begin(self.config.window_offset(),
                                                              dto=True)
        window_begin = window_begin_dto.strftime('%Y%m%d_%H%M%Sz')

        # Define the increment filename and path
        # TODO: Increment iteration number may change according to outer iteration loops
        # which is currenly manually set in varincrement1.yaml
        # For now we are only plotting the first one
        iter_no = 1
        incr_file = f'{self.experiment_id()}.increment-iter{iter_no}.{cycle_time_reformat}.nc4'
        increment_file_path = os.path.join(self.cycle_dir(), incr_file)

        # Create dictionary used to override the eva config
        eva_override = {}
        eva_override['cycle_dir'] = self.cycle_dir()
        eva_override['cycle_time'] = cycle_time_reformat
        eva_override['increment_file_path'] = increment_file_path
        eva_override['window_begin'] = window_begin

        # Override the eva dictionary
        eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
        eva_dict = yaml.safe_load(eva_str)

        # Write eva dictionary to file
        # ----------------------------
        conf_output = os.path.join(self.cycle_dir(), 'eva', 'increment', 'increment_eva.yaml')
        os.makedirs(os.path.dirname(conf_output), exist_ok=True)
        with open(conf_output, 'w') as outfile:
            yaml.dump(eva_dict, outfile, default_flow_style=False)

        # Call eva
        # --------
        eva(eva_dict)
