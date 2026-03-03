# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.swell_questions import QuestionList
import swell.configuration.question_defaults as qd
from swell.suites.base.all_suites import suite_configs

# --------------------------------------------------------------------------------------------------
# Shared groups of questions across suites
# --------------------------------------------------------------------------------------------------

all_suites = QuestionList(
    questions=[
        qd.experiment_id(),
        qd.experiment_root(),
        qd.pause_on_tasks(),
        qd.task_email_parameters(),
        qd.email_address()
    ]
)

suite_configs.register('AllSuites', 'AllSuites', all_suites)

# --------------------------------------------------------------------------------------------------

common = QuestionList(
    questions=[
        all_suites,
        qd.cycle_times(),
        qd.start_cycle_point(),
        qd.final_cycle_point(),
        qd.model_components(),
        qd.runahead_limit()
    ]
)

# --------------------------------------------------------------------------------------------------

marine = QuestionList(
    questions=[
        common,
        qd.marine_models()
    ]
)

# --------------------------------------------------------------------------------------------------

compare = QuestionList(
    questions=[
        all_suites,
        qd.comparison_experiment_paths()
    ]
)

# --------------------------------------------------------------------------------------------------

task_minimum = QuestionList(
    questions=[
        qd.experiment_id(),
        qd.experiment_root(),
        qd.comparison_experiment_paths(),
        qd.model_components(),
        qd.marine_models(),
        qd.use_cycle_dir(),
    ]
)

suite_configs.register('TaskMinimum', 'TaskMinimum', task_minimum)

# --------------------------------------------------------------------------------------------------
