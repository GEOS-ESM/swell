"""
Suite for testing R2D2 observation ingestion.

Usage: swell create ingest_obs_marine

"""

# --------------------------------------------------------------------------------------------------

from swell.utilities.swell_questions import QuestionList
from swell.configuration.question_defaults import QuestionDefaults as qd
from swell.suites.base.suite_questions import common, marine
from swell.suites.base.all_suites import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = 'ingest_obs'

ingest_obs = QuestionList(
    list_name="ingest_obs",
    questions=[
        common,
    ],
)

suite_configs.register(suite_name, 'ingest_obs', ingest_obs)

# --------------------------------------------------------------------------------------------------

# This name should be unique and not conflict with other suites
# (otherwise it might get overwritten)
ingest_obs_marine = QuestionList(
    list_name="ingest_obs_marine",
    questions=[
        ingest_obs,
        marine,
        qd.start_cycle_point("2021-07-02T06:00:00Z"),
        qd.final_cycle_point("2021-07-03T06:00:00Z"),
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

suite_configs.register(suite_name, 'ingest_obs_marine', ingest_obs_marine)

# --------------------------------------------------------------------------------------------------