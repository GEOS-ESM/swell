import os
import yaml
import pandas as pd
import numpy as np
import datetime as dt
from swell.utilities.gsi_record_parser import GSIRecordParser

# --------------------------------------------------------------------------------------------------


def format_date(old_date):

    ''' Formatting date into expected template '''
    date = dt.datetime.strptime(old_date, '%Y%m%d%H%M%S')
    return date.isoformat()

# --------------------------------------------------------------------------------------------------


def read_sat_db(path_to_sat_db, column_names):

    '''
        Reading GSI observing system records row by row into
        a pandas dataframe to be used by the gsi_record_parser
    '''

    filename = path_to_sat_db
    df = pd.DataFrame(columns=column_names)

    file = open(filename, 'r')
    lines = file.readlines()

    # Read blindly into an array, throw line away if it starts with # or newline
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
                    # Accounting for no comment
                    if (len(comment_str) != 1):
                        df['comments'][idx] = comment_str
                else:
                    channel_list = line_parts[7:]

                df['channels'][idx] = channel_list
                idx += 1
    return df

# --------------------------------------------------------------------------------------------------


class ObservingSystemRecords:

    '''
        Class handles calls to parse GSI observing system records. Parsed
        records are saved internally in dataframes and can be outputted into
        yaml files.
    '''

    def __init__(self):
        self.column_names = ['sat', 'start', 'end',
                             'instr', 'channel_num',
                             'channels', 'comments']
        self.active_df = None
        self.available_df = None
        self.obs_registry = []

    def parse_records(self, path_to_sat_db):

        '''
            This method reads in the active.tbl and available.tbl files
            from GEOSAna and loads them into dataframes. These dataframes
            are parsed using GSIRecordParser to get the final dataframes.
        '''

        parser = GSIRecordParser()
        channel_types = ['active', 'available']
        for channel_type in channel_types:
            df = pd.DataFrame(columns=self.column_names)
            path_to_records = os.path.join(path_to_sat_db, channel_type + '_channels.tbl')

            org_df = read_sat_db(path_to_records, self.column_names)
            sat_list = np.unique(org_df['sat'].values)
            for sat in sat_list:
                sat_df = org_df.loc[org_df['sat'] == sat]
                instr_list = np.unique(sat_df['instr'].values)

                for instr in instr_list:
                    instr_df = sat_df.loc[sat_df['instr'] == instr]
                    parser.run(instr_df)
                    new_instr_df = parser.get_instr_df()
                    df = pd.concat([df, new_instr_df], ignore_index=True)
                    if instr+'_'+sat not in self.obs_registry:
                        self.obs_registry.append(instr+'_'+sat)

            if channel_type == 'active':
                self.active_df = df
            elif channel_type == 'available':
                self.available_df = df
            else:
                # logger assert abort?
                print('record parsing unavailable for this type')

    def save_yamls(self, output_dir, observation_list=None):

        '''
            Fields are taken from the internal dataframes populated
            by parse_records and saved to yaml files.
        '''

        if not observation_list:
            observation_list = self.obs_registry

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # Assume that active and available channels have corresponding sat/instr fields
        sat_list = np.unique(self.active_df['sat'].values)
        for sat in sat_list:
            active_df = self.active_df.loc[self.active_df['sat'] == sat]
            available_df = self.available_df.loc[self.available_df['sat'] == sat]
            instr_list = np.unique(active_df['instr'].values)

            for instr in instr_list:
                sat_dict = {}
                instr_active_df = active_df.loc[active_df['instr'] == instr]
                instr_available_df = available_df.loc[available_df['instr'] == instr]

                compare_name = instr+'_'+sat
                if compare_name in observation_list:

                    active_field_list = []
                    for idx, row in instr_active_df.iterrows():
                        row_dict = {}
                        row_dict['begin date'] = format_date(row['start'])
                        row_dict['end date'] = format_date(row['end'])
                        row_dict['channels'] = row['channels']
                        if (row['comments']):
                            row_dict['comments'] = row['comments']
                        else:
                            row_dict['comments'] = 'no comment'
                        active_field_list.append(row_dict)

                    available_field_list = []
                    for idx, row in instr_available_df.iterrows():
                        row_dict = {}
                        row_dict['begin date'] = format_date(row['start'])
                        row_dict['end date'] = format_date(row['end'])
                        row_dict['channels'] = row['channels']
                        available_field_list.append(row_dict)

                    sat_dict['available'] = available_field_list
                    sat_dict['active'] = active_field_list

                    with open(output_dir+'/'+instr+'_'+sat+'_channel_info.yaml', 'w') as file:
                        yaml.dump(sat_dict, file)
