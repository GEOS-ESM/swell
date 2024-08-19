import tempfile
import yaml
import random

from pathlib import Path
from datetime import datetime
from importlib import resources

from swell.deployment.create_experiment import create_experiment_directory
from swell.deployment.launch_experiment import launch_experiment
from swell.utilities.dictionary import update_dict


def run_suite(suite: str):
    # Add a random int to the experiment_id to mitigate errors from workflows
    # created at (roughly) the same time.
    ii = random.randint(0, 99)
    experiment_id = f"t{datetime.now().strftime('%Y%jT%H%M')}r{ii:02d}{suite}"

    # Get test directory from `~/.swell/swell-test.yml`
    test_config = {
        "test_root": Path(tempfile.TemporaryDirectory().name)
    }
    yamlfile = Path("~/.swell/swell-test.yaml").expanduser()
    try:
        with open(yamlfile, "r") as f:
            test_user_config = yaml.safe_load(f)
        print(f"Updating test defaults with user config from {yamlfile}.")
        test_config = {**test_config, **test_user_config}
    except FileNotFoundError:
        pass
    except Exception as err:
        raise err

    testdir = Path(test_config["test_root"]).expanduser()
    testdir.mkdir(exist_ok=True, parents=True)

    print(f"Testing suite: {suite}")
    print(f"Test directory: {testdir}")
    print(f"Experiment ID: {experiment_id}")

    suite_overrides_file = (resources.files("swell") /
                            "test" /
                            "suite_tests" /
                            f"{suite}-tier1.yaml")
    print(f"Reading suite overrides from: {suite_overrides_file}")
    with suite_overrides_file.open("r") as f:
        suite_overrides = yaml.safe_load(f)

    override = {
        "experiment_id": experiment_id,
        "experiment_root": str(testdir),
        **suite_overrides
    }
    if "override" in test_config:
        override = update_dict(override, test_config["override"])

    try:
        k = (override["models"]  # type: ignore
             ["geos_atmosphere"]
             ["observing_system_records_mksi_path"])
        if k is None:
            raise KeyError("observing_system_records_mksi_path is set but is None")
    except KeyError:
        print(
            "WARNING: 'mksi_path' test config is unset. " +
            "By default, Swell will try to clone GEOS_mksi from GitHub, " +
            "which will fail on compute nodes with no internet access."
        )

    experiment_dir = testdir / experiment_id
    experiment_dir.mkdir(parents=True, exist_ok=True)

    override_yml = experiment_dir / "override.yaml"
    with open(override_yml, "w") as f:
        yaml.dump(override, f)

    create_experiment_directory(
        suite, "defaults", "nccs_discover_sles15",
        str(override_yml), False, None
    )

    # TODO: Check some stuff about the experiment directory

    suite_path = str(experiment_dir / f"{experiment_id}-suite")
    log_path = str(experiment_dir / "log")

    launch_experiment(suite_path, True, log_path)

    # TODO: Check the outputs


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Swell suite tests")
    parser.add_argument("suites", nargs="+",
                        help="Suite(s) to run (or `all` to run all suites)")

    args = parser.parse_args()
    if args.suites == ["all"]:
        suites = ("3dvar", "hofx", "ufo_testing")
    else:
        suites = args.suites

    for suite in suites:
        run_suite(suite)
