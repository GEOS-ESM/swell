# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import importlib
import yaml

from swell.utilities.dictionary_utilities import get_element

# --------------------------------------------------------------------------------------------------


class Suites():

    # ----------------------------------------------------------------------------------------------

    def __init__(self, method, logger, config_file):

        self.method = method.lower()  # Ignore any user input cases
        self.logger = logger

        # Assert valid method
        # -------------------
        valid_tasks = ['default', 'gui', 'cli']
        if self.method not in valid_tasks:
            logger.abort(f'In Suites constructor method \'{self.method}\' not one of the valid ' +
                         f'tasks {valid_tasks}')

        # Set the object that will be used to populate dictionary options
        # ---------------------------------------------------------------
        PrepUsing = getattr(importlib.import_module('swell.suites.prep_using_'+self.method),
                            'PrepUsing'+self.method.capitalize())
        self.prep_using = PrepUsing(self.logger, config_file)

    # ----------------------------------------------------------------------------------------------

    def prep_suite_config(self):

        # Call the config prep step
        # -------------------------
        self.prep_using.execute()

        # Write final experiment dictionary
        # ---------------------------------
        experiment_id = get_element(self.logger, self.prep_using.experiment_dict, 'experiment_id')
        experiment_rt = get_element(self.logger, self.prep_using.experiment_dict, 'experiment_root')

        experiment_rt = os.path.expandvars(experiment_rt)

        # Make directory
        experiment_root_id = os.path.join(experiment_rt, experiment_id)
        os.makedirs(experiment_root_id, exist_ok=True)

        # Write dictionary
        exp_dict_file = os.path.join(experiment_root_id, 'experiment.yaml')
        with open(exp_dict_file, 'w') as exp_dict_file_open:
            yaml.dump(self.prep_using.experiment_dict, exp_dict_file_open, default_flow_style=False, sort_keys=False)

# --------------------------------------------------------------------------------------------------


def return_suite_path():
    return os.path.split(__file__)[0]

# --------------------------------------------------------------------------------------------------
