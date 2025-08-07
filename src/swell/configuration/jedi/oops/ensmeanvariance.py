# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class ensmeanvariance(OopsConfig):

    def render_oops(self):

        oops = {
            'geometry': self.interface_model('geometry'),
            'ensemble': self.interface_model('ensemble_block'),
            'variance output': self.interface_model('ensemble_cube_variance_output'),
            'mean output': self.interface_model('ensemble_cube_mean_output')
        }

        return oops


# --------------------------------------------------------------------------------------------------
