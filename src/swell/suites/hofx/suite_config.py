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

    hofx_tier1 = QuestionList(
        list_name="hofx",
        questions=[
            sq.marine,
            qd.window_type(),
            qd.jedi_build_method("use_existing"),
            qd.save_geovals(True),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.horizontal_resolution("91"),
            qd.geos_x_background_directory("/discover/nobackup/projects/gmao/dadev/"
                                           "rtodling/archive/Restarts/JEDI/541x"),
            qd.npx_proc(2),
            qd.npy_proc(2),
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
                "ssmis_f17",
                "tcp"
            ]),
            qd.clean_patterns([]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    hofx = QuestionList(
        list_name="hofx",
        questions=[
            hofx_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
