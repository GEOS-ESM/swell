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

    _3dvar_atmos_base = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            sq.common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_atmos_tier1 = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            _3dvar_atmos_base,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18"
            ]),
            qd.geos_x_background_directory("/discover/nobackup/projects/gmao/"
                                           "dadev/rtodling/archive/Restarts/JEDI/541x"),
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
            qd.window_type("3D"),
            qd.horizontal_resolution("91"),
            qd.vertical_resolution("72"),
            qd.observations([
                "aircraft_temperature",
                "aircraft_wind",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                "amsua_n18",
                "amsua_n19",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n18",
                "avhrr3_n19",
                "cris-fsr_n20",
                "cris-fsr_npp",
                "gmi_gpm",
                "gps",
                "iasi_metop-b",
                "iasi_metop-c",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "mls55_aura",
                "omi_aura",
                "ompsnm_npp",
                "pibal",
                "satwind",
                "scatwind",
                "sfcship",
                "sfc",
                "sondes",
                "ssmis_f17"
            ]),
            qd.clean_patterns(['*.txt', '*.csv']),
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
