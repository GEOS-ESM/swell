import tempfile
from ruamel.yaml import YAML
import random
import os

from pathlib import Path
from datetime import datetime
from importlib import resources
from enum import Enum

from swell.deployment.create_experiment import create_experiment_directory
from swell.deployment.launch_experiment import launch_experiment
from swell.utilities.dictionary import update_dict


class TestSuite(Enum):
    TIER1 = "tier1"
    TIER2 = "tier2"


def build_jedi_for_tier2(test_dir: str, experiment_id_root: str, platform: str, test_config: dict):
    suite_overrides_file = (resources.files("swell") /
                            "test" /
                            "suite_tests" /
                            "build_jedi-tier1.yaml")

    with suite_overrides_file.open("r") as f:
        yaml = YAML(typ='safe')
        suite_overrides = yaml.load(f)

    experiment_id = experiment_id_root + "build_jedi"

    override = {
        "experiment_id": experiment_id,
        "experiment_root": str(test_dir),
        **suite_overrides
    }

    if "override" in test_config:
        override = update_dict(override, test_config['override'])

    experiment_dir = os.path.join(test_dir, experiment_id)
    os.makedirs(experiment_dir, exist_ok=True)
    override_yml = os.path.join(experiment_dir, "override.yaml")

    with open(override_yml, "w") as f:
        yaml.dump(override, f)

    create_experiment_directory(
        "build_jedi", "defaults", platform,
        str(override_yml), False, None, False
    )

    suite_path = os.path.join(experiment_dir, f"{experiment_id}-suite")
    log_path = os.path.join(experiment_dir, "log")

    launch_experiment(suite_path, True, log_path)

    return experiment_dir


def run_suite(suite: str, platform: str, test_tier: TestSuite):
    # Add a random int to the experiment_id to mitigate errors from workflows
    # created at (roughly) the same time.
    ii = random.randint(0, 99)

    experiment_id_root = f"t{datetime.now().strftime('%Y%jT%H%M')}r{ii:02d}"
    experiment_id = f"{experiment_id_root}{suite}"

    # Get test directory from `~/.swell/swell-test.yaml`
    testdir = Path(tempfile.TemporaryDirectory().name).expanduser()
    test_config = {
        "test_root": testdir.name
    }
    yaml = YAML(typ='safe')
    yamlfile = Path("~/.swell/swell-test.yaml").expanduser()
    try:
        with open(yamlfile, "r") as f:
            test_user_config = yaml.load(f)
        print(f"Updating test defaults with user config from {yamlfile}.")
        test_config = {**test_config, **test_user_config}
    except FileNotFoundError:
        pass
    except Exception as err:
        raise err

    testdir.mkdir(exist_ok=True)

    print(f"Testing suite: {suite}")
    print(f"Test directory: {testdir.name}")
    print(f"Experiment ID: {experiment_id}")

    override = {
        "experiment_id": experiment_id,
        "experiment_root": str(testdir),
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

    # Build JEDI for tier 2 tests if existing build is not specified in user yaml
    if test_tier == TestSuite.TIER2:
        if not ("jedi_build_method" in test_config
           and test_config["jedi_build_method"] == "use_existing"
           and 'existing_jedi_source_directory' in test_config
           and 'existing_jedi_build_directory' in test_config):
            jedi_dir = build_jedi_for_tier2(str(testdir), experiment_id_root,
                                            platform, test_config)

            tier2_override = {"jedi_build_method": "use_existing",
                              "existing_jedi_source_directory": f"{jedi_dir}/jedi_bundle/source",
                              "existing_jedi_build_directory": f"{jedi_dir}/jedi_bundle/build"}

            override = update_dict(override, tier2_override)

            if suite == "build_jedi":
                return None

    override_yml = os.path.join(experiment_dir, "override.yaml")
    with open(override_yml, "w") as f:
        yaml.dump(override, f)

    # Suites are currently set up to use tier2 defaults, this setting
    # may need to be changed in the future
    suite_config = suite + ('_tier1' if test_tier == TestSuite.TIER1 else '')

    create_experiment_directory(
        suite_config, "defaults", platform,
        str(override_yml), False, None, True
    )

    # TODO: Check some stuff about the experiment directory

    suite_path = str(experiment_dir / f"{experiment_id}-suite")
    log_path = str(experiment_dir / "log")

    launch_experiment(suite_path, True, log_path)

    # TODO: Check the outputs
