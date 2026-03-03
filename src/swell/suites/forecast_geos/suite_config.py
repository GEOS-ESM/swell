# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
import swell.configuration.question_defaults as qd
from swell.suites.base.suite_questions import all_suites
from swell.suites.base.all_suites import suite_configs

# --------------------------------------------------------------------------------------------------

suite_name = 'forecast_geos'

forecast_geos_tier1 = QuestionList(
    questions=[
        all_suites,
        qd.cycle_times(),
        qd.final_cycle_point(),
        qd.start_cycle_point(),
        qd.start_cycle_point("2021-06-20T00:00:00Z"),
        qd.final_cycle_point("2021-06-21T00:00:00Z"),
        qd.cycle_times([
            "T00",
            "T06",
            "T12",
            "T18"
        ]),
        qd.geos_build_method("use_existing"),
        qd.forecast_duration("PT6H"),
    ],
)

suite_configs.register(suite_name, 'forecast_geos_tier1', forecast_geos_tier1)

# --------------------------------------------------------------------------------------------------

forecast_geos = QuestionList(
    questions=[
        forecast_geos_tier1
    ]
)

suite_configs.register(suite_name, 'forecast_geos', forecast_geos)

# --------------------------------------------------------------------------------------------------
