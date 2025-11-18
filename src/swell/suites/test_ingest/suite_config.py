"""
Suite for testing R2D2 observation ingestion.

Usage: swell create test_ingest -o test_ingest_obs.yaml
"""

from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq
from enum import Enum


class SuiteConfig(QuestionContainer, Enum):

    _test_ingest = QuestionList(
        list_name="test_ingest",
        questions=[
            sq.common,
        ],
        geos_atmosphere=[
            qd.window_length("PT61111111H"),
            qd.window_offset("PT3H"),
            qd.ingest_items([]),           # Configure via YAML override
            # qd.ingest_items([
            #     {
            #         'item_type': 'observation',
            #         'source_directory': '/discover/nobackup/projects/gmao/obs/archive/',
            #         'provider': 'gdas',
            #         'observation_types': [
            #             {
            #                 'name': 'aircraft_temperature',
            #                 'file_extension': 'nc4'
            #             }
            #         ],
            #         'create_empty_if_missing': True
            #     }
            # ])
        ]
    )
