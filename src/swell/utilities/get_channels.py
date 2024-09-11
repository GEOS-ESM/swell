# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import yaml
import os
from datetime import datetime as dt
from itertools import groupby

# --------------------------------------------------------------------------------------------------


def process_channel_lists(channel_list):

    '''
        Function processes list of elements in channel list
    '''

    final_channels_list = []
    if not isinstance(channel_list, list):
        channel_list = [channel_list]
    for element in channel_list:
        if '-' in element:
            start, end = map(int, element.split('-'))
            result_list = [x for x in range(start, end + 1)]
            final_channels_list += result_list
        else:
            final_channels_list += [int(element)]

    return final_channels_list

# --------------------------------------------------------------------------------------------------


def create_range_string(avail_list):
    '''
        Function converts integer list into string of ranges
    '''
    ranges = []
    for _, g in groupby(enumerate(avail_list), lambda i_x: i_x[0]-i_x[1]):
        group = list(map(lambda x: x[1], g))
        if len(group) > 1:
            ranges.append(f'{group[0]}-{group[-1]}')
        else:
            ranges.append(str(group[0]))
    return ', '.join(ranges)

# --------------------------------------------------------------------------------------------------


def get_channel_list(input_dict, dt_cycle_time):

    '''
        Function retrieves channel lists from dict loaded from a yaml file
    '''

    for element in input_dict:
        begin_date = dt.strptime(element['begin date'], "%Y-%m-%dT%H:%M:%S")
        end_date = dt.strptime(element['end date'], "%Y-%m-%dT%H:%M:%S")
        if (dt_cycle_time > begin_date) and (dt_cycle_time < end_date):
            return element['channels']

# --------------------------------------------------------------------------------------------------


def get_channels(path_to_observing_sys_yamls, observation, dt_cycle_time, logger):

    '''
        Comparing available channels and active channels from the observing
        system records to create the use flag array needed in the
        qc filter yaml files.
    '''

    # Retrieve available and active channels from records yaml
    path_to_observing_sys_config = path_to_observing_sys_yamls + '/' + \
        observation + '_channel_info.yaml'

    if os.path.isfile(path_to_observing_sys_config):
        with open(path_to_observing_sys_config, 'r') as file:
            data = yaml.safe_load(file)
            available_channels = get_channel_list(data['available'], dt_cycle_time)
            active_channels = get_channel_list(data['active'], dt_cycle_time)

        if available_channels is None:
            logger.abort(f'Missing available channels for {observation}, '
                         'Confirm that you are using the right version of GEOSmksi')

        if active_channels is None:
            logger.abort(f'Missing active channels for {observation}, '
                         'Confirm that you are using the right version of GEOSmksi')

        available_channels_list = process_channel_lists(available_channels)
        available_range_string = create_range_string(available_channels_list)
        active_channels_list = process_channel_lists(active_channels)
        use_flags = [1 if x in active_channels_list else -1 for x in available_channels_list]

        return available_range_string, use_flags

    else:
        return None, None

# --------------------------------------------------------------------------------------------------


def num_active_channels(path_to_observing_sys_yamls, observation, dt_cycle_time):

    # Retrieve available and active channels from records yaml
    path_to_observing_sys_config = path_to_observing_sys_yamls + '/' + \
        observation + '_channel_info.yaml'

    if os.path.isfile(path_to_observing_sys_config):
        with open(path_to_observing_sys_config, 'r') as file:
            data = yaml.safe_load(file)
            active_channels = get_channel_list(data['active'], dt_cycle_time)

        active_channels_list = process_channel_lists(active_channels)
        return len(active_channels_list)

    else:
        print('path_to_observing_sys_config undefined')
