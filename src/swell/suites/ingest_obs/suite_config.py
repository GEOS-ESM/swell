"""
Suite for testing R2D2 observation ingestion.

Usage: swell create ingest_obs_marine

"""

# --------------------------------------------------------------------------------------------------

from swell.utilities.swell_questions import QuestionList
import swell.configuration.question_defaults as qd
from swell.suites.base.suite_questions import common, marine
from swell.suites.base.suite_attributes import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = 'ingest_obs'

ingest_obs = QuestionList(
    questions=[
        common,
        qd.download_convert_pipeline(False)
    ],
)

suite_configs.register(suite_name, 'ingest_obs', ingest_obs)

# --------------------------------------------------------------------------------------------------

# This name should be unique and not conflict with other suites
# (otherwise it might get overwritten)
ingest_obs_marine = QuestionList(
    questions=[
        ingest_obs,
        marine,
        qd.start_cycle_point("2023-07-01T00:00:00Z"),
        qd.final_cycle_point("2023-07-02T12:00:00Z"),
        qd.model_components(['geos_marine']),
        qd.runahead_limit("P5"),
    ],
    geos_marine=[
        qd.window_length("PT6H"),
        qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
        qd.obs_to_ingest(['adt_cryosat2n',
                          'adt_sentinel6a',
                          'adt_swot_nadir',
                          'sss_smos',
                          ]),  # List of obs names
        qd.dry_run(True),
    ]
)

suite_configs.register(suite_name, 'ingest_obs_marine', ingest_obs_marine)

# --------------------------------------------------------------------------------------------------

ingest_obs_cf = QuestionList(
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
        qd.obs_to_download(['tempo_no2_tropo']),
        qd.obs_to_ingest(['tempo_no2_tropo']),
        qd.converter_path(
            "/discover/nobackup/projects/jcsda/s2127/maryamao/"
            "jedi-bundle/build-intel-1.9/bin/"
        ),
        qd.dry_run(False),
    ]
)

suite_configs.register(suite_name, 'ingest_obs_cf', ingest_obs_cf)

# --------------------------------------------------------------------------------------------------
