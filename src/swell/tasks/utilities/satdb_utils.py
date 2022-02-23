# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import pandas as pd
import numpy as np
from datetime import datetime as dt


# --------------------------------------------------------------------------------------------------


def check_end_times(end_times):

    '''
        Checks end times for 24 hour strings and converts them to 18
    '''

    new_end_times = []

    for end_time in end_times:
        # Note that python datetime does not allow for times with hour = 24
        hour = end_time[8:10]
        if(hour == '24'):
            # Subtract 6 hours
            tmp = int(end_time) - 60000
            new_end_times.append(str(tmp))
        else:
            new_end_times.append(end_time)

    return new_end_times


# --------------------------------------------------------------------------------------------------


class InstrStateMachine:

    def __init__(self, instr_df):

        '''
            Intakes a dataframe representing the rows for a particular
            instrument on a particular satellite.
        '''

        self.idx = 0
        self.main_idx = 0
        self.start_times = []
        self.end_times = []
        self.instr_df = instr_df
        self.compare_channels = []
        self.curr_channel_list = []
        self.main_channel_list = []

        self.return_df = pd.DataFrame(columns=list(instr_df.columns.values))

    # ----------------------------------------------------------------------------------------------

    def run(self):

        '''
            Effectively state one of the state machine.
            Generates an ordered list of start times and corresponding
            end times. Checks the end times and then proceeds to condition one.
        '''

        self.start_times = list(np.unique(self.instr_df["start"].values))
        self.start_times.sort(key=int)
        for start in self.start_times:
            self.end_times.append(
                self.instr_df.loc[self.instr_df["start"] == start]["end"].values[0])

        self.end_times = check_end_times(self.end_times)

        self.condition_one()

    # ----------------------------------------------------------------------------------------------

    def condition_one(self):

        '''
            If there is one row for the date range, go to state 2. Otherwise,
            go to state 3.
        '''

        start_time_df = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        n_curr_start_rows = len(start_time_df)
        assert(n_curr_start_rows != 0)

        if(n_curr_start_rows == 1):
            self.curr_channel_list = start_time_df["channels"].values[0]
            self.state_two()
        else:
            self.state_three()

    # ----------------------------------------------------------------------------------------------

    def state_two(self):

        '''
            Update return_df with new row, increment idx, and then go to
            condition 4.
        '''

        row = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        self.update_return_df(row)
        self.idx += 1

        self.condition_four()

    # ----------------------------------------------------------------------------------------------

    def state_three(self):

        '''
            Gather channels for all rows in current datetime. If there are more
            than one end time within the rows, set main_start_idx and
            main_channels_list, set compare_channels to the current channel list,
            update return_df with a new row, increment index,
            and then go to condition 2.
            Else, go to state 2 with the updated current channel list.
        '''

        rows = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        [self.curr_channel_list.extend(i) for i in rows["channels"].values]
        self.curr_channel_list = list(set(self.curr_channel_list))
        self.curr_channel_list.sort(key=int)

        end_times = rows["end"].values
        other_end_times = end_times[end_times != end_times[0]]

        if(other_end_times):

            first_end = other_end_times[0]
            first_end_row = self.instr_df.loc[self.instr_df["end"] == first_end]
            self.compare_channels = first_end_row["channels"].values[0]

            self.main_channel_list = self.curr_channel_list
            self.main_idx = self.idx

            self.update_return_df(first_end_row, no_comment=True)
            self.idx += 1

            self.condition_two()

        else:
            self.state_two()

    # ----------------------------------------------------------------------------------------------

    def condition_two(self):

        '''
            If curr start/end is in main range, go to condition 3. Otherwise
            go to state 2
        '''

        # Return if end of df is reached
        if(self.idx == len(self.start_times)):
            return

        # Get current and main start and end time
        curr_start = self.start_times[self.idx]
        curr_end = self.end_times[self.idx]

        main_start = self.start_times[self.main_idx]
        main_end = self.end_times[self.main_idx]

        if ((int(curr_start) > int(main_start)) and (int(curr_end) <= int(main_end))):
            self.state_four()
        else:
            self.state_two()

    # ----------------------------------------------------------------------------------------------

    def state_four(self):

        '''
            Update current channel list by whether values need to be turned
            on or turned off. Then update the return df, increment the index
            and go to condition 2.
        '''

        row = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        row_channel_list = row["channels"].values[0]

        # If these are the same, the logic is off
        assert(len(row_channel_list) != len(self.compare_channels))
        self.curr_channel_list = self.main_channel_list

        if(len(row_channel_list) > len(self.compare_channels)):
            # Turn on
            turn_on = list(set(row_channel_list) - set(self.compare_channels))
            self.curr_channel_list += turn_on
        else:
            # Turn off
            turn_off = list(set(self.compare_channels) - set(row_channel_list))
            self.curr_channel_list = [x for x in self.curr_channel_list if x not in turn_off]

        self.update_return_df(row)
        self.idx += 1

        self.condition_two()

    # ----------------------------------------------------------------------------------------------

    def condition_four(self):

        '''
            If next date range is right after previous date range, go to
            condition one. Otherwise, go to state 6. If there's no next
            then return.
        '''

        assert(self.idx != 0)
        if(self.idx == len(self.start_times)):
            return
        else:
            assert(self.end_times[self.idx-1] != self.start_times[self.idx])

            prev_end_dt = dt.strptime(self.end_times[self.idx-1], '%Y%m%d%H%M%S')
            next_start_dt = dt.strptime(self.start_times[self.idx], '%Y%m%d%H%M%S')
            diff = next_start_dt - prev_end_dt

            if diff == dt.timedelta(hours=6):
                self.condition_one()
            else:
                self.state_six()

    # ----------------------------------------------------------------------------------------------

    def state_six(self):

        '''
            Create new empty date range, update return df with new row, and then
            head over to state one. No update to the index.
        '''

        missing_time = {}

        prev_end = dt.strptime(self.end_times[self.idx-1], '%Y%m%d%H%M%S')
        miss_begin_time = prev_end + dt.timedelta(hours=6)
        missing_time['begin_time'] = (miss_begin_time).strftime('%Y%m%d%H%M%S')

        curr_start = dt.strptime(self.start_times[self.idx], '%Y%m%d%H%M%S')
        miss_end_time = curr_start - dt.timedelta(hours=6)
        missing_time['end_time'] = (miss_end_time).strftime('%Y%m%d%H%M%S')

        row = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        self.update_return_df(row, missing=True, missing_time=missing_time)

        self.condition_one()

    # ----------------------------------------------------------------------------------------------

    def get_instr_df(self):

        '''
            Returns the dataframe that the state machine generated!
        '''
        return self.return_df

    # ----------------------------------------------------------------------------------------------

    def update_return_df(self, row, no_comment=False, missing=False, missing_time={}):

        '''
            Updates the return df based on parameters
        '''

        if(missing):
            self.return_df = self.return_df.append({
               "sat": row["sat"].values[0],
               "start": missing_time['begin_time'],
               "end": missing_time['end_time'],
               "instr": row["instr"].values[0],
               "channel_num": 0,
               "channels": [],
               "comments": "missing for this period",
             }, ignore_index=True)

        elif(no_comment):
            self.return_df = self.return_df.append({
               "sat": row["sat"].values[0],
               "start": self.start_times[self.idx],
               "end": self.end_times[self.idx],
               "instr": row["instr"].values[0],
               "channel_num": len(self.curr_channel_list),
               "channels": self.curr_channel_list,
               "comments": ""
             }, ignore_index=True)

        else:
            self.return_df = self.return_df.append({
               "sat": row["sat"].values[0],
               "start": self.start_times[self.idx],
               "end": self.end_times[self.idx],
               "instr": row["instr"].values[0],
               "channel_num": len(self.curr_channel_list),
               "channels": self.curr_channel_list,
               "comments": row["comments"].values[0],
             }, ignore_index=True)


# --------------------------------------------------------------------------------------------------


def run_sat_db_process(git_out_dir):

    # Process satellite database files in GEOS-ESM and return dataframe
    # -----------------------------------------------------------------------

    git_repo = 'https://github.com/GEOS-ESM/GEOSana_GridComp.git'
    git_branch = 'develop'

    # Clone repo
    git_got(git_repo, git_branch, git_out_dir)
    path_to_sat_db = git_out_dir+'/GEOSaana_GridComp/GSI_GridComp/mksi/sidb/'

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


def read_sat_db(path_to_sat_db, column_names):

    # read data into a dataframe, throw line away if it starts with # or newline
    # ---------------------------------------------------------------------------
    filename = path_to_sat_db + 'active_channels.tbl'
    df = pd.DataFrame(columns=column_names)

    file = open(filename, 'r')
    lines = file.readlines()

    # Read blindly into an array, throw line away if it starts with # or newline
    idx = 0
    for line in lines:
        line_parts = line.split()
        if(line_parts):

            if(line_parts[0][0] != '#' and line_parts[0][0] != '\n'):

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

                if(comment_present):
                    channel_list = line_parts[7:comment_present]
                    comment = line_parts[comment_present:]
                    comment_str = ' '.join(comment)
                    if(len(comment_str) != 1):  # Accounting for no comment
                        df['comments'][idx] = comment_str
                else:
                    channel_list = line_parts[7:]

                df['channels'][idx] = channel_list
                idx += 1

    return df


# --------------------------------------------------------------------------------------------------
