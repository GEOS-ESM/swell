"""
Suite for testing R2D2 observation ingestion.

Usage: swell create ingest_obs_marine

"""

from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq
from enum import Enum


class SuiteConfig(QuestionContainer, Enum):

    ingest_obs = QuestionList(
        list_name="ingest_obs",
        questions=[
            sq.common,
        ],
    )

    ingest_obs_atmosphere = QuestionList(
        list_name="ingest_obs_atmosphere",
        questions=[
            ingest_obs,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.model_components(['geos_atmosphere']),
            qd.runahead_limit("P5"),
            qd.jedi_build_method("use_existing"),
            qd.bufr_pipeline(True),
        ],
        geos_atmosphere=[
            qd.window_length("PT6H"),
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.bufr_obs_classes(['ncep_1bamua_bufr', 'ncep_mtiasi_bufr']),
            qd.obs_to_ingest(['ncep_1bamua_bufr', 'ncep_mtiasi_bufr']),
            qd.dry_run(True),
        ]
    )

    # This name should be unique and not conflict with other suites
    # (otherwise it might get overwritten)
    ingest_obs_marine = QuestionList(
        list_name="ingest_obs_marine",
        questions=[
            ingest_obs,
            sq.marine,
            qd.start_cycle_point("2021-07-02T06:00:00Z"),
            qd.final_cycle_point("2021-07-03T06:00:00Z"),
            qd.model_components(['geos_marine']),
            qd.runahead_limit("P5"),
            qd.bufr_pipeline(False),
        ],
        geos_marine=[
            qd.window_length("PT6H"),
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.obs_to_ingest(['adt_cryosat2n']),
            qd.dry_run(True),
        ]
    )
