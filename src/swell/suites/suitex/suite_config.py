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

    _x1 = QuestionList(
        list_name="x1",
        questions=[
            qd.final_cycle_point("2023-10-10T12:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.horizontal_resolution('91'),
            qd.varx(32)
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _suitex = QuestionList(
        list_name="suitex_t1",
        questions=[
            _x1
        ]
    )

    # --------------------------------------------------------------------------------------------------
