import pandas as pd
import numpy as np


def check_end_time(end_time: str) -> str:

    ''' Checks end times for 24 hour strings and converts them to 18 '''

    hour = end_time[8:10]
    if (hour == '24'):
        # Subtract 6 hours
        new_end_time = str(int(end_time) - 60000)
        return new_end_time
    else:
        return end_time


class GSIRecordParser:

    def __init__(self) -> None:
        self.instr_df = None
        self.return_df = None
        self.sat = None
        self.instr = None

    def get_channel_list(self, start) -> list:
        channel_list = []
        rows = self.instr_df.loc[self.instr_df["start"] == start]
        for row_ch_list in rows["channels"].values:
            ch_list = eval(row_ch_list)
            channel_list.extend(ch_list)

        channel_list = list(set(channel_list))
        channel_list.sort(key=int)
        return channel_list

    def run(self, instr_df: pd.core.frame.DataFrame) -> None:

        # Save instrument dataframe
        self.instr_df = instr_df

        # Save satellite and instrument name
        self.sat = self.instr_df.iloc[0]['sat']
        self.instr = self.instr_df.iloc[0]['instr']

        # Initialize return dataframe
        self.return_df = pd.DataFrame(columns=list(instr_df.columns.values))

        # Create lists for start and end times
        end_times = []
        start_times = list(np.unique(self.instr_df['start'].values))
        start_times.sort(key=int)
        for start in start_times:
            end_times.append(self.instr_df.loc[self.instr_df['start'] == start]['end'].values[0])

        done = []
        for idx in range(len(start_times)):
            main_start = start_times[idx]
            main_end = end_times[idx]

            # If time has already been processed, then skip
            if main_start in done:
                continue

            start_df = self.instr_df.loc[self.instr_df['start'] == main_start]
            if (len(start_df) == 1):
                # Only one row to process
                channel_list = eval(start_df['channels'].values[0])
                comment = start_df['comments'].values[0]
                self.update_return_df(main_start, main_end, channel_list, comment)
                done.append(main_start)

            elif len(np.unique(start_df['end'].values)) == 1:
                # Collect channels and update dataframe with row
                channel_list = self.get_channel_list(main_start)
                self.update_return_df(main_start, main_end, channel_list, '')
                done.append(main_start)

            else:
                # Collect all channels for main start time
                channel_list = self.get_channel_list(main_start)

                inner_start = []
                inner_end = []
                # Get list of remaining start times that fall in range of start and end
                for inner_idx in range(idx+1, len(start_times)):
                    if (int(start_times[inner_idx]) >= int(main_start)) and \
                       (int(start_times[inner_idx]) <= int(main_end)):
                        inner_start.append(start_times[inner_idx])
                        inner_end.append(end_times[inner_idx])

                # Update df for start to first start with all channels
                new_end = str(int(inner_start[0]))
                self.update_return_df(main_start, new_end, channel_list, '')

                # Get channel list for main start/ main end time
                row_channel_list = start_df.loc[start_df["end"] != main_end]["channels"].values[0]

                for inner_idx in range(len(inner_start)):
                    # Compare channels from next time range
                    row = self.instr_df.loc[self.instr_df["start"] == inner_start[inner_idx]]
                    compare_channels = row["channels"].values[0]

                    # Turn channels on or off
                    if (len(row_channel_list) > len(compare_channels)):
                        # Turn off
                        turn_off = list(set(row_channel_list) - set(compare_channels))
                        channel_list = [x for x in channel_list if x not in turn_off]
                    else:
                        # Turn on
                        turn_on = list(set(compare_channels) - set(row_channel_list))
                        channel_list += turn_on

                    # Update row
                    comment = row['comments'].values[0]
                    # pass dictionary to update return df
                    self.update_return_df(inner_start[inner_idx], inner_end[inner_idx],
                                          channel_list, comment)
                    done.append(inner_start[inner_idx])

    def update_return_df(self, start: str, end: str, channel_list: list, comment: str) -> None:

        # Fix end time if on the 24 hour mark
        end = check_end_time(end)

        new_row = pd.DataFrame.from_dict({
                  'sat': [self.sat],
                  'start': [start],
                  'end': [end],
                  'instr': [self.instr],
                  'channel_num': [len(channel_list)],
                  'channels': [channel_list],
                  'comments': [comment]})

        self.return_df = pd.concat([self.return_df, new_row], ignore_index=True)

    def get_instr_df(self) -> pd.core.frame.DataFrame:

        ''' Returns the dataframe that the state machine generated! '''

        return self.return_df
