import tempfile
import yaml
# import shutil

from pathlib import Path
from datetime import datetime

from swell.deployment.create_experiment import create_experiment_directory
from swell.deployment.launch_experiment import launch_experiment

def run_suite(suite: str):
    print(f"Suite: {suite}")
    experiment_id = f"t{datetime.now().strftime('%Y%jT%H%M')}{suite}"

    # with tempfile.TemporaryDirectory() as rundir:
    rundir = tempfile.TemporaryDirectory()

    testdir = Path(rundir.name)

    print(f"Storing test results in {testdir}")

    override = {
        "experiment_id": experiment_id,
        "experiment_root": str(testdir)
    }
    override_yml = testdir / "override.yaml"
    with open(override_yml, "w") as f:
        yaml.dump(override, f)

    # Setup
    # cylc_run_path = Path.home() / "cylc-run" / f"{experiment_id}-suite"
    # try:
    #     shutil.rmtree(cylc_run_path)
    # except FileNotFoundError:
    #     pass

    create_experiment_directory(suite, "defaults", "nccs_discover_sles15", str(override_yml), False, None)

    # TODO: Check some stuff about the experiment directory

    suite_path = str(testdir / experiment_id / f"{experiment_id}-suite")
    log_path = str(testdir / "log")

    launch_experiment(suite_path, True, log_path)

    # TODO: Check the outputs

def suite_tests():
    for suite in ("3dvar", "hofx", "ufo_testing"):
        run_suite(suite)
