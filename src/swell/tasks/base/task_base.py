#!/usr/bin/env python

# (C) Copyright 2021- United States Government as represented by the Administrator of the
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
import yaml

# local imports
from swell.tasks.base.config import Config
from swell.tasks.base.datetime import Datetime
from swell.utilities.date_time import datetime_formats
from swell.utilities.logger import Logger
from swell.tasks.base.task_registry import valid_tasks
from swell.tasks.base.utils import camelcase_to_underscore
from swell.utilities.date_time import DataAssimilationWindowParams
from swell.utilities.render_jedi_interface_files import JediConfigRendering


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
        self.__config__ = Config(config_input, self.logger, self.__model__)

        # All experiment have the experiment root and id and suite
        # --------------------------------------------------------
        self.__experiment_root__ = self.config_get('experiment_root')
        self.__experiment_id__ = self.config_get('experiment_id')
        self.__suite__ = self.config_get('suite_to_run')

        # Create some extra helpers available when the datetime is present
        # ----------------------------------------------------------------
        if self.__datetime__ is not None:

            # Create the cycle directory
            cycle_dir = self.get_cycle_dir()
            os.makedirs(cycle_dir, 0o755, exist_ok=True)

            # Jedi config file rendering
            self.jedi_rendering = JediConfigRendering(self.logger, self.__experiment_root__,
                                                      self.__experiment_id__, cycle_dir,
                                                      self.__model__)

            # Object for computing data assimilation window parameters
            self.da_window_params = DataAssimilationWindowParams(self.logger, self.__datetime__)

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

    # Method to get the experiment root
    def experiment_root(self):
        return self.__experiment_root__

    # ----------------------------------------------------------------------------------------------

    # Method to get the experiment ID
    def experiment_id(self):
        return self.__experiment_id__

    # ----------------------------------------------------------------------------------------------

    # Method to get the suite type
    def suite(self):
        return self.__suite__

    # ----------------------------------------------------------------------------------------------

    # Method to get the experiment directory
    def experiment_path(self):
        return os.path.join(self.__experiment_root__, self.__experiment_id__)

    # ----------------------------------------------------------------------------------------------

    # Method to get the experiment configuration directory
    def experiment_config_path(self):
        swell_exp_path = self.experiment_path()
        return os.path.join(swell_exp_path, 'configuration')

    # ----------------------------------------------------------------------------------------------

    def get_model(self):
        return self.__model__

    # ----------------------------------------------------------------------------------------------

    def is_datetime_dependent(self):
        if self.__datetime__ is None:
            return False
        else:
            return True

    # ----------------------------------------------------------------------------------------------

    def cycle_time(self):
        self.logger.assert_abort(self.__datetime__ is not None, f'Cannot obtain the cycle time' +
                                 f'when the task was not initialized with the cycle time.')
        return self.__datetime__

    # ----------------------------------------------------------------------------------------------

    def cycle_dir(self):

        # Check that model is set
        self.logger.assert_abort(self.__model__ is not None, 'In get_cycle_dir but this ' +
                                 'should not be called if the task does not receive model.')

        # Get the current cycle in directory format
        current_cycle_dir_format = self.__datetime__.strftime(datetime_formats['dir_format'])

        # Combine with the model
        cycle_dir = os.path.join(current_cycle_dir_format, self.__model__)

        # Return
        return cycle_dir

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
        valid_task_logger.abort('ABORT: Task not found in task registry.')

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
