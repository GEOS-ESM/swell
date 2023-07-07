# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.deployment.prep_config_base import PrepConfigBase


# --------------------------------------------------------------------------------------------------


class PrepConfigDefaults(PrepConfigBase):

    def get_answer(self, key, val):
        return val['default_value']

    # ---------------------------------------------------------------------------------------------- 

    def get_models(self):
        return self.default_models

    # ----------------------------------------------------------------------------------------------

    def before_next(self):
        return None

# --------------------------------------------------------------------------------------------------
