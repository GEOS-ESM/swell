# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class convert_state_fv3(OopsConfig):

    def render_oops(self):

        oops = {
            'input geometry': self.interface_model('geometry'),
            'output geometry': self.interface_model('geometry_target'),
            'states': self.interface_model('convert_state_states'),
        }

        return oops


# --------------------------------------------------------------------------------------------------
