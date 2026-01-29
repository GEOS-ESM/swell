# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from ruamel.yaml import YAML

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------

task_name = 'EvaIncrement'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.is_cycling = True
        self.is_model = True
        self.questions = [
            qd.marine_models(),
            qd.window_length(),
            qd.window_type()
        ]

# --------------------------------------------------------------------------------------------------


class EvaIncrement(taskBase):

    def execute(self) -> None:

        # Local import because module is not loaded until experiment launch
        from eva.eva_driver import eva

        # Get the model and window type
        # -----------------------------
        model = self.get_model()
        window_type = self.config.window_type()

        if model == 'geos_marine':
            marine_models = self.config.marine_models()

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
        window_begin_dto = self.da_window_params.window_begin(self.config.window_length(),
                                                              dto=True)
        window_begin = window_begin_dto.strftime('%Y%m%d_%H%M%Sz')

        # Define the increment filename and path
        # For 3D-Var and 3D-FGAT, the increment file is in the middle of the DA window
        # For 3D-FGAT atmos, the increment is at the beginning of the DA window. This
        # is just a limited implementation of 4DVAR in SWELL by turning the linear operator off,
        # where the cost-type is 4D-VAR in OOPS folder.
        # TODO: This really complicates the increment file naming and path for now, this
        # is a temporary solution (I'm refering to window type and atmos if statement)
        # TODO: Increment iteration number may change according to outer iteration loops
        # which is currenly manually set in varincrement1.yaml
        # For now we are only plotting the first one
        iter_no = 1
        incr_file = f'{self.experiment_id()}.increment-iter{iter_no}.{cycle_time_reformat}.nc4'
        if self.suite_name() == 'localensembleda':
            incr_file = f'geos.mean-inc.{window_begin}.nc4'
        if window_type == '4D' and 'atmos' in self.suite_name():
            incr_file = f'{self.experiment_id()}.increment-iter{iter_no}.{window_begin}.nc4'

        # Create dictionary used to override the eva config
        eva_override = {}

        # Soca case
        if model == 'geos_marine':
            ocn_cycle_time = self.cycle_time_dto().strftime('%Y-%m-%dT%H:%M:%SZ')
            incr_file = f'ocn.{self.experiment_id()}.incr.{ocn_cycle_time}.nc'

            eva_override['marine_models'] = marine_models

            if 'cice6' in marine_models:
                # sea-ice increment is optional
                ice_incr_file = f'ice.{self.experiment_id()}.incr.{ocn_cycle_time}.nc'
                ice_increment_file_path = os.path.join(self.cycle_dir(), ice_incr_file)
                eva_override['ice_increment_file_path'] = ice_increment_file_path

        increment_file_path = os.path.join(self.cycle_dir(), incr_file)

        eva_override['cycle_dir'] = self.cycle_dir()
        eva_override['cycle_time'] = cycle_time_reformat
        eva_override['increment_file_path'] = increment_file_path
        eva_override['window_begin'] = window_begin

        # Override the eva dictionary
        eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
        yaml = YAML(typ='safe')
        eva_dict = yaml.load(eva_str)

        # Write eva dictionary to file
        # ----------------------------
        conf_output = os.path.join(self.cycle_dir(), 'eva', 'increment', 'increment_eva.yaml')
        os.makedirs(os.path.dirname(conf_output), exist_ok=True)
        with open(conf_output, 'w') as outfile:
            # dont sort the mappings to preserve the order in the output yaml
            yaml.sort_base_mapping_type_on_output = False
            yaml.dump(eva_dict, outfile)

        # Call eva
        # --------
        eva(eva_dict)
