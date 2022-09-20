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
import sys
import time

# local imports
from swell.tasks.base.config import Config
from swell.tasks.base.datetime import Datetime
from swell.utilities.logger import Logger
from swell.tasks.task_registry import valid_tasks
from swell.tasks.utilities.utils import camelcase_to_underscore


# --------------------------------------------------------------------------------------------------


class taskBase(ABC):

    # Base class constructor
    def __init__(self, config_input, datetime_input, task_name):

        # Create message logger
        # ---------------------
        self.logger = Logger(task_name)

        # Write out the initialization info
        # ---------------------------------
        self.logger.info('  Initializing task with the following parameters:')
        self.logger.info('  Task name:     ' + task_name)
        self.logger.info('  Configuration: ' + config_input)

        # Create a configuration object
        # -----------------------------
        self.config = Config(config_input, self.logger)

        # If task receives a datetime create the object and update the config
        # -------------------------------------------------------------------
        if (datetime_input is not None):

            # Write out the datetime
            self.logger.info('  Date and time: ' + datetime_input + '\n')

            # Create a datetime object
            self.datetime = Datetime(datetime_input)

            # Augment configuration with cycle time.
            self.config.add_cyle_time_parameter(self.datetime.datetime)

            # Add data assimilation window paramters to config
            self.config.add_data_assimilation_window_parameters()

        # Resolve all variables that can be resolved
        # ------------------------------------------
        self.config.resolve_config_file()

    # Execute is the place where a task does its work. It's defined as abstract in the base class
    # in order to force the sub classes (tasks) to implement it.
    @abstractmethod
    def execute(self):
        pass


# --------------------------------------------------------------------------------------------------


class taskFactory():

    def create_task(self, task, config, datetime):

        # Convert capitilized string to one with underscores
        task_lower = camelcase_to_underscore(task)

        # Import class based on user selected task
        task_class = getattr(importlib.import_module('swell.tasks.'+task_lower), task)

        # Return task object
        return task_class(config, datetime, task)


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
    task_object = creator.create_task(task, config, datetime)
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
@click.option('-m', '--model', 'model', default='all')
def main(task, config, datetime, model):

    task_main(task, config, datetime, model)


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()

# --------------------------------------------------------------------------------------------------
