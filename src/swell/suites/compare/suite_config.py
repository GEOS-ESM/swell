# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------

from swell.utilities.swell_questions import QuestionList, WidgetType
import swell.configuration.question_defaults as qd
from swell.suites.base.all_suites import suite_configs
from swell.suites.base.suite_questions import all_suites

# --------------------------------------------------------------------------------------------------

suite_name = 'compare'

compare = QuestionList(
    questions=[
        all_suites,
        qd.comparison_experiment_paths(),
        qd.start_cycle_point(default_value=None, widget_type=WidgetType.STRING),
        qd.final_cycle_point(default_value=None, widget_type=WidgetType.STRING),
        qd.cycle_times(default_value=[None], widget_type=WidgetType.STRING_CHECK_LIST),
        qd.model_components(),
        qd.runahead_limit(),
    ]
)

suite_configs.register(suite_name, 'compare', compare)

# --------------------------------------------------------------------------------------------------

compare_variational_marine = QuestionList(
    questions=[
        compare,
        qd.comparison_log_type('variational'),
        qd.model_components(['geos_marine']),
    ]
)

suite_configs.register(suite_name, 'compare_variational_marine', compare_variational_marine)

# --------------------------------------------------------------------------------------------------

compare_variational_atmosphere = QuestionList(
    questions=[
        compare,
        qd.comparison_log_type('variational'),
        qd.model_components(['geos_atmosphere']),
    ]
)

suite_configs.register(suite_name, 'compare_variational_atmosphere', compare_variational_atmosphere)

# --------------------------------------------------------------------------------------------------

compare_fgat_marine = QuestionList(
    questions=[
        compare,
        qd.comparison_log_type('fgat'),
        qd.model_components(['geos_marine']),
    ]
)

suite_configs.register(suite_name, 'compare_fgat_marine', compare_fgat_marine)

# --------------------------------------------------------------------------------------------------
