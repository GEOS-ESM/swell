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

    _3dvar_cf_tier1 = QuestionList(
        list_name="3dvar_cf",
        questions=[
            sq.common,
            qd.start_cycle_point("2023-08-05T18:00:00Z"),
            qd.final_cycle_point("2023-08-05T18:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_cf']),
            qd.check_for_obs(False)
        ],
        geos_cf=[
            qd.cycle_times(['T18']),
            qd.window_length("PT6H"),
            qd.window_type("3D"),
            qd.horizontal_resolution("c90"),
            qd.npx(91),
            qd.npy(91),
            qd.npx_proc(2),
            qd.npy_proc(2),
            qd.vertical_resolution(72),
            qd.analysis_variables(["volume_mixing_ratio_of_no2"]),
            qd.background_experiment("swell_test"),
            qd.background_time_offset("PT9H"),
            qd.observations([
                "tempo_no2_tropo",
                "tropomi_s5p_no2_tropo",
            ]),
            qd.clean_patterns(['*.nc4', '*.txt', 'logfile.*.out']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cf = QuestionList(
        list_name="3dvar_cf",
        questions=[
            _3dvar_cf_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
