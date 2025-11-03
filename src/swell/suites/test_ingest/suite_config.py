from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq
from enum import Enum


class SuiteConfig(QuestionContainer, Enum):

    _test_ingest = QuestionList(
        list_name="test_ingest",
        questions=[
            sq.common,
            qd.start_cycle_point("2023-10-09T15:00:00Z"),
            qd.final_cycle_point("2023-10-09T15:00:00Z"),
            qd.runahead_limit("P1"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times(["T15"]),
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
            qd.ingest_items([
                {
                    'item_type': 'observation',
                    'source_directory': '/discover/nobackup/projects/gmao/obs/archive/',
                    'provider': 'gdas',
                    'observation_types': [
                        {
                            'name': 'aircraft_temperature',
                            'file_extension': 'nc4'
                        }
                    ],
                    'create_empty_if_missing': True
                }
            ])
        ]
    )

