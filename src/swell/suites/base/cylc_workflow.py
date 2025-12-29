# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Tuple
from abc import abstractmethod, ABC

from swell.utilities.logger import get_logger

# --------------------------------------------------------------------------------------------------


header_str = '''#!jinja2
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

'''


class CylcWorkflow(ABC):

    """Abstract class setting tasks to be run by the workflow,
    as well as specifying the contents of flow.cylc.

    Attributes:
    experiment_dict: Mapping of suite config to use in configuring the graph
    slurm_external: Mapping of user and global slurm settings
    tasks: list of TaskSetup objects which specify questions used by the
           suite and cylc runtime attributes
    """

    def __init__(self, experiment_dict, slurm_external) -> None:
        self.experiment_dict = experiment_dict
        self.slurm_external = slurm_external

        self.logger = get_logger(self.__class__.__name__)

        self.tasks = []
        self.set_tasks()

    # --------------------------------------------------------------------------------------------------

    def default_header(self) -> str:
        """Set the default header, contains copyright information for Swell."""
        return header_str

    # --------------------------------------------------------------------------------------------------

    @abstractmethod
    def set_tasks(self) -> None:
        """Abstract method to be overridden by child workflows, sets a list of TaskSetup objects."""
        pass

    # --------------------------------------------------------------------------------------------------

    def get_independent_and_model_tasks(self) -> Tuple[list, dict]:
        """Iterates through tasks and separate questions into model-independent and dependent.
        
        Returns:
        List of model-independent questions.
        Mapping of model to list of questions associated with that model.
        """

        ind_tasks = []
        model_tasks = {}

        models = []
        if 'model_components' in self.experiment_dict:
            models = self.experiment_dict['model_components']
        else:
            models = []

        for model in models:
            model_tasks[model] = []

        for task in self.tasks:
            if task.model is not None:
                model_tasks[task.model].append(task)
            else:
                ind_tasks.append(task)

        return ind_tasks, model_tasks

    # --------------------------------------------------------------------------------------------------

    @abstractmethod
    def get_workflow_string(self) -> str:
        """Abstract method containing instructions for constructing flow.cylc contents."""
        return ''

    # --------------------------------------------------------------------------------------------------
