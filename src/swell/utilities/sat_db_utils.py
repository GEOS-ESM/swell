# (C) Copyright 2021 NASA Global Modeling and Assimilation Office
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import pandas as pd
import numpy as np
from swell.utilities.git_utils import git_got
from swell.utilities.instr_state_machine import InstrStateMachine


# --------------------------------------------------------------------------------------------------


def read_sat_db(path_to_sat_db, column_names):

    # read data into a dataframe, throw line away if it starts with # or newline
    # ---------------------------------------------------------------------------
    filename = os.path.join(path_to_sat_db, 'active_channels.tbl')
    df = pd.DataFrame(columns=column_names)

    file = open(filename, 'r')
    lines = file.readlines()

    # read blindly into an array, throw line away if it starts with # or newline
    idx = 0
    for line in lines:
        line_parts = line.split()
        if (line_parts):

            if (line_parts[0][0] != '#' and line_parts[0][0] != '\n'):

                df = df.append({
                    'sat': '',
                    'start': '',
                    'end': '',
                    'instr': '',
                    'channel_num': 0,
                    'channels': [],
                    'comments': ''
                }, ignore_index=True)

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
