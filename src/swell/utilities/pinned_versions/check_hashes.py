import os
import yaml
import subprocess
from swell.utilities.logger import Logger


def get_pinned_vers_path() -> str:
    return os.path.split(__file__)[0]


def check_hashes(jedi_bundle_loc: str, logger: Logger) -> None:

    # Get list of directories in jedi_bundle_loc
    dirs = os.listdir(jedi_bundle_loc)

    pinned_vers_file = get_pinned_vers_path() + "/pinned_versions.yaml"
    # Loaded pinned_versions into dict
    with open(pinned_vers_file) as stream:
        pinned_vers = yaml.safe_load(stream)

    incorrect_hash = []
    for repo_dict in pinned_vers:
        repo_name = next(iter(repo_dict))
        expected_hash = repo_dict[repo_name]["branch"]

        # Get hash or branch of repo in jedi bundle
        if repo_name in dirs:
            cmd = ["git", "rev-parse", "HEAD"]
            with subprocess.Popen(cmd, cwd=jedi_bundle_loc+repo_name,
                                  stdout=subprocess.PIPE) as proc:
                curr_hash = proc.stdout.read()
                proc.kill()

            curr_hash = curr_hash.decode("utf-8").replace('\n', '')
            if expected_hash != curr_hash:
                incorrect_hash.append(repo_name)

    # If there are incorrect hashes, logger abort
    if incorrect_hash:
        logger.abort("Wrong commit hashes found for these repositories "
                     f"in jedi_bundle: {incorrect_hash}")
