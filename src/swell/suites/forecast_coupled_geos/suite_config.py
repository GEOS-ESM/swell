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
from swell.suites.base.suite_attributes import suite_configs

# --------------------------------------------------------------------------------------------------

suite_name = 'forecast_coupled_geos'

forecast_geos_tier1 = QuestionList(
    questions=[
        all_suites,
        qd.start_cycle_point("2021-07-02T12:00:00Z"),
        qd.final_cycle_point("2021-07-03T12:00:00Z"),
        qd.cycle_times([
            "T12",
        ]),
        qd.geos_build_method("use_existing"),
        qd.forecast_duration("P1D"),
    ],
)

suite_configs.register(suite_name, 'forecast_coupled_geos_tier1', forecast_geos_tier1)

# --------------------------------------------------------------------------------------------------

forecast_geos = QuestionList(
    questions=[
        forecast_geos_tier1
    ]
)

suite_configs.register(suite_name, 'forecast_coupled_geos', forecast_geos)

# --------------------------------------------------------------------------------------------------
