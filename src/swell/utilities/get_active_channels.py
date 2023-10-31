# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import yaml
import os
import pandas as pd
import numpy as np
from datetime import datetime as dt

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


def get_active_channels(path_to_observing_sys_yamls, observation, dt_cycle_time):

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

        available_channels_list = process_channel_lists(available_channels)
        active_channels_list = process_channel_lists(active_channels)
        use_flags = [1 if x in active_channels_list else -1 for x in available_channels_list]

        return use_flags

    else:
        return None

# --------------------------------------------------------------------------------------------------
