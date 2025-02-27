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

    convert_ncdiags_base = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            sq.common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    convert_ncdiags_tier1 = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            convert_ncdiags_base,
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
            qd.path_to_gsi_nc_diags("/discover/nobackup/projects/gmao/advda/SwellTestData/"
                                    "ufo_testing/ncdiagv2/%Y%m%d%H"),
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

