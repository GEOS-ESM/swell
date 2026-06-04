# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names_ensemble

# --------------------------------------------------------------------------------------------------


def comp_mean_output(template_dict: Mapping) -> Mapping:
        
    fn_output_mean = template_dict['ensmeanvariance_spec_item'].get('fn_output_mean')
    geom = template_dict['ensmeanvariance_spec_item'].get('geom')

    mean_output = {}
    if geom == 'latlon':
        mean_output = {
            'filetype': 'auxgrid',
            'gridtype': 'latlon',
            'datapath': template_dict['cycle_dir'],
            'filename': fn_output_mean,
            'field io names': field_io_names_ensemble
        }

    return ensemble_mean_output


# --------------------------------------------------------------------------------------------------
