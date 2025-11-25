"""
Suite for testing R2D2 observation ingestion.

Usage: swell create test_ingest -o test_ingest_obs.yaml
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

    ingest_obs_marine = QuestionList(
        list_name="ingest_obs_marine",
        questions=[
            ingest_obs,
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
            qd.ingest_items([
                {
                    'item_type': 'observation',
                    'source_directory': '',
                    'provider': 'gdas',
                    'observation_types': [
                        {'name': 'adt_cryosat2n', 'file_extension': 'nc4'}
                    ]
                }
            ]),
        ]
    )