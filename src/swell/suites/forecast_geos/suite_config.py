# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

# --------------------------------------------------------------------------------------------------

forecast_geos_tier1 = QuestionList(
    list_name="forecast_geos",
    questions=[
        sq.all_suites,
        qd.cycle_times(),
        qd.final_cycle_point(),
        qd.start_cycle_point()
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

# --------------------------------------------------------------------------------------------------

forecast_geos = QuestionList(
    list_name="forecast_geos",
    questions=[
        forecast_geos_tier1
    ]
)

# --------------------------------------------------------------------------------------------------
