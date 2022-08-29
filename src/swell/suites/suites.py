# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import importlib


# --------------------------------------------------------------------------------------------------


class suites():

    # ----------------------------------------------------------------------------------------------

    def __init__(self, method, logger):

        self.method = method
        self.logger = logger

    # ----------------------------------------------------------------------------------------------

    def prep_suite_config(self):

        # Import the chosen method
        # ------------------------
        method_class = getattr(importlib.import_module('swell.suites.prep_using_'+self.method),
                               'prep_suite_config')

        # Initiate the class
        # ------------------
        method_obj = method_class(logger)

        # Call the config prep step
        # -------------------------
        method_obj.execute()

# --------------------------------------------------------------------------------------------------


def return_suite_path():
    return os.path.split(__file__)[0]


# --------------------------------------------------------------------------------------------------
