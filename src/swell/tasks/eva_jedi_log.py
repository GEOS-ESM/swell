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


class EvaJediLog(taskBase):

    def execute(self) -> None:

        # Get the model
        # -------------
        model = self.get_model()

        # Read Eva template file into dictionary
        # --------------------------------------
        eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_config_file = os.path.join(eva_path, f'jedi_log-{model}.yaml')
        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_str_template = eva_config_file_open.read()

        # Info to task log
        info_string = 'Running Eva to plot from the jedi_log file'
        self.logger.info('')
        self.logger.info(info_string)
        self.logger.info('-'*len(info_string))

        # Create dictionary used to override the eva config
        eva_override = {}
        eva_override['cycle_dir'] = self.cycle_dir()

        # Override the eva dictionary
        eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
        eva_dict = yaml.safe_load(eva_str)

        # Write eva dictionary to file
        # ----------------------------
        conf_output = os.path.join(self.cycle_dir(), 'eva', 'jedi_log', 'jedi_log_eva.yaml')
        os.makedirs(os.path.dirname(conf_output), exist_ok=True)
        with open(conf_output, 'w') as outfile:
            yaml.dump(eva_dict, outfile, default_flow_style=False)

        # Call eva
        # --------
        eva(eva_dict)
