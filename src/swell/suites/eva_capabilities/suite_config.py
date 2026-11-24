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

    eva_capabilities = QuestionList(
        list_name="eva_capabilities",
        questions=[
            sq.marine,
            qd.start_cycle_point("2023-01-02T12:00:00Z"),
            qd.final_cycle_point("2023-08-01T12:00:00Z"),
            qd.model_components(['geos_marine']),
            qd.runahead_limit("P6"),
        ],
        geos_marine=[
            qd.cycle_times(['T12']),
            qd.window_length("P1D"),
            # qd.background_time_offset()
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3n",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "adt_sentinel6a",
                "adt_swot_nadir",
                "insitu_profile_argo",
                "insitu_profile_ctd",
                "insitu_profile_pirata",
                "insitu_profile_tao",
                "icec_amsr2_north",
                "icec_amsr2_south",
                #"insitu_profile_rama",
                "sss_smos",
                "sss_smapv5",
                "sst_avhrrf_mb_l3u",
                "sst_avhrrf_mc_l3u",
                "sst_viirs_n20_l3u",
                "sst_viirs_npp_l3u",
            ]),
            qd.ncdiag_experiments(['fgat_dataatm_1day_02']),
            qd.clean_patterns(['*.nc4', '*.txt']),
        ]
    )


    eva_capabilities_5day = QuestionList(
        list_name="eva_capabilities_5day",
        questions=[eva_capabilities,
            qd.start_cycle_point("2023-01-08T12:00:00Z"),
            qd.final_cycle_point("2023-02-22T12:00:00Z"),
                   ],
        geos_marine=[
            qd.cycle_times(['P5D']),
            qd.window_length("P5D"),
            qd.ncdiag_experiments(['swell-3dfgat_marine_cycle-e92e3746']),
            qd.marine_models(["mom6"])
        ]
    )
    # --------------------------------------------------------------------------------------------------
