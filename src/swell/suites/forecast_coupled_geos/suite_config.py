# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum


# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    forecast_coupled_geos = QuestionList(
        list_name="forecast_coupled_geos",
        questions=[
            sq.all_suites,
            qd.start_cycle_point("2021-07-02T12:00:00Z"),
            qd.final_cycle_point("2021-07-03T12:00:00Z"),
            qd.cycle_times([
                "T12",
            ]),
            qd.geos_build_method("use_existing"),
            qd.forecast_duration("P1D"),
        ],
    )

    # --------------------------------------------------------------------------------------------------

    forecast_coupled_geos_tier1 = QuestionList(
        list_name="forecast_coupled_geos_tier1",
        questions=[
            forecast_coupled_geos
        ]
    )

    # --------------------------------------------------------------------------------------------------
