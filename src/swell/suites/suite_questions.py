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
            qd.experiment_root()
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
            qd.runahead_limit(),
            qd.r2d2_experiment_id(),
            qd.r2d2_server(),
            qd.r2d2_datastore(),
            qd.skip_r2d2(),
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
