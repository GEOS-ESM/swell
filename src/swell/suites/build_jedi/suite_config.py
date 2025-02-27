# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum


# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    build_jedi_base = QuestionList(
        list_name="build_jedi",
        questions=[
            sq.all_suites
        ]
    )

    # --------------------------------------------------------------------------------------------------

    build_jedi = QuestionList(
        list_name="build_jedi",
        questions=[
            build_jedi_base
        ]
    )

    # --------------------------------------------------------------------------------------------------
