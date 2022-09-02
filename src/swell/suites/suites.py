# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import importlib


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

        # Final experiment dictionary

        print(self.prep_using.experiment_dict)

# --------------------------------------------------------------------------------------------------


def return_suite_path():
    return os.path.split(__file__)[0]

# --------------------------------------------------------------------------------------------------
