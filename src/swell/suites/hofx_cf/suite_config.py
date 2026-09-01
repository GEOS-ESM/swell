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

    hofx_cf = QuestionList(
        list_name="hofx_cf",
        questions=[
            sq.common,
            qd.swell_static_files(
                "/discover/nobackup/projects/gmao/geos_cf_dev/GEOS-CF3-dev/SwellStaticFiles"
                ),
            qd.start_cycle_point("2023-08-05T18:00:00Z"),
            qd.final_cycle_point("2023-08-05T18:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_cf']),
            qd.check_for_obs(False)  # don't check empty for empty obs
        ],

        geos_cf=[
            # 3D uses a single background at the window centre; 4D propagates the window with the
            # PSEUDO model, reading one background per background_frequency step.
            qd.window_type("3D"),
            qd.window_length("PT6H"),
            qd.background_frequency("PT3H"),
            qd.jedi_forecast_model("pseudo_model"),
        ]
    )

    hofx_cf_tier1 = QuestionList(
        list_name="hofx_cf_tier1",
        questions=[
             hofx_cf
        ]
    )
