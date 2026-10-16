# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from ruamel.yaml import YAML

from eva.eva_driver import eva

from swell.tasks.base.task_base import taskBase
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.comparisons import comparison_tags


# --------------------------------------------------------------------------------------------------


class EvaComparisonJediLog(taskBase):

    def execute(self) -> None:

        # Get the model
        # -------------
        model = self.get_model()

        # Get the log type
        # ----------------
        log_type = self.config.comparison_log_type()

        # Read Eva template file into dictionary
        # --------------------------------------
        eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_config_file = os.path.join(eva_path, f'comparison_jedi_log-{model}.yaml')
        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_str_template = eva_config_file_open.read()

        # Get the paths for the two experiments
        experiment_paths = self.config.comparison_experiment_paths()

        experiment_tag_paths = comparison_tags(experiment_paths, self.logger)

        experiment_tag_exp = list(experiment_tag_paths.keys())[0]
        experiment_tag_ctl = list(experiment_tag_paths.keys())[1]

        experiment_path_exp = list(experiment_tag_paths.values())[0]
        experiment_path_ctl = list(experiment_tag_paths.values())[1]

        yaml = YAML(typ='safe')
        with open(experiment_path_ctl, 'r') as f:
            experiment_dict_ctl = yaml.load(f)

        experiment_id_ctl = experiment_dict_ctl['experiment_id']

        with open(experiment_path_exp, 'r') as f:
            experiment_dict_exp = yaml.load(f)

        experiment_id_exp = experiment_dict_exp['experiment_id']

        cycle_dir_ctl = os.path.join(os.path.dirname(experiment_path_ctl), '..', 'run',
                                     self.__datetime__.string_directory(), self.get_model())
        cycle_dir_exp = os.path.join(os.path.dirname(experiment_path_exp), '..', 'run',
                                     self.__datetime__.string_directory(), self.get_model())

        # Info to task log
        info_string = 'Running Eva to plot from the jedi_log file'
        self.logger.info('')
        self.logger.info(info_string)
        self.logger.info('-'*len(info_string))

        # Create dictionary used to override the eva config
        eva_override = {}
        eva_override['cycle_dir'] = self.cycle_dir()
        eva_override['cycle_dir_ctl'] = cycle_dir_ctl
        eva_override['cycle_dir_exp'] = cycle_dir_exp

        eva_override['experiment_id_ctl'] = experiment_id_ctl
        eva_override['experiment_id_exp'] = experiment_id_exp

        eva_override['experiment_tag_ctl'] = experiment_tag_ctl
        eva_override['experiment_tag_exp'] = experiment_tag_exp

        eva_override['log_type'] = log_type

        # Override the eva dictionary
        eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
        eva_dict = yaml.load(eva_str)

        # Write eva dictionary to file
        # ----------------------------
        conf_output = os.path.join(self.cycle_dir(), 'eva', 'jedi_log',
                                   'comparison_jedi_log_eva.yaml')
        os.makedirs(os.path.dirname(conf_output), exist_ok=True)
        with open(conf_output, 'w') as outfile:
            yaml.dump(eva_dict, outfile)

        # Call eva
        # --------
        eva(eva_dict)
