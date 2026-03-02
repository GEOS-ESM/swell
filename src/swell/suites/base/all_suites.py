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
from swell.suites.base.suite_questions import SuiteQuestions
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
    # Maps suites to workflow objects

    def __init__(self) -> None:
        workflow_dict = {}

        for suite in get_suites():
            workflow_path = os.path.join(get_swell_path(), 'suites', suite, 'workflow.py')
            if os.path.exists(workflow_path):
                workflow = getattr(
                        import_module(f'swell.suites.{suite}.workflow'), f'Workflow_{suite}')

                workflow_dict[suite] = workflow

        self.workflow_dict = workflow_dict

    def get_workflow(self, suite: str) -> type[CylcWorkflow]:
        return self.workflow_dict[suite]

    def all_workflows(self) -> list:
        return self.workflow_dict.keys()

# --------------------------------------------------------------------------------------------------

workflows = Workflows()

# --------------------------------------------------------------------------------------------------

class SuiteConfigs():

    def __init__(self) -> None:

        # Dictionary tracking configs under each suite
        self.__suites_to_configs_map__ = {}
        self.__configs_to_suites_map__ = {}

        # Dictionary tracking the suite for each config
        self.__config_map__ = {}
    
    def register(self, base_suite: str, config_name: str, question_list: QuestionList) -> None:
        
        if base_suite not in self.__suite_map__:
            self.__suites_to_configs_map__[base_suite] = []

        self.__suites_to_configs_map__[base_suite].append(config_name)

        self.__configs_to_suites_map__[config_name] = base_suite

        self.__config_map__[config_name] = question_list

    def get_config(self, config_name: str) -> QuestionList:
        return self.__config_map__[config_name]
    
    def base_suite(self, config_name: str) -> str:
        return self.__configs_to_suites_map__[config_name]
    
    def all_configs(self) -> str:
        return list(self.__configs_to_suites_map__.keys())

# --------------------------------------------------------------------------------------------------

# Objects to reference in imports
suite_configs = SuiteConfigs()

discover_plugins(swell.suites)

# --------------------------------------------------------------------------------------------------
