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

from swell.utilities.question_defaults import QuestionDefaults as qd

# --------------------------------------------------------------------------------------------------


class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    compare_jedi = QuestionList(
        list_name="compare_jedi",
        questions=[
            sq.all_suites,
            qd.comparison_experiment_paths()
        ]
    )

    # --------------------------------------------------------------------------------------------------
