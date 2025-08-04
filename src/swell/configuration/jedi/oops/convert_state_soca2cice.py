# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------

class convert_state_soca2cice(OopsConfig):

    def render_oops(self):

        oops = {
            'input geometry': self.interface_model('geometry'),
            'output geometry': self.interface_model('geometry'),
            'variable change': self.interface_model('variable_change_soca2cice'),
            'states': self.interface_model('states')
        }

        return oops


# --------------------------------------------------------------------------------------------------
