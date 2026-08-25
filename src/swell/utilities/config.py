# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


from ruamel.yaml import YAML
from typing import Callable

from swell.tasks.task_questions import TaskQuestions as task_questions
from swell.utilities.logger import Logger
from swell.suites.all_suites import AllSuites
from swell.utilities.swell_questions import SwellQuestion

# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


class Config():
    """Provides methods for reading YAML files and managing configuration
       parameters.

       Attributes
       ----------
       self : dict
         YAML definitions
       defs : dict
         Root-level YAML, environment and cycle dependent parameters

       Methods
       -------
       __init__(inputs):
         Reads in YAML files.
       define(cycle_dt):
         Defines cycle/time dependent parameters.
    """

    # ----------------------------------------------------------------------------------------------

    def __init__(self, input_file: str, logger: Logger, task_name: str, model: str) -> None:

        # Keep copy of owner's logger
        self.__logger__ = logger

        # Read the configuration yaml file
        yaml = YAML(typ='safe')
        with open(input_file, 'r') as ymlfile:
            experiment_dict = yaml.load(ymlfile)

        # Save some things that all tasks can use (suite level questions)
        self.__experiment_root__ = experiment_dict.get('experiment_root')
        self.__experiment_id__ = experiment_dict.get('experiment_id')
        self.__platform__ = experiment_dict.get('platform')
        self.__start_cycle_point__ = experiment_dict.get('start_cycle_point')
        self.__final_cycle_point__ = experiment_dict.get('final_cycle_point')
        self.__suite_to_run__ = experiment_dict.get('suite_to_run')

        # If experiment_dict contains models key add the model components to the object
        if 'models' in experiment_dict.keys():
            self.__model_components__ = list(experiment_dict['models'].keys())
        else:
            self.__model_components__ = None

        # Step1: flatten the dictionary based on the model
        # ------------------------------------------------

        # Extract the model config
        if model is not None:
            # Assert the model name is found in the config
            if model not in experiment_dict['models'].keys():
                self.__logger__.abort(f'Did not find the model \'{model}\' in the ' +
                                      f'experiment configuration')
            # Extract the model specific part of the config
            model_config = experiment_dict['models'][model]
            # Add model component to config
            experiment_dict['model_component'] = model
        else:
            model_config = {}

        self.all_model_configs = {}
        if 'models' in experiment_dict.keys():
            self.all_model_configs = experiment_dict['models']

        # Remove the model specific part from the full config
        if 'models' in experiment_dict.keys():
            del experiment_dict['models']

        # Assert that the full and model level configs have only unique keys
        for key in experiment_dict.keys():
            if key in model_config.keys():
                self.__logger__.abort(f'Model config contains the key \'{key}\'. Which is ' +
                                      f'also contained in the top level config.')

        # Now merge the top level config and the model specific parts of the config. This prevents
        # tasks from accessing the config associated with any model other than the one they are
        # supposed to act upon.
        experiment_dict.update(model_config)

        self.experiment_dict = experiment_dict

        # Step 2: create variables in the object with the keys/values in the config
        # -------------------------------------------------------------------------

        # Check for suite questions
        suite_questions = AllSuites.get_config(
                self.__suite_to_run__).get_all_question_names('suite')
        self.question_list = []

        # Add suite questions if they aren't already set
        for question in suite_questions:
            if question not in suite_questions:
                self.question_list.append(question)

        # Find the questions associated with the task
        if task_name in task_questions.get_all():
            self.question_list.extend(task_questions[task_name].value.get_all_question_names())

    # ----------------------------------------------------------------------------------------------

    def resolve(self, question: SwellQuestion, default='LrZRExPGcQ'):
        question_obj = question()
        name = question_obj.question_name

        if name in self.question_list:
            default = self.experiment_dict[name]
        elif name in self.experiment_dict:
            raise KeyError(f'Value {name} is present in config but this task has not been assigned'
                           ' it in `task_questions.py`')

        if default == 'LrZRExPGcQ':
            raise KeyError(f'Trying to reference value {name} in config but this key does not '
                           'exist and no default has been provided')
        
        data_type = question_obj.data_type

        if isinstance(data_type, list):
            if not any([dtype.is_type(default) for dtype in data_type]):
                self.__logger__.warning(f'Warning: Experiment key {name} does not conform to any expected'
                                        f' types {" ".join(data_type)}')

        elif not data_type.is_type(default):
            self.__logger__.warning(f'Warning: Experiment key {name} does not conform to expected'
                                    f' type <{data_type.value}>.')

        return default

    # ----------------------------------------------------------------------------------------------

    def get_key_for_model(self, name: str, model: str, default='LrZRExPGcQ'):
        """ Access keys in any model component. Provide a default to avoid errors. """

        try:
            default = self.all_model_configs[model][name]
        except KeyError:
            pass

        if default == 'LrZRExPGcQ':
            self.__logger__.abort(f"In config class, trying to reference value '{name}'" +
                                  f" for model '{model}', but config key does not exist and no" +
                                  f" default has been provided.")
        return default
# self.config.resolve(skip_ensemble_hofx, True)
# ----------------------------------------------------------------------------------------------
