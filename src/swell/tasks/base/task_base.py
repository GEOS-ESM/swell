#!/usr/bin/env python

# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
from abc import ABC, abstractmethod
import glob
import importlib
import os
import time

# swell imports
from swell.swell_path import get_swell_path
from swell.utilities.case_switching import camel_case_to_snake_case, snake_case_to_camel_case
from swell.utilities.config import Config
from swell.utilities.data_assimilation_window_params import DataAssimilationWindowParams
from swell.utilities.datetime import Datetime
from swell.utilities.logger import Logger
from swell.utilities.render_jedi_interface_files import JediConfigRendering
from swell.utilities.geos import Geos


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
        self.config = Config(config_input, self.logger, task_name, self.__model__)

        # All experiment have the experiment root and id and suite
        # --------------------------------------------------------
        self.__experiment_root__ = self.config.__experiment_root__
        self.__experiment_id__ = self.config.__experiment_id__

        # Save the model components
        # -------------------------
        self.__model_components__ = self.config.__model_components__

        # Create cycle and forecast directories
        # -------------------------------------
        cycle_dir = None
        self.cycle_forecast_dir = None

        if datetime_input is not None:
            # Name of directory where cycle forecast files will be staged
            self.cycle_forecast_dir = os.path.join(self.experiment_path(), 'run',
                                                   self.__datetime__.string_directory(), 'forecast')

            if model is not None:
                cycle_dir = self.cycle_dir()
                os.makedirs(cycle_dir, 0o755, exist_ok=True)

        # Add JEDI config rendering helper
        # --------------------------------
        self.jedi_rendering = JediConfigRendering(self.logger, self.__experiment_root__,
                                                  self.__experiment_id__, cycle_dir, self.__model__)

        # Add GEOS utils
        # --------------
        self.geos = Geos(self.logger, self.cycle_forecast_dir)

        # Create some extra helpers available when the datetime is present
        # ----------------------------------------------------------------
        if self.__datetime__ is not None:

            # Object for computing data assimilation window parameters
            self.da_window_params = DataAssimilationWindowParams(self.logger,
                                                                 self.__datetime__.string_iso())

    # ----------------------------------------------------------------------------------------------

    # Execute is the place where a task does its work. It's defined as abstract in the base class
    # in order to force the sub classes (tasks) to implement it.
    @abstractmethod
    def execute(self):
        pass

    # ----------------------------------------------------------------------------------------------

    # Method to get the experiment root
    def experiment_root(self):
        return self.__experiment_root__

    # ----------------------------------------------------------------------------------------------

    # Method to get the experiment ID
    def experiment_id(self):
        return self.__experiment_id__

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

    def get_model_components(self):
        return self.__model_components__

    # ----------------------------------------------------------------------------------------------

    def is_datetime_dependent(self):
        if self.__datetime__ is None:
            return False
        else:
            return True

    # ----------------------------------------------------------------------------------------------

    def cycle_dir(self):

        # Check that model is set
        self.logger.assert_abort(self.__model__ is not None, 'In get_cycle_dir but this ' +
                                 'should not be called if the task does not receive model.')

        # Combine datetime string (directory format) with the model
        cycle_dir = os.path.join(self.experiment_path(), 'run',
                                 self.__datetime__.string_directory(), self.__model__)

        # Return
        return cycle_dir

    # ----------------------------------------------------------------------------------------------

    def forecast_dir(self, paths=[]):

        # Make sure forecast directory exists
        # -----------------------------------
        os.makedirs(self.cycle_forecast_dir, 0o755, exist_ok=True)

        # Combine datetime string (directory format) with the model
        # ------------------------------------------------------
        forecast_dir = self.cycle_forecast_dir

        if len(paths) > 0:
            # If paths (which should be a list) is not empty, combine with forecast_dir
            # -------------------------------------------------------------------------
            if isinstance(paths, str):
                paths = [paths]

            # Combining list of paths with forecast dir for code brevity
            # ---------------------------------------------------------
            forecast_dir = os.path.join(forecast_dir, *paths)

        return forecast_dir

    # ----------------------------------------------------------------------------------------------

    def cycle_time_dto(self):

        return self.__datetime__.dto()

    # ----------------------------------------------------------------------------------------------

    def cycle_time(self):

        return self.__datetime__.string_iso()

    # ----------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------


class taskFactory():

    def create_task(self, task, config, datetime, model):

        # Convert camel case string to snake case
        task_lower = camel_case_to_snake_case(task)

        # Import class based on user selected task
        task_class = getattr(importlib.import_module('swell.tasks.'+task_lower), task)

        # Return task object
        return task_class(config, datetime, model, task)


# --------------------------------------------------------------------------------------------------

def get_tasks():

    # Path to tasks
    tasks_directory = os.path.join(get_swell_path(), 'tasks', '*.py')

    # List of tasks
    task_files = sorted(glob.glob(tasks_directory))

    # Get just the task name
    tasks = []
    for task_file in task_files:
        base_name = os.path.basename(task_file)
        if '__' not in base_name:
            tasks.append(snake_case_to_camel_case(base_name[0:-3]))

    # Return list of valid task choices
    return tasks

# --------------------------------------------------------------------------------------------------


def task_wrapper(task, config, datetime, model):

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
