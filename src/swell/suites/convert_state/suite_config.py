# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Suite configuration for the convert_state suite.
#  Converts GEOS atmospheric background files from one cubed-sphere resolution to a
#  user-specified target resolution using fv3jedi_convertstate.x.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum


# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    _convert_state_tier1 = QuestionList(
        list_name="convert_state",
        questions=[
            sq.common,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T00:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times(["T00"]),

            # Source GEOS experiment providing the bkgcrst tar archive
            qd.background_experiment("x0050"),
            qd.background_time_offset("PT3H"),
            qd.geos_x_background_directory(
                "/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x"
            ),

            # Input (source) resolution
            qd.horizontal_resolution("91"),
            qd.vertical_resolution("72"),
            qd.npx_proc(2),
            qd.npy_proc(2),

            # Target (output) resolution
            qd.target_background_experiment("x0054"),
            qd.target_horizontal_resolution("13"),

            # Background files to convert: hourly offsets spanning the 6-hour DA window
            qd.background_window_times([
                "-PT3H", "-PT2H", "-PT1H", "PT0H", "PT1H", "PT2H", "PT3H"
            ]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _convert_state = QuestionList(
        list_name="convert_state",
        questions=[
            _convert_state_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
