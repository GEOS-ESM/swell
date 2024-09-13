# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os

from swell.utilities.shell_commands import run_subprocess_dev_null
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


def git_change_branch(logger: Logger, git_branch: str, out_dir: str) -> None:

    # Change to a specific branch
    # ---------------------------
    cwd = os.getcwd()
    os.chdir(out_dir)
    logger.info('Checking out branch/tag/commit ' + git_branch)

    # Change branch
    command = ['git', 'checkout', git_branch]
    run_subprocess_dev_null(logger, command)

    # Go back to previous directory
    os.chdir(cwd)


# --------------------------------------------------------------------------------------------------


def git_clone(
    logger: Logger,
    git_url: str,
    git_branch: str,
    out_dir: str,
    change_branch: bool = False
) -> None:

    # Clone repo at git_url to out_dir
    # --------------------------------
    if not os.path.exists(out_dir):

        # Clone the repo
        command = ['git', 'clone', '-b', git_branch, git_url, out_dir]
        run_subprocess_dev_null(logger, command)

    else:

        logger.info('Directory ' + out_dir + ' already exists so ' + git_url + ' not cloned.')
        if change_branch:
            logger.info('Will instead attempt to change to requested branch.')
            git_change_branch(logger, git_branch, out_dir)


# --------------------------------------------------------------------------------------------------


def git_got(git_url: str, git_branch: str, out_dir: str, logger: Logger):

    # Clone repo at git_url to out_dir
    # --------------------------------
    if not os.path.exists(out_dir):

        # If directory does not exist clone the repo
        os.mkdir(out_dir)

        # Clone the repo
        logger.info('Attempting Git clone of ' + git_url + ' to ' + out_dir)
        run_subprocess_dev_null(logger, ['git', 'clone', git_url, out_dir])

    else:

        logger.info('Directory ' + out_dir + ' already exists so ' + git_url + ' not cloned.')

    # Whether the directory exists or not switch to desired branch
    # ------------------------------------------------------------
    os.chdir(out_dir)
    logger.info('Checking out branch/tag/commit ' + git_branch)
    run_subprocess_dev_null(logger, ['git', 'checkout', git_branch])


# --------------------------------------------------------------------------------------------------
