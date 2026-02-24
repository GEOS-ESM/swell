# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def ensemble_solver(template_dict: Mapping) -> Mapping:

    local_ensemble_solver = template_dict['local_ensemble_solver']
    local_ensemble_use_linear_observer = template_dict['local_ensemble_use_linear_observer']
    local_ensemble_inflation_rtps = template_dict['local_ensemble_inflation_rtps']
    local_ensemble_inflation_rtpp = template_dict['local_ensemble_inflation_rtpp']
    local_ensemble_inflation_mult = template_dict['local_ensemble_inflation_mult']
    frac_retained_variance = template_dict['frac_retained_variance']
    vertical_localization_lengthscale = template_dict['vertical_localization_lengthscale']
    
    ensemble_solver = {
        'solver': local_ensemble_solver,
        'use linear observer': local_ensemble_use_linear_observer,
        'vertical localization': {
            'fraction of retained variance': frac_retained_variance,
            'lengthscale': vertical_localization_lengthscale,
            'lengthscale units': 'logp',
            'write eigen vectors': True,    # False
            'read eigen vectors': False, 
        },
        'inflation': {
            'rtps': local_ensemble_inflation_rtps,
            'rtpp': local_ensemble_inflation_rtpp,
            'mult': local_ensemble_inflation_mult,
        }
    }

    return ensemble_solver

# --------------------------------------------------------------------------------------------------
