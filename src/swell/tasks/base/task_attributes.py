# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob
import importlib

from swell.swell_path import get_swell_path
from swell.utilities.case_switching import snake_case_to_camel_case

# --------------------------------------------------------------------------------------------------

class TaskAttributes():
    def __init__(self) -> None:
        task_path = os.path.join(get_swell_path(), 'tasks', '*.py')

        self.task_map = {}

        for task_file in glob.glob(task_path):
            module_name = os.path.basename(task_file).split('.py')[0]
            module_path = f'swell.tasks.{module_name}'

            try:
                module = importlib.import_module(module_path)
                setup = getattr(module, 'Setup')

                task_name = snake_case_to_camel_case(module_name)

                self.task_map[task_name] = setup

            except (ImportError, AttributeError):
                pass

    def get(self, task_name: str):
        return self.task_map[task_name]

# --------------------------------------------------------------------------------------------------