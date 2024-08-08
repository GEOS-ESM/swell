import tempfile
import yaml

from pathlib import Path
from datetime import datetime

from swell.deployment.create_experiment import create_experiment_directory
from swell.deployment.launch_experiment import launch_experiment

def run_suite(suite: str):
    experiment_id = f"t{datetime.now().strftime('%Y%jT%H%M')}{suite}"

    # Get test directory from `~/.swell/swell-test.yml`
    yamlfile = Path("~/.swell/swell-test.yaml").expanduser()
    try:
        with open(yamlfile, "r") as f:
            test_config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"User test config ({yamlfile}) found. Using defaults.")
        test_config = {"test_root": Path(tempfile.TemporaryDirectory().name)}
    except Exception as err:
        raise(err)

    testdir = Path(test_config["test_root"]).expanduser()
    testdir.mkdir(exist_ok=True, parents=True)

    print(f"Testing suite: {suite}")
    print(f"Test directory: {testdir}")
    print(f"Experiment ID: {experiment_id}")

    override = {
        "experiment_id": experiment_id,
        "experiment_root": str(testdir)
    }

    experiment_dir = testdir / experiment_id
    experiment_dir.mkdir(parents=True, exist_ok=True)

    override_yml = experiment_dir / "override.yaml"
    with open(override_yml, "w") as f:
        yaml.dump(override, f)

    create_experiment_directory(suite, "defaults", "nccs_discover_sles15", str(override_yml), False, None)

    # TODO: Check some stuff about the experiment directory

    suite_path = str(experiment_dir / f"{experiment_id}-suite")
    log_path = str(experiment_dir / "log")

    launch_experiment(suite_path, True, log_path)

    # TODO: Check the outputs

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description = "Swell suite tests")
    parser.add_argument("suites", nargs="+",
                        help="Suite(s) to run (or `all` to run all suites)")

    args = parser.parse_args()
    if args.suites == ["all"]:
        suites = ("3dvar", "hofx", "ufo_testing")
    else:
        suites = args.suites

    for suite in suites:
        run_suite(suite)
