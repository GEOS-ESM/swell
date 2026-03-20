# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_cf.model.shared import \
        field_io_names


# Central block builders
# --------------------------------------------------------------------------------------------------


def _build_identity_central_block(template_dict: Mapping) -> Mapping:
    """Identity covariance central block"""
    return {'saber block name': 'ID'}


def _build_bump_nicas_central_block(template_dict: Mapping) -> Mapping:
    """BUMP/NICAS covariance central block"""
    field_aliases = []
    for var in template_dict.get('analysis_variables', []):
        field_aliases.append({
            'in code': var,
            'in file': 'fixedlevel_H_500_300_V_00_03'
        })

    return {
        'saber block name': 'BUMP_NICAS',
        'read': {
            'io': {
                'data directory': f"{template_dict['cycle_dir']}/",
                'files prefix': 'geos_cf',
                'alias': field_aliases
            },
            'drivers': {
                'multivariate strategy': 'univariate',
                'read local nicas': True
            }
        }
    }

# Outer block builders
# --------------------------------------------------------------------------------------------------


def _build_stddev_bkg_scaled(template_dict: Mapping) -> Mapping:
    """Standard deviation outer block"""
    return {
        'saber block name': 'StdDev',
        'stddev scale factor': '0.25',
        'read': {
            'model file': {
                'datetime': template_dict['local_background_time_iso'],
                'set datetime on read': True,
                'filetype': 'cube sphere history',
                'max allowable geometry difference': 0.1,
                'datapath': template_dict['cycle_dir'],
                'filename': 'bkg.%yyyy%mm%ddT%hh%MM%ssZ.nc4',
                'field io names': field_io_names,
            }
        }
    }


def _build_stddev_fixed_values(template_dict: Mapping) -> Mapping:
    """Standard deviation outer block with fixed values from analysis variables"""
    # Get the stddev values for each analysis variable
    # Example: {'volume_mixing_ratio_of_no2': 5e-9, 'volume_mixing_ratio_of_o3': 1e-8}
    stddev_dict = {
        'volume_mixing_ratio_of_no2': 5e-9,
        'volume_mixing_ratio_of_o3': 1e-8,
        'volume_mixing_ratio_of_co': 5e-8,
    }

    # Build the standard deviations list
    standard_deviations = [
        {'variable': var, 'stddev': value}
        for var, value in stddev_dict.items()
    ]

    return {
        'saber block name': 'StdDev',
        'standard deviations': standard_deviations
    }

# Main assembler
# --------------------------------------------------------------------------------------------------


def background_error(template_dict: Mapping) -> Mapping:
    """
    Assemble background error covariance configuration from modular components.

    Parameters
    ----------
    template_dict : Mapping
        Dictionary containing configuration parameters including:
        - central_block: Type of central block ('identity', 'bump_nicas', 'diffusion')
        - outer_block: add StdDev outer block


    Returns
    -------
    Mapping
        JEDI-compatible background error covariance configuration
    """

    # Select central block builder
    central_block_select = template_dict.get('saber_central_block', 'identity')

    central_block_types = {
        'identity': _build_identity_central_block,
        'bump_nicas': _build_bump_nicas_central_block,
    }

    # Build the central block
    if central_block_select not in central_block_types:
        raise ValueError(
            f"Unknown background_error_model '{central_block_select}'. "
            f"Choose from: {list(central_block_types.keys())}"
        )

    central_block = central_block_types[central_block_select](template_dict)

    # Assemble base configuration
    background_error_config = {
        'covariance model': 'SABER',
        'saber central block': central_block,
    }

    # Optionally add outer blocks (skip for identity central block)
    if central_block_select != 'identity' and 'saber_outer_block' in template_dict:

        outer_block_select = template_dict.get('saber_outer_block')

        outer_block_types = {
            'stddev_bkg_scaled': _build_stddev_bkg_scaled,
            'stddev_fixed_values': _build_stddev_fixed_values,
        }

        if outer_block_select not in outer_block_types:
            raise ValueError(
                f"Unknown outer_block '{outer_block_select}'. "
                f"Choose from: {list(outer_block_types.keys())}"
            )

        outer_block = outer_block_types[outer_block_select](template_dict)

        background_error_config['saber outer blocks'] = [outer_block]

    return background_error_config

# --------------------------------------------------------------------------------------------------