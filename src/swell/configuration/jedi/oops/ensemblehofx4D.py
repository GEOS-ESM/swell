# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class ensemblehofx4D(OopsConfig):

    def render_oops(self):

        packet_ensemble_members = self.template_dict['packet_ensemble_members']

        files = [f'jedi_hofx_mem{member}_config.yaml' for member in packet_ensemble_members]

        oops = {
            'files': files
        }

        return oops


# --------------------------------------------------------------------------------------------------
