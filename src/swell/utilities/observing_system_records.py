import os
import yaml
import pandas as pd
import numpy as np
import datetime as dt
from swell.utilities.sat_db_utils import read_sat_db
from swell.utilities.instr_state_machine import InstrStateMachine


def format_date(old_date):
    date = dt.datetime.strptime(old_date, '%Y%m%d%H%M%S')
    return date.isoformat()


class ObservingSystemRecords:

    def __init__(self, root_directory):
        self.column_names = ['sat', 'start', 'end',
                             'instr', 'channel_num',
                             'channels', 'comments']
        self.df = pd.DataFrame(columns=self.column_names)
        self.obs_registry = []

        # Location where directories containing observing system records are located
        self.root_directory = root_directory

    def parse_records(self, path_to_records):
        # Only save satellites that are in list
        org_df = read_sat_db(path_to_records, self.column_names)
        sat_list = np.unique(org_df['sat'].values)
        for sat in sat_list:
            sat_df = org_df.loc[org_df['sat'] == sat]
            instr_list = np.unique(sat_df['instr'].values)

            for instr in instr_list:
                instr_df = sat_df.loc[sat_df['instr'] == instr]
                state_machine = InstrStateMachine(instr_df)
                state_machine.run()
                new_instr_df = state_machine.get_instr_df()
                self.df = pd.concat([self.df, new_instr_df], ignore_index=True)
                self.obs_registry.append(instr+'_'+sat)


    def save_yamls(self, output_dir, observation_list=None):

        if not observation_list:
            observation_list = self.obs_registry

        # Switch output directory to root/radiances

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        sat_list = np.unique(self.df['sat'].values)
        for sat in sat_list:
            df = self.df.loc[self.df['sat'] == sat]
            instr_list = np.unique(df['instr'].values)
            sat_dict = {}

            for instr in instr_list:
                sat_dict = {}
                instr_df = df.loc[df['instr'] == instr]

                compare_name = instr+'_'+sat
                if compare_name in observation_list:

                    field_list = []
                    for idx, row in instr_df.iterrows():
                        row_dict = {}
                        row_dict['begin date'] = format_date(row['start'])
                        row_dict['end date'] = format_date(row['end'])
                        row_dict['channels'] = row['channels']
                        if (row['comments']):
                            row_dict['comments'] = row['comments']
                        else:
                            row_dict['comments'] = 'no comment'
                        field_list.append(row_dict)

                    sat_dict[instr] = field_list

                    with open(output_dir+'/'+instr+'_'+sat+'.yaml', 'w') as file:
                        yaml.dump(sat_dict, file)

