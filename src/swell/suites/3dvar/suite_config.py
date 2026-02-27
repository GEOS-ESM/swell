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

    _3dvar_tier1 = QuestionList(
        list_name="3dvar",
        questions=[
            sq.marine,
            qd.cycling_varbc(),
            qd.start_cycle_point("2021-07-01T12:00:00Z"),
            qd.final_cycle_point("2021-07-01T12:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_marine']),
            qd.parser_options(),
        ],
        geos_marine=[
            qd.cycle_times(['T12']),
            qd.marine_models(['mom6']),
            qd.window_length("P1D"),
            qd.horizontal_resolution("72x36"),
            qd.vertical_resolution("50"),
            qd.total_processors(6),
            qd.obs_experiment("s2s_v1"),
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
            qd.background_time_offset("PT18H"),
            qd.clean_patterns(['*.nc4', '*.txt']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar = QuestionList(
        list_name="3dvar",
        questions=[
            _3dvar_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
