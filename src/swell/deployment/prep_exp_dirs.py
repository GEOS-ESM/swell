# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import os
import shutil
import yaml

from swell.suites.suites import return_suite_path

# --------------------------------------------------------------------------------------------------


class dir_config():


    # ----------------------------------------------------------------------------------------------


    def __init__(self, logger, suite_name, experiment_id_dir, exp_id, *dirs):

        # Create copy of the logger
        # -------------------------
        self.logger = logger

        # Dictionary with paths to experiment directories
        # -----------------------------------------------
        self.dir_dict = {}
        self.dir_dict['experiment'] = exp_id
        self.dir_dict.update({'experiment_root': os.path.dirname(experiment_id_dir)})

        # Create the sub directories of the experiment
        # --------------------------------------------
        for new_dir in dirs:
            self.dir_maker(experiment_id_dir, new_dir)

        # Put files in the suite directory
        # --------------------------------
        self.populate_suite(suite_name)



    # ----------------------------------------------------------------------------------------------


    def dir_maker(self, exp_id_dir, dir_name=('', '')):
        dir_var_name = dir_name[0]
        dir_full = os.path.join(exp_id_dir, dir_name[1])
        self.logger.info('Creating directory: {}'.format(dir_full))
        try:
            os.mkdir(dir_full)
        except Exception:
            self.logger.info('Directory already exists: {}'.format(dir_full))

        self.logger.info('Adding this directory to config with key: {}'.format(dir_var_name))
        self.dir_dict.update({dir_var_name: dir_full})


    # ----------------------------------------------------------------------------------------------


    def populate_suite(self, suite_name):
        print(suite_name)
        suite_path = return_suite_path()
        for s in ['modules', os.path.join(suite_name, 'flow.cylc'), 'CMakeLists_template.txt']:
          src_file = os.path.split(s)[1]
          src_path_file = os.path.join(suite_path, os.path.split(s)[0], src_file)
          dst_path_file = os.path.join(self.dir_dict['suite_dir'], '{}'.format(src_file))
          self.logger.info('Copying {} to {}'.format(src_path_file, dst_path_file))
          shutil.copy(src_path_file, dst_path_file)


# --------------------------------------------------------------------------------------------------
