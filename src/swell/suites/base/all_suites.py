# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from importlib import import_module

from swell.swell_path import get_swell_path
from swell.utilities.suite_utils import get_suites
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.utilities.swell_questions import QuestionList
import swell.suites
from swell.utilities.plugins import discover_plugins

# --------------------------------------------------------------------------------------------------


def format_suite_name(suite_name):
    # Format suite names starting with a digit
    return suite_name[1:] if suite_name[0] == '_' else suite_name

# --------------------------------------------------------------------------------------------------

class Workflows():

    def __init__(self) -> None:
        self.__workflow_names__ = []

    def register(self, name: str) -> None:
        self.__workflow_names__.append(name)
        def wrapper(cls):
            setattr(self, name, cls)
            return cls
        return wrapper
    
    def get(self, name: str) -> type[CylcWorkflow]:
        return getattr(self, name)
    
    def all(self) -> list:
        return self.__workflow_names__

# --------------------------------------------------------------------------------------------------


class SuiteConfigs():

    def __init__(self) -> None:

        # Dictionary tracking the suite for each config
        self.__config_map__ = {}
    
    # --------------------------------------------------------------------------------------------------
    
    def register(self,
                 base_suite: str,
                 config_name: str,
                 question_list: QuestionList) -> None:
        
        self.__config_map__[config_name] = sub_dict = {}

        sub_dict['suite'] = base_suite
        sub_dict['list'] = question_list
    
    # --------------------------------------------------------------------------------------------------

    def get_config(self, config_name: str) -> QuestionList:
        return self.__config_map__[config_name]['list']
    
    # --------------------------------------------------------------------------------------------------
    
    def base_suite(self, config_name: str) -> str:
        return self.__config_map__[config_name]['suite']

    # --------------------------------------------------------------------------------------------------
    
    def all_configs(self) -> str:
        return list(self.__config_map__.keys())
    
    # --------------------------------------------------------------------------------------------------

    def configs_under_suites(self) -> dict:
        suite_map = {}

        for config_name, config_dict in self.__config_map__.items():
            suite_name = config_dict['suite']

            if suite_name not in suite_map:
                suite_map[suite_name] = []

            suite_map[suite_name].append(config_name)

        return suite_map

# --------------------------------------------------------------------------------------------------

# Objects to reference in imports
suite_configs = SuiteConfigs()
workflows = Workflows()
discover_plugins(swell.suites)

# --------------------------------------------------------------------------------------------------
