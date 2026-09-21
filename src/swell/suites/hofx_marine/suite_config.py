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

    hofx_marine = QuestionList(
        list_name="hofx_marine",
        questions=[
            sq.common,
            qd.start_cycle_point("2023-01-03T12:00:00Z"),
            qd.final_cycle_point("2023-01-04T12:00:00Z"),
            qd.window_type("4D"),
            qd.model_components(['geos_marine']),
        ],
        geos_marine=[
            qd.horizontal_resolution("1440x1080"),
            qd.vertical_resolution("75"),
            qd.window_length("P1D"),
            qd.background_time_offset("P1DT12H"),
            qd.background_frequency("PT6H"),
            qd.cycle_times([
                "T12",
            ]),
            qd.marine_models(["mom6"]),
            qd.background_experiment(["swell-3dfgat_marine_cycle-ef812e05"]),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3n",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "adt_sentinel6a",
                "insitu_profile_argo",
                "insitu_profile_ctd",
                "insitu_profile_pirata",
                "insitu_profile_rama",
                "insitu_profile_tao",
                "sss_smos",
                "sss_smapv5",
                "sst_avhrrf_mb_l3u",
                "sst_avhrrf_mc_l3u",
                "sst_viirs_n20_l3u",
                "sst_viirs_npp_l3u",
            ]),
            qd.total_processors("720"),
            qd.clean_patterns([]),
        ]
    )

    # --------------------------------------------------------------------------------------------------
