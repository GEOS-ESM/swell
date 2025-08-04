# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------

class hofx3D(OopsConfig):

    def render_oops(self):

        oops = {
            'time window': {
                'begin': self.template_dict['window_begin_iso'],
                'end': self.template_dict['window_end_iso'],
                'bound to include': 'begin'
            },
            'geometry': self.interface_model('geometry'),
            'state': self.interface_model('background'),
            'observations': {
                'get values': self.interface_model('getvalues'),
                'observers': self.special_observations()
            }
        }

        return oops


# --------------------------------------------------------------------------------------------------
