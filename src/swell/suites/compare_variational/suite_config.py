# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------

from swell.utilities.swell_questions import QuestionContainer, QuestionList, WidgetType
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum

# --------------------------------------------------------------------------------------------------


class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    compare_variational = QuestionList(
        list_name="compare",
        questions=[
            sq.compare,
            qd.start_cycle_point(default_value=None, widget_type=WidgetType.STRING),
            qd.final_cycle_point(default_value=None, widget_type=WidgetType.STRING),
            qd.cycle_times(default_value=[None], widget_type=WidgetType.STRING_CHECK_LIST),
            qd.model_components(),
            qd.runahead_limit(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_variational_marine = QuestionList(
        list_name="compare_variational_marine",
        questions=[
            compare_variational,
            qd.model_components(['geos_marine']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_variational_atmosphere = QuestionList(
        list_name="compare_variational_atmosphere",
        questions=[
            compare_variational,
            qd.model_components(['geos_atmosphere']),
        ]
    )

    # --------------------------------------------------------------------------------------------------
