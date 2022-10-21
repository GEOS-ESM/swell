#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
from abc import ABC, abstractmethod
import click
import importlib
import os
import sys
import time

# local imports
from swell.tasks.base.config import Config
from swell.tasks.base.datetime import Datetime
from swell.utilities.logger import Logger
from swell.tasks.task_registry import valid_tasks
from swell.tasks.utilities.utils import camelcase_to_underscore
from swell.utilities.dictionary_utilities import dict_get


# --------------------------------------------------------------------------------------------------


class taskBase(ABC):

    # Base class constructor
    def __init__(self, config_input, datetime_input, model, task_name):

        # Create message logger
        # ---------------------
        self.logger = Logger(task_name)

        # Write out the initialization info
        # ---------------------------------
        self.logger.info('  Initializing task with the following parameters:')
        self.logger.info('  Task name:     ' + task_name)
        self.logger.info('  Configuration: ' + config_input)
        if (datetime_input is not None):
            self.logger.info('  Date and time: ' + datetime_input + '\n')

        # Create datetime
        # ---------------
        self.__datetime__ = None
        if datetime_input is not None:
            self.__datetime__ = Datetime(datetime_input)

        # Keep copy of model directive
        # ----------------------------
        self.__model__ = model

        # Create a configuration object
        # -----------------------------
        self.__config__ = Config(config_input, self.logger, self.__datetime__)

    # ----------------------------------------------------------------------------------------------

    # Execute is the place where a task does its work. It's defined as abstract in the base class
    # in order to force the sub classes (tasks) to implement it.
    @abstractmethod
    def execute(self):
        pass

    # ----------------------------------------------------------------------------------------------

    # Method to get something from config (with fail if not existing)
    def config_get(self, key, default='NODEFAULT'):
        return self.__config__.get(key, default)

    # ----------------------------------------------------------------------------------------------

    # Method to get something from the model specific config (with fail if not existing)
    def config_get_model(self, key):
        if model is None:
            self.logger.abort(f'The task base method \'config_get_model\' cannot be called' +
                              f'when the model directive is not passed to the task.')
        return dict_get(self.logger, self.__config__['models'][self.__model__], key)

    # ----------------------------------------------------------------------------------------------

    # Method to get the Swell experiment path
    def get_swell_exp_path(self):
        experiment_root = self.config_get('experiment_root')
        experiment_id = self.config_get('experiment_id')
        return os.path.join(experiment_root, experiment_id)

    # ----------------------------------------------------------------------------------------------

    # Method to get the Swell experiment configuration path
    def get_swell_exp_config_path(self):
        swell_exp_path = self.get_swell_exp_path()
        return os.path.join(swell_exp_path, 'configuration')

    # ----------------------------------------------------------------------------------------------

    # Method to open a specific configuration file
    def __open_jedi_interface_config_file(self, model_or_obs, config_name):
        # JEDI interface name
        jedi_interface = self.config_get_model('jedi_interface')

        # Swell application name
        jedi_interface_swell = self.config_get_model('jedi_interface_swell')

        # Get experiment configuration path
        swell_exp_config_path = self.get_swell_exp_config_path()

        # Path to configuration file
        jedi_stage_config = os.path.join(swell_exp_config_path, 'jedi', jedi_interface,
                                         jedi_interface_swell, model_or_obs, config_name + '.yaml')

        # Load file into dictionary

    # ----------------------------------------------------------------------------------------------

    # Method to open a specific model configuration file
    def open_jedi_interface_model_config_file(self, config_name):
        return self.__open_jedi_interface_config_file('model', config_name)

    # ----------------------------------------------------------------------------------------------

    # Method to open a specific observation configuration file
    def open_jedi_interface_obs_config_file(self, config_name):
        return self.__open_jedi_interface_config_file('observations', config_name)


# --------------------------------------------------------------------------------------------------


class taskFactory():

    def create_task(self, task, config, datetime, model):

        # Convert capitilized string to one with underscores
        task_lower = camelcase_to_underscore(task)

        # Import class based on user selected task
        task_class = getattr(importlib.import_module('swell.tasks.'+task_lower), task)

        # Return task object
        return task_class(config, datetime, model, task)


# --------------------------------------------------------------------------------------------------


def task_main(task, config, datetime, model):

    # For security check that task is in the registry
    if task not in valid_tasks:
        valid_task_logger = Logger('CheckValidTasks')
        valid_task_logger.info(' ')
        valid_task_logger.info('Task \'' + task + '\' not found in registry; valid tasks are:')
        valid_tasks.sort()
        for valid_task in valid_tasks:
            valid_task_logger.info('  ' + valid_task)
        valid_task_logger.info(' ')
        valid_task_logger.info('ABORT: Task not found in task registry.')
        sys.exit()

    # Create the object
    constrc_start = time.perf_counter()
    creator = taskFactory()
    task_object = creator.create_task(task, config, datetime, model)
    constrc_final = time.perf_counter()
    constrc_time = f'Constructed in {constrc_final - constrc_start:0.4f} seconds'

    # Execute task
    execute_start = time.perf_counter()
    task_object.execute()
    execute_final = time.perf_counter()
    execute_time = f'Executed in {execute_final - execute_start:0.4f} seconds'

    # Output timing stats
    task_object.logger.info('-----------------------------')
    task_object.logger.info('        Task Complete        ')
    task_object.logger.info('-----------------------------')
    task_object.logger.info('Timing statistics:')
    task_object.logger.info(constrc_time)
    task_object.logger.info(execute_time)
    task_object.logger.info('-----------------------------')


# --------------------------------------------------------------------------------------------------


@click.command()
@click.argument('task')
@click.argument('config')
@click.option('-d', '--datetime', 'datetime', default=None)
@click.option('-m', '--model', 'model', default=None)
def main(task, config, datetime, model):

    task_main(task, config, datetime, model)


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
