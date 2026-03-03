# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
from swell.configuration.question_defaults import QuestionDefaults as qd
from swell.suites.base.suite_questions import common
from swell.suites.base.all_suites import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = 'hofx_cf'

hofx_cf = QuestionList(
    list_name="hofx_cf",
    questions=[
        common,
        qd.start_cycle_point("2023-08-05T18:00:00Z"),
        qd.final_cycle_point("2023-08-05T18:00:00Z"),
        qd.jedi_build_method("use_existing"),
        qd.model_components(['geos_cf']),
        qd.check_for_obs(False)  # don't check empty for empty obs
    ],

    geos_cf=[
    ]
)

suite_configs.register(suite_name, 'hofx_cf', hofx_cf)

# --------------------------------------------------------------------------------------------------

hofx_cf_tier1 = QuestionList(
    list_name="hofx_cf_tier1",
    questions=[
        hofx_cf
    ]
)

suite_configs.register(suite_name, 'hofx_cf_tier1', hofx_cf_tier1)

# --------------------------------------------------------------------------------------------------
