# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class diffstates(OopsConfig):

    def render_oops(self):

        two_states = self.interface_model('two_states')
        oops = {
            'state geometry': self.interface_model('geometry'),
            'increment geometry': self.interface_model('geometry_wofms'),
            **two_states,
            'output': self.interface_model('diffstates_output')
        }

        return oops


# --------------------------------------------------------------------------------------------------
