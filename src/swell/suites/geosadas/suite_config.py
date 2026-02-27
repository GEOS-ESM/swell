# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.configuration.question_defaults import QuestionDefaults as qd
from swell.suites.base.suite_questions import SuiteQuestions as sq

from enum import Enum


# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    geosadas_tier1 = QuestionList(
        list_name="geosadas",
        questions=[
            sq.all_suites,
            qd.jedi_build_method("use_existing"),
            qd.bundles("REMOVE"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.horizontal_resolution("13"),
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
                "iasi_metop-b",
                "iasi_metop-c",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "mls55_aura",
                "omi_aura",
                "ompsnm_npp",
                "satwind",
                "scatwind",
                "ssmis_f17"
            ]),
            qd.produce_geovals(False),
            qd.window_type("3D"),
            qd.gradient_norm_reduction("1e-6"),
            qd.number_of_iterations([5]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    geosadas = QuestionList(
        list_name="geosadas",
        questions=[
            geosadas_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
