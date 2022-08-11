# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


import os
import yaml
import click
import numpy as np
import pandas as pd

from datetime import datetime as dt

from swell.utilities.git_utils import git_got
from swell.utilities.sat_db_utils import run_sat_db_process


def make_yamls(final_df, output_dir):

    '''
        Uses the dataframe created by sat_db_processing
        to write out yaml files
    '''

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    sat_list = np.unique(final_df['sat'].values)
    for sat in sat_list:

        df = final_df.loc[final_df['sat'] == sat]
        instr_list = np.unique(df['instr'].values)
        sat_dict = {}

        for instr in instr_list:

            sat_dict[instr] = {}
            instr_df = df.loc[df['instr'] == instr]

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

        with open(output_dir+'/'+sat+'.yaml', 'w') as file:
            yaml.dump(sat_dict, file)


def format_date(old_date):

    '''
        Formatting datetime object
    '''

    date = dt.strptime(old_date, '%Y%m%d%H%M%S')
    return date.isoformat()


@click.command()
@click.argument('config')
def main(config):

    with open(config, 'r') as ymlfile:
        config_dict = yaml.safe_load(ymlfile)
    user = os.environ['USER']
    geos_sat_db_root = config_dict['geos_sat_db_root'].replace('${USER}', user)

    try:
        os.makedirs(geos_sat_db_root)
    except Exception:
        print('SATELLITE DATABASE DIRECTORY IS ALREADY GENERATED')

    yaml_out_dir = geos_sat_db_root + '/satdb_yamls'
    git_out_dir = geos_sat_db_root + '/GEOSana_GridComp'

    # run sat db processing util
    processed_data = run_sat_db_process(git_out_dir)

    # create yamls
    make_yamls(processed_data, yaml_out_dir)


if __name__ == '__main__':
    main()
