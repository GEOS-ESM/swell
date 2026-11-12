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

    hofx_cf = QuestionList(
        list_name="hofx_cf",
        questions=[
            sq.common,
            qd.swell_static_files(
                "/discover/nobackup/projects/gmao/geos_cf_dev/GEOS-CF3-dev/SwellStaticFiles"
                ),
            qd.start_cycle_point("2023-08-05T18:00:00Z"),
            qd.final_cycle_point("2023-08-05T18:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_cf']),
            qd.check_for_obs(False)  # don't check empty for empty obs
        ],

        geos_cf=[
            qd.window_type("3D"),
            qd.window_length("PT6H"),
        ]
    )

    hofx_cf_tier1 = QuestionList(
        list_name="hofx_cf_tier1",
        questions=[
             hofx_cf
        ]
    )

    # HofX of WOUDC ozonesondes (evaluation only: `monitoring only: true` in
    # observations/ozonesonde.yaml). The sondes must first be ingested into R2D2
    # with the ingest_obs_cf suite for the same cycles; most windows have no
    # sonde, which GetObservations and the HofX handle as empty obs.
    hofx_cf_ozonesonde = QuestionList(
        list_name="hofx_cf_ozonesonde",
        questions=[
            hofx_cf,
            qd.start_cycle_point("2025-03-01T12:00:00Z"),
            qd.final_cycle_point("2025-03-01T12:00:00Z"),
        ],
        geos_cf=[
            qd.observations(['ozonesonde']),
        ]
    )
