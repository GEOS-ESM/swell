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

    convert_bufr = QuestionList(
        list_name="convert_bufr",
        questions=[
            sq.common,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.clean_patterns([
                "gsi_bcs/*.nc4",
                "gsi_bcs/*.txt",
            ]),
            qd.bufr_obs_classes([
               "ncep_1bamua_bufr",
               "ncep_mtiasi_bufr",
            ]),
        ]
    )


