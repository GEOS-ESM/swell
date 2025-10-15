# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Tuple
from abc import abstractmethod

from swell.utilities.cylc_formatting import CylcSection, indent_lines
from swell.tasks.task_runtimes import TaskRuntimes
from swell.utilities.logger import get_logger
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------


header_str = '''#!jinja2
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

'''


class CylcWorkflow():

    '''
    Handles generating the flow.cylc file contents using the CylcSection syntax for each
    necessary section in the cylc file. Since Swell workflows share a lot of common language,
    this method has the convenience of automatically setting a lot of the contents. This means
    that the graph section is the only part that will need to be adjusted in many cases,
    and tasks may need to be altered in src/swell/tasks/task_runtimes.py.
    '''

    def __init__(self, experiment_dict, slurm_external) -> None:
        self.experiment_dict = experiment_dict
        self.slurm_external = slurm_external

        self.logger = get_logger(self.__class__.__name__)

    # --------------------------------------------------------------------------------------------------

    def default_header(self) -> str:
        return header_str

    # --------------------------------------------------------------------------------------------------

    def get_independent_and_model_tasks(self) -> Tuple[list, dict]:
        # Separate the tasks into model independent and dependent

        ind_tasks = []
        model_tasks = {}

        models = []
        if 'model_components' in self.experiment_dict:
            models = self.experiment_dict['model_components']
        else:
            models = []

        for model in models:
            model_tasks[model] = []

        task_dict = self.tasks()

        for task_name, task in task_dict.items():
            if task.model is not None:
                model_tasks[task.model] = task_name
            else:
                ind_tasks.append(task_name)

        return ind_tasks, model_tasks

    # --------------------------------------------------------------------------------------------------

    @abstractmethod
    def get_workflow_string(self) -> str:
        return ''

    # --------------------------------------------------------------------------------------------------
