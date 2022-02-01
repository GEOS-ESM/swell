# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import os
import sys
import yaml
import shutil
import re
from string import *


# --------------------------------------------------------------------------------------------------


class yaml_exploder():

    def __init__(self, exp_id_dir, suite_dir, dir_dict):
        self.dir_dict = dir_dict
        self.experiment_id_dir = exp_id_dir
        self.suite_dir = suite_dir
        self.exp_file_path = os.path.join(exp_id_dir,
                                          'experiment_{}.yaml'.format(self.dir_dict['experiment']))

    # ----------------------------------------------------------------------------------------------

    def boom(self):
        '''
        Expands the experiment yaml file into a readable expanded yaml file that the workflow engine
        will use
        '''
        # Open the copied experiment yaml
        with open(self.exp_file_path, 'r') as yamlfile:
            self.target = yaml.safe_load(yamlfile)

        # Append the environmental directories to the top of the experiment file dictionary
        self.target = self.add_env_dirs(self.dir_dict)

        # Loop over experiment yaml and expand
        for k in self.target.keys():
            param_list = self.target[k]
            # Checks for yaml file type, and if there is a list of files or single file. List type
            # requires an additional loop to tease out individual files. Alternative would be to
            # check if something is a string, if yes, then force into list. However, that may cause
            # problems later

            # Check if key is STAGE, then get the pre-pend paths that we'll use later in the
            # expanded yaml
            if 'STAGE' in k:
                self.stage_setter(param_list)

            if 'yaml::' in str(param_list) and isinstance(param_list, list):
                exp_list = []
                for p in param_list:
                    # Call the pull_yaml function
                    big_yaml = self.pull_yaml(p)
                    # Append the dictionary to the expanded list
                    exp_list.append(big_yaml)
                # Write the expanded list element to the original dictionary key
                self.target[k] = exp_list
            elif 'yaml::' in str(param_list):
                # Call the pull_yaml function
                big_yaml = self.pull_yaml(param_list)
                # Assign the expanded yaml to the original ditionary key
                self.target[k] = big_yaml

        # Prepend stage paths to stage items
        self.stage_filler()

    # ----------------------------------------------------------------------------------------------

    def write(self):

        # Write out the final expanded yaml file
        with open(os.path.join(self.suite_dir, 'experiment-filled.yaml'), 'w') as outfile:
            yaml.dump(self.target, outfile, default_flow_style=False)

    # ----------------------------------------------------------------------------------------------

    def check_wilds(self, param):
        '''
        Checks for wildcard variables that need to be replaced to find the correct data file
        '''
        for item in ['layout', 'vertical_resolution', 'horizontal_resolution']:
            if '$({})'.format(item) in param:
                param = param.replace('$({})'.format(item), self.target[item])
        return param

    # ----------------------------------------------------------------------------------------------

    def add_env_dirs(self, dir_dict):
        '''
        Add the environmental directories to the experiment file.
        '''
        exp_root = dir_dict['experiment_root']
        dir_dict.update(self.target)
        dir_dict.update({'experiment_root': exp_root})

        return dir_dict

    # ----------------------------------------------------------------------------------------------

    def pull_yaml(self, param):
        '''
        Takes a yaml line in the experiment file and replaces it with the opened yaml file.
        '''
        # Set useful directory path variables
        stage_dir = self.dir_dict['stage_dir']
        bundle_dir = self.dir_dict['bundle']
        run_dir = os.path.join(self.dir_dict['experiment_dir'], '{{current_cycle}}')

        # Get the path to the yaml files and open as text files
        p = param.split('yaml::')[1]
        p = p.replace('$(bundle)', bundle_dir)
        p_path = self.check_wilds(p)
        with open(p_path, 'r') as yamlfile:
            big_yaml = yamlfile.read()

        # Replace the directories and experiment ID variables specific to this run
        big_yaml = replace_vars(big_yaml, stage_dir=stage_dir,
                                experiment_id_dir=self.experiment_id_dir,
                                run_dir=run_dir, experiment=self.dir_dict['experiment'])
        big_yaml = yaml.safe_load(big_yaml)
        return big_yaml

    # ----------------------------------------------------------------------------------------------

    def stage_setter(self, param_list):
        self.stage_path_list = []
        if isinstance(param_list, list):
            for p in param_list:
                p_path = p.split('yaml::')[1]
                pre_path = os.path.dirname(p_path)
                self.stage_path_list.append(pre_path)
        else:
            raise Exception('Stage value must be a yaml list in experiment yaml.')

        return None

    # ----------------------------------------------------------------------------------------------

    def stage_filler(self):
        stage_list = self.target['STAGE']
        for i, stage_item in enumerate(stage_list):
            copy_list = stage_item['copy_files']['directories']
            stage_path_item = self.stage_path_list[i]
            for j, copy_item in enumerate(copy_list):
                copy_item[0] = prepend_path(copy_item[0], stage_path_item)
                self.target['STAGE'][i]['copy_files']['directories'][j] = copy_item


# --------------------------------------------------------------------------------------------------


def replace_vars(s, **defs):
    '''
    Replaces $() variables with the provided def
    '''
    expr = s

    # Resolve {{var}} and $(var) first
    for var in re.findall(r'{{(\w+)}}', expr):
        if var in defs:
            expr = re.sub(r'{{'+var+r'}}', defs[var], expr)
    for var in re.findall(r'\$\((\w+)\)', expr):
        if var in defs:
            expr = re.sub(r'\$\('+var+r'\)', defs[var], expr)

    # Recursively resolve shell variables
    s_interp = Template(expr).safe_substitute(defs)

    if s_interp != s:
        s_interp = replace_vars(s_interp, **defs)

    return s_interp


# --------------------------------------------------------------------------------------------------


def prepend_path(s, prepath):
    '''
    prepend repo path to src directory from stage yaml
    '''
    s_list = s.split('/')
    parent_count = s_list.count('..')
    for i in range(parent_count):
        prepath = os.path.dirname(prepath)
        s_list.remove('..')
    s = ('/').join(s_list)
    new_s = os.path.join(prepath, s)
    return new_s
