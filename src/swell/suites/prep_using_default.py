# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.suites.prep_using_base import PrepUsingBase


# --------------------------------------------------------------------------------------------------

def dictionary_lopper(input_dictionary, experiment_dict):

    for key in input_dictionary:

        # Extract type
        type = input_dictionary[key]['type']

        # If the type is not another file add to dictionary
        if 'file' not in type:
            experiment_dict[key] = input_dictionary[key]['default_value']
        else:
            print('Found a dict')
            subdir = input_dictionary[key]['default_value']
            with open(os.path.join(subdir, 'suites-' + subdir + '.yaml'), 'r') as ymlfile:
                sub_dict = yaml.safe_load(ymlfile)
            experiment_dict = dictionary_lopper(sub_dict, experiment_dict)

    return experiment_dict


# --------------------------------------------------------------------------------------------------


class PrepUsingDefault(PrepUsingBase):

    def execute(self, top_level_dictionary):

        self.logger.info('This is where default will do its work')

        experiment_dict = {}

        experiment_dict = dictionary_lopper(top_level_dictionary, experiment_dict)

        print(experiment_dict)

# --------------------------------------------------------------------------------------------------
