# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
from typing import Optional, Tuple
import importlib
import re
from enum import StrEnum, auto

from swell.swell_path import get_swell_path
from swell.utilities.suite_utils import get_suites
from swell.tasks.task_questions import TaskQuestions as tq
from swell.utilities.swell_questions import QuestionList
from swell.utilities.case_switching import camel_case_to_snake_case
from swell.suites.all_suites import workflows
from swell.utilities.logger import get_logger
from swell.deployment.prepare_config_and_suite.prepare_config_and_suite import (
        PrepareExperimentConfigAndSuite)


# --------------------------------------------------------------------------------------------------

class CodeDependentQuestions(StrEnum):
    """ Questions which are set by swell during experiment creation. """
    EXPERIMENT_ID = auto()
    EXPERIMENT_ROOT = auto()
    PLATFORM = auto()

    @classmethod
    def filter_list(cls, lst: list) -> list:
        values = [item.value for item in cls]
        return [item for item in lst if item not in values]

# --------------------------------------------------------------------------------------------------


def get_workflow(suite: str):
    """ Parse the suite's flow.cylc file and get all the tasks used by the suite. """

    logger = get_logger('CodeTests')

    prepare_config = PrepareExperimentConfigAndSuite(logger,
                                                     suite,
                                                     suite,
                                                     'nccs_discover_sles15',
                                                     'defaults',
                                                     None)

    suite_dict = prepare_config.get_experiment_dict()

    workflow_class = workflows.get_workflow(suite)
    workflow_obj = workflow_class(suite_dict, {})

    return workflow_obj

# --------------------------------------------------------------------------------------------------


def get_scheduling(suite: str):

    workflow_obj = get_workflow(suite)

    scheduling_section = workflow_obj.define_scheduling()

    return scheduling_section

# --------------------------------------------------------------------------------------------------


def get_all_tasks(suite: str) -> list:
    """ Parse the suite's flow.cylc file and get all the tasks used by the suite. """

    workflow_obj = get_workflow(suite)

    tasks = workflow_obj.parse_graph_for_tasks()

    base_tasks = []

    for task in tasks:
        base_task = task.split('-')[0]
        if base_task not in ['StageJediCycle', 'sync_point']:
            base_tasks.append(base_task)

    return base_tasks

# --------------------------------------------------------------------------------------------------


def get_question_names(config: QuestionList, model: Optional[str] = None) -> list:
    """ Get a list of question names from a QuestionList object. """
    return [q['question_name'] for q in config.expand_question_list(model)]

# --------------------------------------------------------------------------------------------------


def questions_in_cylc(suite: str) -> list:
    """ Parse the suite's flow.cylc file and get a list of external questions. """

    cylc_questions = []

    scheduling = get_scheduling(suite)

    lines = scheduling.split('\n')

    for line in lines:
        line = line.strip()

        if '.' in line or 'scheduling' in line or 'key' in line:
            None
        elif re.search(".* = {{.*}}", line):
            cylc_questions.append(
                    line.split('{{')[1].split('}}')[0].strip())
        elif 'models[' in line:
            cylc_questions.append(
                    line.split('["')[-1].split('"]')[0].strip())
        elif re.search(".*{%.* in .* %}", line) and '(' in line:
            cylc_questions.append(
                    line.split('(')[1].split(')')[0].strip())
        elif re.search(".*{%.* in .* %}", line):
            cylc_questions.append(
                    line.split('in ')[1].split(' %}')[0].strip())

    cylc_questions = sorted(list(set(cylc_questions)))
    return cylc_questions

# --------------------------------------------------------------------------------------------------


def compare_used_and_set_questions() -> Tuple[dict, dict]:
    """
    Finds the questions which are set in the suite/task configuration,
    and those that are actually used by the suite.

    This method returns two dictionaries, used_not_set and set_not_used, indexed by suite and task.

    used_not_set[suite]['suite'_or_task] is a list of questions which are used in the code,
    but are not specified in the suite config or task_questions.py

    set_not_used[suite]['suite'_or_task] consists of questions defined
    in the suite or task config, which are not used in the code.
    """

    suites = get_suites()

    # Dictionary for questions used in the suite, but not specified in configuration
    used_not_set = {}
    # Dictionary for questions set in the configuration, but not actually used
    set_not_used = {}

    # GEOS model components
    possible_model_components = os.listdir(os.path.join(get_swell_path(),
                                                        'configuration', 'jedi', 'interfaces'))

    for suite in suites:
        # Sub-suite dictionary for questions used in the code
        used_by = {}
        # Sub-suite dictionary for questions set in the configuration
        set_for = {}

        # Get the default suite configuration
        config_name = ('_' if suite[0].isdigit() else '') + suite
        suite_config = getattr(importlib.import_module(f'swell.suites.{suite}.suite_config'),
                               'SuiteConfig')
        base_config = suite_config[config_name].value

        config_questions = get_question_names(base_config)

        # Get questions which are specified as model-dependent
        for model in possible_model_components:
            config_questions.extend(get_question_names(base_config, model))

        config_questions = sorted(list(set(config_questions)))

        # Set suite-defined questions
        set_for['suite'] = CodeDependentQuestions.filter_list(config_questions)
        # Check for questions used by flow.cylc
        used_by['suite'] = CodeDependentQuestions.filter_list(questions_in_cylc(suite))

        tasks = get_all_tasks(suite)

        for task in tasks:
            # Task-specific used and set questions
            used_task = []
            set_task = []

            # Get the set questions for the task
            if task in tq.get_all():
                set_task.extend(get_question_names(tq[task].value))

                for model in possible_model_components:
                    set_task.extend(get_question_names(tq[task].value, model))

            # Check the task's code for the questions it uses
            task_file = os.path.join(get_swell_path(), 'tasks',
                                     camel_case_to_snake_case(task) + '.py')

            if os.path.exists(task_file):
                with open(task_file, 'r') as f:
                    config_lines = [line for line in f.readlines() if 'self.config.' in line]
                    for line in config_lines:
                        if 'get_key_for_model' in line:
                            field = line.split(
                                    'self.config.get_key_for_model(')[1].split(')')[0].strip() + ')'
                            if len(field.split(',')) == 1:
                                field = field.split(',')[0] + '()'
                            else:
                                field = field.split(',')[
                                        0].strip() + '(' + field.split(',')[-1].strip() + ')'

                            field = field.replace('"', '')
                            field = field.replace("'", '')
                        else:
                            field = line.split('self.config.')[1].split(')')[0].strip() + ')'

                        # Include the parentheses, so we can later
                        # assess whether the key is optional
                        used_task.append(field)

            set_task = sorted(list(set(set_task)))
            used_task = sorted(list(set(used_task)))

            # Filter out the questions set by the code
            set_task = CodeDependentQuestions.filter_list(set_task)
            used_task = CodeDependentQuestions.filter_list(used_task)

            used_by[task] = used_task
            set_for[task] = set_task

        used_not_set[suite] = {}
        set_not_used[suite] = {}

        # Set the dictionary for used-but-not-set questions
        for suite_task, lst in used_by.items():
            used_not_set[suite][suite_task] = []

            for question in lst:
                question_name = question.split('(')[0].strip()
                # Include only non-optional calls from the code
                if len(question_name.split(')')[0].strip()) == 0 and (
                        question_name not in set_for[suite_task] + set_for['suite']):
                    used_not_set[suite][suite_task].append(question_name)

            # Clear the suite or task key if there are no discrepancies
            if len(used_not_set[suite][suite_task]) == 0:
                del used_not_set[suite][suite_task]

        # Get a list of all questions used by tasks across the suite, to compare against the
        # set suite questions.
        all_used_questions = []
        for key in used_by.keys():
            for question in used_by[key]:
                if '(' in question:
                    all_used_questions.append(question.split('(')[0])
                else:
                    all_used_questions.append(question)

        # Set the dictionary for set-but-not-used questions
        for suite_task, lst in set_for.items():
            set_not_used[suite][suite_task] = []

            for question in lst:
                if suite_task == 'suite':
                    # Suite questions may be used in tasks throughout the suite
                    if question not in all_used_questions:
                        set_not_used[suite]['suite'].append(question)
                else:
                    # Include optional questions
                    used_by_all = [q if '(' not in q else q.split('(')[0]
                                   for q in used_by[suite_task]]
                    if question not in used_by_all:
                        set_not_used[suite][suite_task].append(question)

            # Clear the key if there are no discrepancies
            if len(set_not_used[suite][suite_task]) == 0:
                del set_not_used[suite][suite_task]

        # Clear the suite if there are no discrepancies
        if len(set_not_used[suite]) == 0:
            del set_not_used[suite]

        if len(used_not_set[suite]) == 0:
            del used_not_set[suite]

    return used_not_set, set_not_used

# --------------------------------------------------------------------------------------------------
