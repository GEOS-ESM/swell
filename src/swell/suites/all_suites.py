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
from swell.suites.suite_questions import SuiteQuestions
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.utilities.swell_questions import QuestionList

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

    def get_workflow(self, suite: str) -> CylcWorkflow:
        return self.workflow_dict[suite]

    def all_workflows(self) -> list:
        return self.workflow_dict.keys()


# --------------------------------------------------------------------------------------------------


class SuiteConfigs():
    # Maps suite configuration objects

    def __init__(self) -> None:

        # Dictionary used to create the enum
        config_dict = {}
        # Map of config names to their parent suites
        config_map = {}

        # Find all of the suite configs
        for suite in get_suites():
            config_path = os.path.join(get_swell_path(), 'suites', suite, 'suite_config.py')
            if os.path.exists(config_path):
                suite_container = getattr(
                        import_module(f'swell.suites.{suite}.suite_config'), 'SuiteConfig')
                suite_configs = suite_container.get_all()

                for config in suite_configs:
                    config_dict[format_suite_name(config)] = getattr(suite_container, config)
                    config_map[format_suite_name(config)] = suite
            else:
                config_dict[suite] = SuiteQuestions.all_suites.value
                config_map[suite] = suite

        self.config_dict = config_dict
        self.__config_map__ = config_map

    # --------------------------------------------------------------------------------------------------

    def get_config(self, name: str) -> QuestionList:
        return self.config_dict[name].value

    # --------------------------------------------------------------------------------------------------

    def all_configs(self) -> list:
        return self.config_dict.keys()

    # --------------------------------------------------------------------------------------------------

    def base_suite(self, config: str) -> str:
        return self.__config_map__[config]

# --------------------------------------------------------------------------------------------------


# Objects to reference in imports
suite_configs = SuiteConfigs()
workflows = Workflows()

# --------------------------------------------------------------------------------------------------
