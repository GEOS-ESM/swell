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
from swell.suites.base.suite_questions import SuiteQuestions as sq

from enum import Enum


# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    eva_capabilities = QuestionList(
        list_name="eva_capabilities",
        questions=[
            sq.marine,
            qd.start_cycle_point("2021-07-02T06:00:00Z"),
            qd.final_cycle_point("2021-07-03T06:00:00Z"),
            qd.model_components(['geos_marine']),
        ],
        geos_marine=[
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.window_length("PT6H"),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "insitu_profile_argo",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_gmi_l3u",
                "sst_viirs_n20_l3u",
                "temp_profile_xbt"
            ]),
            qd.ncdiag_experiments(['fgat_jra55_01']),
            qd.clean_patterns(['*.nc4', '*.txt']),
        ]
    )

    eva_capabilities_atmosphere = QuestionList(
        list_name="eva_capabilities_atmosphere",
        questions=[
            eva_capabilities,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.observations([
                # "aircraft_temperature",
                # "aircraft_wind",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                # "amsua_n18",
                # "amsua_n19",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                # "avhrr3_n18",
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
                # "mls55_aura",
                # "omi_aura",
                # "ompsnm_npp",
                # "pibal",
                "satwind",
                "scatwind",
                "sfcship",
                "sfc",
                "sondes",
                "ssmis_f17"
            ]),
            qd.ncdiag_experiments(['x0050_fgat']),
            qd.clean_patterns(['*.txt', '*.csv']),
        ]
    )

    # --------------------------------------------------------------------------------------------------
