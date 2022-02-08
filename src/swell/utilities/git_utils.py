# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import subprocess


# --------------------------------------------------------------------------------------------------


def git_got(git_url, git_branch, out_dir, logger):

    # Clone repo at git_url to out_dir
    # --------------------------------
    if not os.path.exists(out_dir):

        # If directory does not exist clone the repo
        os.mkdir(out_dir)

        # Clone the repo
        logger.info('Attempting Git clone of ' + git_url)
        try:
            subprocess.run(['git', 'clone', git_url, out_dir], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.abort('Git clone failed in git_got.')

    else:

        logger.info('Directory ' + out_dir + ' already exists so ' + git_url + ' not cloned.')

    # Whether the directory exists or not switch to desired branch
    # ------------------------------------------------------------
    cwd = os.getcwd()
    os.chdir(out_dir)
    logger.info('Checking out branch/tag/commit ' + git_branch)
    try:
        subprocess.run(['git', 'checkout', git_branch], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.abort('Git checkout of branch ' + git_branch + ' failed in git_got. ')
    os.chdir(cwd)


# --------------------------------------------------------------------------------------------------
