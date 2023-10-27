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
from swell.utilities.git_utils import git_got
from swell.utilities.instr_state_machine import InstrStateMachine
from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------

def process_channel_lists(channel_list):

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
    for element in input_dict:
        begin_date = dt.strptime(element['begin date'], "%Y-%m-%dT%H:%M:%S")
        end_date = dt.strptime(element['end date'], "%Y-%m-%dT%H:%M:%S")
        if (dt_cycle_time > begin_date) and (dt_cycle_time < end_date):
            return element['channels']

# --------------------------------------------------------------------------------------------------

def get_active_channels(path_to_observing_sys_yamls, observation, cycle_time):

    # Cycle time to datetime object
    dt_cycle_time = dt.strptime(cycle_time, "%Y%m%dT%H%M%SZ")

    # Retrieve available and active channels from records yaml
    obs_name = observation.split('_')[0]
    path_to_observing_sys_config = path_to_observing_sys_yamls + '/' + observation +'_channel_info.yaml'

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

def read_sat_db(path_to_sat_db, column_names):

    # read data into a dataframe, throw line away if it starts with # or newline
    # ---------------------------------------------------------------------------
    filename = path_to_sat_db
    df = pd.DataFrame(columns=column_names)

    file = open(filename, 'r')
    lines = file.readlines()

    # read blindly into an array, throw line away if it starts with # or newline
    idx = 0
    for line in lines:
        line_parts = line.split()
        if (line_parts):

            if (line_parts[0][0] != '#' and line_parts[0][0] != '\n'):
                new_row = pd.DataFrame.from_dict({
                    'sat': [''],
                    'start': [''],
                    'end': [''],
                    'instr': [''],
                    'channel_num': [0],
                    'channels': [[]],
                    'comments': ['']})

                df = pd.concat([df, new_row], ignore_index=True)
                df['sat'][idx] = line_parts[0]
                df['start'][idx] = line_parts[1]+line_parts[2]
                df['end'][idx] = line_parts[3]+line_parts[4]
                df['instr'][idx] = line_parts[5]
                df['channel_num'][idx] = line_parts[6]

                comment_present = next((i for i, x in enumerate(line_parts) if x == '#'), None)

                if (comment_present):
                    channel_list = line_parts[7:comment_present]
                    comment = line_parts[comment_present:]
                    comment_str = ' '.join(comment)
                    # accounting for no comment
                    if (len(comment_str) != 1):
                        df['comments'][idx] = comment_str
                else:
                    channel_list = line_parts[7:]

                df['channels'][idx] = channel_list
                idx += 1
    return df


# --------------------------------------------------------------------------------------------------


def run_sat_db_process(git_out_dir, logger):

    # Process satellite database files in GEOS-ESM and return dataframe
    # -----------------------------------------------------------------------

    git_repo = 'https://github.com/GEOS-ESM/GEOSana_GridComp.git'
    git_branch = 'develop'
    git_out_path = os.path.join(git_out_dir, 'GEOSana_GridComp')

    # clone repo
    git_got(git_repo, git_branch, git_out_path, logger)
    path_to_sat_db = os.path.join(git_out_path, 'GEOSaana_GridComp', 'GSI_GridComp', 'mksi', 'sidb')

    column_names = ['sat', 'start', 'end', 'instr', 'channel_num',
                           'channels', 'comments']
    df = read_sat_db(path_to_sat_db, column_names)
    final_df = pd.DataFrame(columns=column_names)

    sat_list = np.unique(df['sat'].values)
    for sat in sat_list:
        sat_df = df.loc[df['sat'] == sat]

        instr_list = np.unique(sat_df['instr'].values)

        for instr in instr_list:
            instr_df = sat_df.loc[sat_df['instr'] == instr]

            state_machine = InstrStateMachine(instr_df)
            state_machine.run()
            new_instr_df = state_machine.get_instr_df()
            final_df = final_df.append(new_instr_df)

    return final_df


# --------------------------------------------------------------------------------------------------
