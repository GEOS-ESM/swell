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

    _3dvar_cycle_base = QuestionList(
        list_name="3dvar_cycle",
        questions=[
            sq.marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cycle_tier1 = QuestionList(
        list_name="3dvar_cycle",
        questions=[
            _3dvar_cycle_base,
            qd.start_cycle_point("2021-07-02T06:00:00Z"),
            qd.final_cycle_point("2021-07-02T12:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.geos_build_method("use_existing"),
            qd.model_components(['geos_marine']),
        ],
        geos_marine=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18",
            ]),
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
            qd.horizontal_resolution("72x36"),
            qd.vertical_resolution("50"),
            qd.total_processors(6),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "insitu_profile_argo",
                "sst_ostia",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_gmi_l3u",
                "sst_viirs_n20_l3u",
                "temp_profile_xbt"
            ]),
            qd.number_of_iterations([10]),
            qd.obs_provider(['odas', 'gdas_marine']),
            qd.mom6_iau(True),
            qd.marine_models(['mom6']),
            qd.analysis_forecast_window_offset("-PT3H"),
            qd.background_time_offset("PT9H"),
            qd.clean_patterns([
                "*.nc4",
                "*.txt",
                "*.rc",
                "*.bin"
            ]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cycle = QuestionList(
        list_name="3dvar_cycle",
        questions=[
            _3dvar_cycle_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
