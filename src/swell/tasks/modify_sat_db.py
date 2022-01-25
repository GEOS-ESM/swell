# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# ---------------------------------------------------------------------------

from tide.task_base import taskBase
from r2d2 import fetch

import os
import re
import sys
import time
import argparse
from datetime import datetime as dt
from tide.utils import run_sat_db_process
import itertools
import yaml

def ranges(i):
    for _, group in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        group = list(group)
        yield group[0][1], group[-1][1]

class ModifySatDb(taskBase):
  """Provides methods for modifying UFO Observation files with GEOS Sat DB

     Methods
     -------
     execute:
       Execution handle for this task.
  """

  def execute(self):

    """Modifies UFO yamls based on current cycle time

       Parameters
       ----------
         All inputs are extracted from the JEDI experiment file configuration.
         See the taskBase constructor for more information.

    """

    cfg = self.config

    time_window     = cfg.get('current_cycle')
    bundle          = cfg.get('bundle')
    obs = cfg.get('OBSERVATIONS')
    cycle_dt = dt.strptime(time_window,'%Y-%m-%dT%H:%M:%SZ')
    geos_sat_db_dir = cfg.get('geos_sat_db_root')
    use_sat_db_yaml = cfg.get('use_sat_db_yaml')
    sat_db_yaml_loc = geos_sat_db_dir + 'satdb_yamls/'

    # Get satellite database
    # -------------------------------

    #make git_out_dir if it doesn't exist
    try:
       os.makedirs(geos_sat_db_dir)
    except Exception:
       print('GEOS SAT DATABASE DIRECTORY IS ALREADY GENERATED')

    git_out_dir = geos_sat_db_dir + 'GEOSana_GridComp'

    if not use_sat_db_yaml:
        sat_db = run_sat_db_process(git_out_dir)

    # Loop over observation operators
    # -------------------------------
    for ob in obs:

      name = ob['obs space']['name']
      if '_' in name:
          sat_instr_list = name.split('_')
          instr = sat_instr_list[0]
          sat   = sat_instr_list[1]

          try:
             if use_sat_db_yaml:
                with open(sat_db_yaml_loc + sat + '.yaml', 'r') as file:
                   sat_dict = yaml.full_load(file)
                   instr_dict = sat_dict[instr]
                   instr_ind = 999
                   for ind in range(len(instr_dict)):
                      #convert begin and end times to datetimes
                      begin = dt.strptime(instr_dict[ind]['begin date'], '%Y-%m-%dT%H:%M:%S')
                      end   = dt.strptime(instr_dict[ind]['end date'], '%Y-%m-%dT%H:%M:%S')
                      if((cycle_dt >= begin) and (cycle_dt < end)):
                         instr_ind = ind
                   assert(instr_ind != 999)
                   instr_ch_list = instr_dict[ind]['channels']

             else:
                sat_df = sat_db.loc[sat_db['sat']==sat]
                instr_df = sat_df.loc[sat_df['instr']==instr]

                instr_ind = 999
                for ind in range(len(instr_df)):
                  #convert begin and end times to datetimes
                  begin = dt.strptime(instr_df['start'][ind], '%Y%m%d%H%M%S')
                  end   = dt.strptime(instr_df['end'][ind], '%Y%m%d%H%M%S')
                  if((cycle_dt >= begin) and (cycle_dt < end)):
                     instr_ind = ind
                assert(instr_ind != 999)
                instr_ch_list = instr_df['channels'][ind]


             instr_ch_list = [int(i) for i in instr_ch_list]
             ch_ranges = list(ranges(instr_ch_list))
             new_ch_str = ''
             for ch_range in ch_ranges:
                if(ch_range[0] != ch_range[1]):
                   new_ch_str += str(ch_range[0]) + '-' + str(ch_range[1]) + ' '
                else:
                   new_ch_str += str(ch_range[0]) + ' '
             new_ch_str = new_ch_str[0:-1]

             #find where the channel list is defined in the dict
             #replace it with new channel string
             yaml_file = bundle + '/ufo/ewok/jedi-geos/' + instr + '_' + sat + '.yaml'
             with open(yaml_file, 'r') as file:
                ufo_dict = yaml.full_load(file)
             ufo_dict['obs space']['channels'] = new_ch_str

             #Dump the yaml back out
             with open(yaml_file, 'w') as file:
               yaml.dump(ufo_dict, file, default_style=None)

          except:
             print('satellite {} and instrument {} are not in the satellite database'.format(sat, instr))
             continue
