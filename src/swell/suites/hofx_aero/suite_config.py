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

    hofx_aero = QuestionList(
        list_name="hofx_aero",
        questions=[
            sq.common,
            qd.start_cycle_point("2025-11-30T12:00:00Z"),
            qd.final_cycle_point("2025-11-30T12:00:00Z"),
            qd.window_type("3D"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_aero']),
            qd.check_for_obs(False),
        ],

        geos_aero=[
             qd.horizontal_resolution("181"),
             qd.background_experiment("x0054"),
             #qd.background_time_offset("PT3H"),
             qd.geos_x_background_directory(
                 "/discover/nobackup/projects/gmao/dadev/rtodling/archive/544/x0054/rs"
             ),
             # Explicitly set obs location for geos_aero so GetObsNotInR2d2 uses
             # the aerosol MODIS AOD directory instead of platform defaults.
             qd.ioda_locations_not_in_r2d2(
                 "/discover/nobackup/mabdiosk/garage/applications/aod-ext/hx/inputs/obs"
             ),
             qd.npx_proc(4),
             qd.npy_proc(4),
             qd.observations(["mod04_l2a_land"]),
             qd.clean_patterns([]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    hofx_aero_tier1 = QuestionList(
        list_name="hofx_aero_tier1",
        questions=[
            hofx_aero
        ]
    )

# --------------------------------------------------------------------------------------------------
