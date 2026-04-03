# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from ruamel.yaml import YAML
import os
from datetime import datetime

from swell.utilities.logger import get_logger
from swell.utilities.datetime_util import datetime_formats

# --------------------------------------------------------------------------------------------------


def check_da_params(config_list: list,
                    model_component: str,
                    start_cycle_point_in: str | None,
                    final_cycle_point_in: str | None,
                    cycle_times_in: str | None) -> None:

    # From two or more experiments, check that the window parameters are the same, and gather the
    # common cycle times between the two. Returns times between the start and final cycle points,
    # or pick automatically if set to None.

    # Dictionary containing window and cycles for all experiments
    cycle_dicts = {}

    logger = get_logger('CheckDAParams')

    for i, config_file in enumerate(config_list):

        # Name the config after its index
        cycle_dict = cycle_dicts[str(i)] = {}

        # Abort if file not found
        if not os.path.isfile(config_file):
            logger.abort(f'Config file {config_file} does not exist.')

        # Open the file for location and window information
        yaml = YAML(typ='safe')
        with open(config_file, 'r') as f:
            config_dict = yaml.load(f)

        # Window params
        start_cycle_point = config_dict['start_cycle_point']
        final_cycle_point = config_dict['final_cycle_point']

        window_length = config_dict['models'][model_component]['window_length']
        cycle_times = config_dict['models'][model_component]['cycle_times']

        # Save the information
        cycle_dict['start_cycle_dto'] = datetime.strptime(start_cycle_point,
                                                          datetime_formats['iso_format'])
        cycle_dict['final_cycle_dto'] = datetime.strptime(final_cycle_point,
                                                          datetime_formats['iso_format'])

        cycle_dict['window_length'] = window_length
        cycle_dict['cycle_times'] = cycle_times

    start_cycle_dtos = []
    final_cycle_dtos = []

    window_lengths = []

    # Gather all the window params into a list
    for value in cycle_dicts.values():
        start_cycle_dtos.append(value['start_cycle_dto'])
        final_cycle_dtos.append(value['final_cycle_dto'])

        window_lengths.append(value['window_length'])

    # Check to make sure the window params match
    if len(set(window_lengths)) > 1:
        logger.abort('The experiments specified have mismatched window parameters.')

    # Iterate through all the cycle times and find the common ones.
    common_cycle_times = None
    for value in cycle_dicts.values():
        cycle_times = value['cycle_times']

        if common_cycle_times is not None:
            common_cycle_times = list(set(cycle_times) & set(common_cycle_times))
        else:
            common_cycle_times = cycle_times

    cycle_times_out = []

    if cycle_times_in == [None] or cycle_times_in == 'None':
        if common_cycle_times is None:
            cycle_times_out = []
        else:
            cycle_times_out = common_cycle_times
    else:
        cycle_times_out = cycle_times_in

    # Get the start cycle dto object, or set automatically
    if start_cycle_point_in is None or start_cycle_point_in == 'None':
        if len(start_cycle_dtos) > 0:
            start_cycle_dto = max(start_cycle_dtos)
            start_cycle_point_out = start_cycle_dto.strftime(datetime_formats['iso_format'])
        else:
            start_cycle_point_out = None
    else:
        start_cycle_point_out = start_cycle_point_in

    # Get the final cycle dto object, or set automatically
    if final_cycle_point_in is None or final_cycle_point_in == 'None':
        if len(final_cycle_dtos) > 0:
            final_cycle_dto = min(final_cycle_dtos)
            final_cycle_point_out = final_cycle_dto.strftime(datetime_formats['iso_format'])
        else:
            final_cycle_point_out = None
    else:
        final_cycle_point_out = final_cycle_point_in

    return start_cycle_point_out, final_cycle_point_out, cycle_times_out

# --------------------------------------------------------------------------------------------------
