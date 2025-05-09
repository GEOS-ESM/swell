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

    eva_capabilities_tier1 = QuestionList(
        list_name="eva_capabilities",
        questions=[
            sq.marine,
            qd.start_cycle_point("2021-07-02T06:00:00Z"),
            qd.final_cycle_point("2021-07-02T18:00:00Z"),
            qd.model_components(['geos_marine']),
        ],
        geos_marine=[
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
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

    # --------------------------------------------------------------------------------------------------

    eva_capabilities = QuestionList(
        list_name="eva_capabilities",
        questions=[
            eva_capabilities_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
