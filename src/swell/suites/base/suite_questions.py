# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from enum import Enum

from swell.utilities.swell_questions import QuestionList, QuestionContainer
from swell.utilities.question_defaults import QuestionDefaults as qd


# --------------------------------------------------------------------------------------------------

class SuiteQuestions(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------
    # Shared groups of questions across suites
    # --------------------------------------------------------------------------------------------------

    all_suites = QuestionList(
        list_name="all_suites",
        questions=[
            qd.experiment_id(),
            qd.experiment_root(),
            qd.pause_on_tasks(),
            qd.task_email_parameters(),
            qd.email_address()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    common = QuestionList(
        list_name="common",
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
        list_name="marine",
        questions=[
            common,
            qd.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare = QuestionList(
        list_name="compare",
        questions=[
            all_suites,
            qd.comparison_experiment_paths()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    task_minimum = QuestionList(
        list_name="task_minimum",
        questions=[
            qd.experiment_id(),
            qd.experiment_root(),
            qd.comparison_experiment_paths(),
            qd.model_components(),
            qd.marine_models(),
            qd.use_cycle_dir(),
        ]
    )

    # --------------------------------------------------------------------------------------------------
