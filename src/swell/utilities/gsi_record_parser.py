# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt


def check_end_times(end_times):

    ''' Checks end times for 24 hour strings and converts them to 18 '''

    new_end_times = []

    for end_time in end_times:
        # Note that python datetime does not allow for times with hour = 24
        hour = end_time[8:10]
        if (hour == '24'):
            # Subtract 6 hours
            tmp = int(end_time) - 60000
            new_end_times.append(str(tmp))
        else:
            new_end_times.append(end_time)

    return new_end_times


class GSIRecordParser:

    def __init__(self):

        ''' 
            This class employs a state machine algorithm to process raw data from GSI
            .tbl files. The different states work together to parse through an initial
            dataframe. The rows of the resulting dataframe correspond to clean entries
            for a given instrument and satellite.

        '''

        self.idx = None
        self.main_idx = None
        self.start_times = None
        self.end_times = None
        self.instr_df = None
        self.compare_channels = None
        self.curr_channel_list = None
        self.main_channel_list = None
        self.return_df = None

    def reset(self):
        self.idx = 0
        self.main_idx = 0
        self.start_times = []
        self.end_times = []
        self.compare_channels = []
        self.curr_channel_list = []
        self.main_channel_list = []

    def run(self, instr_df):

        '''
            Effectively state one of the state machine.
            Generates an ordered list of start times and corresponding
            end times. Checks the end times and then proceeds to condition one.

            input:
                instr_df = a dataframe containing raw data for a given satellite and
                           instrument
        '''

        self.reset()
        self.instr_df = instr_df
        self.return_df = pd.DataFrame(columns=list(instr_df.columns.values))

        self.start_times = list(np.unique(self.instr_df["start"].values))
        self.start_times.sort(key=int)
        for start in self.start_times:
            self.end_times.append(
                self.instr_df.loc[self.instr_df["start"] == start]["end"].values[0])

        self.end_times = check_end_times(self.end_times)
        self.condition_one()

    def condition_one(self):

        '''
            If there is one row for the date range, go to state 2. Otherwise,
            go to state 3.
        '''

        start_time_df = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        n_curr_start_rows = len(start_time_df)
        assert (n_curr_start_rows != 0)

        if (n_curr_start_rows == 1):
            self.curr_channel_list = start_time_df["channels"].values[0]
            self.state_two()
        else:
            self.state_three()

    def state_two(self):

        '''
            Update return_df with new row, increment idx, and then go to
            condition 4.
        '''

        row = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        self.update_return_df(row)
        self.idx += 1
        self.condition_four()

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

        if (other_end_times):

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

    def condition_two(self):

        '''
            If curr start/end is in main range, go to condition 3. Otherwise
            go to state 2
        '''

        # Return if end of df is reached
        if (self.idx == len(self.start_times)):
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

    def state_four(self):

        '''
            Update current channel list by whether values need to be turned
            on or turned off. Then update the return df, increment the index
            and go to condition 2.
        '''

        row = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        row_channel_list = row["channels"].values[0]

        # If these are the same, the logic is off
        assert (len(row_channel_list) != len(self.compare_channels))
        self.curr_channel_list = self.main_channel_list

        if (len(row_channel_list) > len(self.compare_channels)):
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

    def condition_four(self):

        '''
            If next date range is right after previous date range, go to
            condition one. Otherwise, go to state 6. If there's no next
            then return.
        '''

        assert (self.idx != 0)
        if (self.idx == len(self.start_times)):
            return
        else:
            assert (self.end_times[self.idx-1] != self.start_times[self.idx])

            prev_end_dt = dt.strptime(self.end_times[self.idx-1], '%Y%m%d%H%M%S')
            next_start_dt = dt.strptime(self.start_times[self.idx], '%Y%m%d%H%M%S')
            diff = next_start_dt - prev_end_dt

            if diff == datetime.timedelta(hours=6):
                self.condition_one()
            else:
                self.state_six()

    def state_six(self):

        '''
            Create new empty date range, update return df with new row, and then
            head over to state one. No update to the index.
        '''

        missing_time = {}

        prev_end = dt.strptime(self.end_times[self.idx-1], '%Y%m%d%H%M%S')
        miss_begin_time = prev_end + datetime.timedelta(hours=6)
        missing_time['begin_time'] = (miss_begin_time).strftime('%Y%m%d%H%M%S')

        curr_start = dt.strptime(self.start_times[self.idx], '%Y%m%d%H%M%S')
        miss_end_time = curr_start - datetime.timedelta(hours=6)
        missing_time['end_time'] = (miss_end_time).strftime('%Y%m%d%H%M%S')

        row = self.instr_df.loc[self.instr_df["start"] == self.start_times[self.idx]]
        self.update_return_df(row, missing=True, missing_time=missing_time)

        self.condition_one()

    def get_instr_df(self):

        ''' Returns the dataframe that the state machine generated! '''

        return self.return_df

    def update_return_df(self, row, no_comment=False,  missing=False, missing_time={}):

        ''' Adding rows to final dataframe that will be returned through get_instr_df '''

        # Updates the return df based on parameters
        if (missing):
            new_row = pd.DataFrame.from_dict({
                        'sat': [row["sat"].values[0]],
                        'start': [missing_time['begin_time']],
                        'end': [missing_time['end_time']],
                        'instr': [row['instr'].values[0]],
                        'channel_num': [0],
                        'channels': [[]],
                        'comments': ['missing for this period']})

        elif (no_comment):
            new_row = pd.DataFrame.from_dict({
                        'sat': [row["sat"].values[0]],
                        'start': [self.start_times[self.idx]],
                        'end': [self.end_times[self.idx]],
                        'instr': [row['instr'].values[0]],
                        'channel_num': [len(self.curr_channel_list)],
                        'channels': [self.curr_channel_list],
                        'comments': ['']})

        else:
            new_row = pd.DataFrame.from_dict({
                        'sat': [row["sat"].values[0]],
                        'start': [self.start_times[self.idx]],
                        'end': [self.end_times[self.idx]],
                        'instr': [row['instr'].values[0]],
                        'channel_num': [len(self.curr_channel_list)],
                        'channels': [self.curr_channel_list],
                        'comments': [row["comments"].values[0]]})

        self.return_df = pd.concat([self.return_df, new_row], ignore_index=True)
