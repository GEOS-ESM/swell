# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

<<<<<<< HEAD:src/swell/tasks/remove_forecast_dir.py
import shutil

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes

# --------------------------------------------------------------------------------------------------

task_name = 'RemoveForecastDir'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.is_cycling = True
=======
from collections.abc import Mapping
>>>>>>> develop:src/swell/configuration/jedi/interfaces/geos_cf/model/increment_cs.py

# --------------------------------------------------------------------------------------------------


def increment_cs(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']

    output = {
        'state component': {
            'states': [{
                'filetype': 'cube sphere history',
                'datapath': f'{cycle_dir}',
                'filename': f'{template_dict["experiment_id"]}.inc.%yyyy%mm%dd_%hh%MM%ssz.nc4'
            }]
        }
    }

    return output

# --------------------------------------------------------------------------------------------------
