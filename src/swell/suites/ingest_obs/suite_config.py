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
            qd.download_convert_pipeline(False)
        ],
    )
    # This name should be unique and not conflict with other suites
    # (otherwise it might get overwritten)
    ingest_obs_marine = QuestionList(
        list_name="ingest_obs_marine",
        questions=[
            ingest_obs,
            sq.marine,
            qd.start_cycle_point("2023-07-02T06:00:00Z"),
            qd.final_cycle_point("2023-07-03T06:00:00Z"),
            qd.model_components(['geos_marine']),
            qd.runahead_limit("P5"),
        ],
        geos_marine=[
            qd.window_length("PT6H"),
            qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
            qd.obs_to_ingest(['adt_cryosat2n']),  # List of obs names
            qd.dry_run(True),
        ]
    )

    ingest_obs_cf = QuestionList(
        list_name="ingest_obs_cf",
        questions=[
            ingest_obs,
            qd.start_cycle_point("2023-08-10T00:00:00Z"),
            qd.final_cycle_point("2023-08-11T00:00:00Z"),
            qd.model_components(['geos_cf']),
            qd.runahead_limit("P5"),
            qd.download_convert_pipeline(True),
            qd.jedi_build_method("use_existing"),  # For pyioda
        ],
        geos_cf=[
            qd.window_length("PT6H"),
            qd.obs_to_download(['omps_o3_nm_total']),
            qd.obs_to_ingest(['omps_o3_nm_total']),
            qd.converter_path(
                "/discover/nobackup/projects/jcsda/s2127/maryamao/"
                "jedi-bundle/build-intel-1.9/bin/"
            ),
            qd.dry_run(False),
        ]
    )
