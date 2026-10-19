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

    _3dvar_atmos_tier1 = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            sq.common,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.runahead_limit("P1"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times([
                "T00",
            ]),
            qd.background_experiment("x0054"),
            qd.geos_x_background_directory("/discover/nobackup/projects/gmao/"
                                           "dadev/rtodling/archive/Restarts/5_44/c90"),
            qd.window_length("PT6H"),
            qd.window_type("3D"),
            qd.horizontal_resolution("91"),
            qd.gsibec_nlats("91"),
            qd.gsibec_nlons("144"),
            qd.vertical_resolution("72"),
            qd.observations([
                "abi_g16",
                # "tcp"
            ]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_atmos = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            _3dvar_atmos_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
