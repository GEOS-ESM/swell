# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import importlib
import ruamel.yaml
import sys
import yaml

from swell.utilities.dictionary_utilities import get_element, add_comments_to_dictionary

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
        # --------------
        experiment_root_id = os.path.join(experiment_rt, experiment_id)
        os.makedirs(experiment_root_id, exist_ok=True)

        # Add comments to dictionary
        # --------------------------
        experiment_dict_string = yaml.dump(self.prep_using.experiment_dict,
                                           default_flow_style=False, sort_keys=False)

        experiment_dict_string_comments = add_comments_to_dictionary(experiment_dict_string,
                                                                     self.prep_using.comment_dict)


        print('\nNEW DICT')
        print(experiment_dict_string_comments)

        # Write dictionary with ruamel.yaml to preserve comments
        exp_dict_file = os.path.join(experiment_root_id, 'experiment.yaml')
        experiment_dict_comments = ruamel.yaml.round_trip_load(experiment_dict_string_comments)
        with open(exp_dict_file, 'w') as exp_dict_file_open:
            ruamel.yaml.round_trip_dump(experiment_dict_comments, exp_dict_file_open)


# --------------------------------------------------------------------------------------------------


def return_suite_path():
    return os.path.split(__file__)[0]

# --------------------------------------------------------------------------------------------------
