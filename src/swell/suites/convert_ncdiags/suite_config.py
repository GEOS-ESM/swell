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

    convert_ncdiags_tier1 = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            sq.common,
            qd.start_cycle_point("2021-12-12T00:00:00Z"),
            qd.final_cycle_point("2021-12-12T06:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.bundles("REMOVE"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times(['T00', 'T06']),
            qd.clean_patterns([
                "gsi_bcs/*.nc4",
                "gsi_bcs/*.txt",
                "gsi_bcs/*.yaml",
                "gsi_bcs",
                "gsi_ncdiags/*.nc4",
                "gsi_ncdiags/aircraft/*.nc4",
                "gsi_ncdiags/aircraft",
                "gsi_ncdiags"
            ]),
            qd.observations([
                "abi_n16",
                "abi_n18",
                "aircraft",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                "amsua_n18",
                "amsua_n19",
                "atms_n20",
                "atms_n21",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n18",
                "avhrr3_n19",
                "cris-fsr_n20",
                "cris-fsr_n21",
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
                "omieff_aura",
                "ompslpnc_n21",
                "ompslpnc_npp",
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
            qd.path_to_gsi_nc_diags("/discover/nobackup/projects/gmao/advda/SwellTestData/"
                                    "obsolete/ufo_testing/ncdiagv2/%Y%m%d%H"),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    convert_ncdiags = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            convert_ncdiags_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
