# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from swell.deployment.platforms import get_tasks_per_node

import os

class PrepSuite():

  def __init__(self, logger, exp_dict):

    # Copy of logger
    # --------------
    self.logger = logger

    # First update the scheduling dictionary, overwriting default with task specific values
    # -------------------------------------------------------------------------------------
    self.update_scheduling_dictionary(exp_dict)

    # Convert to jinja dictionary that can be inserted into flow.cylc
    # ---------------------------------------------------------------
    self.convert_dict_to_jinja2()


  # ------------------------------------------------------------------------------------------------


  def update_scheduling_dictionary(self, exp_dict):


    # Extract suite and scheduling dictionaries
    # -----------------------------------------
    self.suite_path = exp_dict['suite_dir']
    self.suite_dict = exp_dict['suite']
    scheduling_dicts = self.suite_dict['scheduling']


    # Loop and get default dictionary
    # -------------------------------
    for scheduling_dict in scheduling_dicts:
      if scheduling_dict['task'] == 'Default':
        def_scheduling_dict = scheduling_dict

    # Get default tasks per node depending on platform/constraint
    dtpn = get_tasks_per_node(def_scheduling_dict['platform'], def_scheduling_dict['constraint'])
    def_scheduling_dict['ntasks_per_node'] = dtpn


    # Loop and set task dictionaries
    # ------------------------------
    scheduling_dicts_new = []
    for scheduling_dict in scheduling_dicts:

      if scheduling_dict['task'] != 'Default':
        # Merge the default and task specific values
        task_merged = ({**def_scheduling_dict, **scheduling_dict})
        #scheduling_dicts_new.append(task_merged)
        self.suite_dict[task_merged['task']] = task_merged

    del self.suite_dict['scheduling']

    # Overwrite suite dictionary
    # --------------------------
    #self.suite_dict['scheduling'] = scheduling_dicts_new


  # ------------------------------------------------------------------------------------------------


  def convert_dict_to_jinja2(self):

    # Convert dictionary to jinja2 like string
    suite_dict_jinja2_str = '{% set suite_properties = '+str(self.suite_dict)+'%}'

    # Write jinja2 dictionary to file in suite directory
    with open(os.path.join(self.suite_path,'suite.jinja2'),'w') as suite_jinja2:
      suite_jinja2.write(suite_dict_jinja2_str)


  # ------------------------------------------------------------------------------------------------
