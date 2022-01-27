# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os


# --------------------------------------------------------------------------------------------------


def git_got(git_url, git_branch, out_dir):

    # Clone repo at git_url to out_dir
    # --------------------------------
    if not os.path.exists(out_dir):
        # If directory does not exist clone the repo
        os.mkdir(out_dir)
        os.system('git clone -b {} {} {}'.format(git_branch, git_url, out_dir))
    else:
        # If directory does exists just check on the correct branch
        cwd = os.getcwd()
        os.chdir(out_dir)
        os.system('git checkout {}'.format(git_branch))
        os.chdir(cwd)


# --------------------------------------------------------------------------------------------------
