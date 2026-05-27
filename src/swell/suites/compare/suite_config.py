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

    compare = QuestionList(
        list_name="compare",
        questions=[
            sq.all_suites,
            qd.comparison_experiment_paths(),
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
            compare,
            qd.comparison_log_type('variational'),
            qd.model_components(['geos_marine']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_variational_atmosphere = QuestionList(
        list_name="compare_variational_atmosphere",
        questions=[
            compare,
            qd.comparison_log_type('variational'),
            qd.model_components(['geos_atmosphere']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_variational_cf = QuestionList(
        list_name="compare_variational_cf",
        questions=[
            compare,
            qd.comparison_log_type('variational'),
            qd.model_components(['geos_cf']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_fgat_marine = QuestionList(
        list_name="compare_fgat_marine",
        questions=[
            compare,
            qd.comparison_log_type('fgat'),
            qd.model_components(['geos_marine']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_hofx = QuestionList(
        list_name="compare_hofx",
        questions=[
            compare,
            qd.comparison_log_type('hofx'),
            qd.model_components(['geos_atmosphere']),
            qd.observations([])
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_hofx_cf = QuestionList(
        list_name="compare_hofx_cf",
        questions=[
            compare,
            qd.comparison_log_type('hofx'),
            qd.observations([]),
            qd.model_components(['geos_cf']),
        ]
    )

    # --------------------------------------------------------------------------------------------------
