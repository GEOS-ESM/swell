"""
Suite for R2D2 background/forecast ingestion.

Usage: swell create ingest_background_marine
"""

from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq
from enum import Enum


class SuiteConfig(QuestionContainer, Enum):

    ingest_background = QuestionList(
        list_name="ingest_background",
        questions=[
            sq.common,
        ],
    )

    ingest_background_marine = QuestionList(
        list_name="ingest_background_marine",
        questions=[
            ingest_background,
            sq.marine,
            qd.start_cycle_point("2021-07-02T06:00:00Z"),
            qd.final_cycle_point("2021-07-03T06:00:00Z"),
            qd.model_components(['geos_marine']),
            qd.runahead_limit("P5"),
        ],
        geos_marine=[
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.backgrounds_to_ingest(['geos_restart']),  # List of background names
            qd.dry_run(True),
        ]
    )

