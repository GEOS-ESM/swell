# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.deployment.prep_config_base import PrepConfigBase


# --------------------------------------------------------------------------------------------------


class PrepConfigCli(PrepConfigBase):

    def execute(self):

        self.logger.abort('This is where a cli interface will do its work')


# --------------------------------------------------------------------------------------------------
