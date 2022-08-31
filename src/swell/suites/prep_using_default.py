# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.suites.prep_using_base import PrepUsingBase

# --------------------------------------------------------------------------------------------------

class PrepUsingDefault(PrepUsingBase):

    # ----------------------------------------------------------------------------------------------

    def __init__(self, input_file):

        # Get the path and filename of the dictionary
        self.directory = os.path.dirname(input_file)
        self.filename = os.path.basename(input_file)

    # ----------------------------------------------------------------------------------------------

    def append_directory_and_filename(self, subname):

        self.directory = os.path.join(self.directory, subname)
        self.filename = self.filename + '-' + subname

    # ----------------------------------------------------------------------------------------------

    def subtract_directory_and_filename(self, subname):

        self.directory = os.path.basename(self.directory)
        self.filename = '-'.join(self.filename.split('-')[0:-1])

   # ----------------------------------------------------------------------------------------------

    def open_dictionary(self):

        # Append the filename according the type of files
        filename_ext = self.filename + '.yaml'

        with open(os.path.join(self.directory, filename_ext), 'r') as opened_file:
            dict = yaml.safe_load(opened_file)

        return dict

    # ----------------------------------------------------------------------------------------------

    def execute(self, dict, exp_dict):

        for key in dict:

            # Element dictionary
            el_dict = dict[key]

            # Extract type
            type = el_dict['type']

            # If the type is not another file add to dictionary
            if 'file' not in type:
                # In this case the key is not expected to refer to a sub dictionary but have
                # everything needed in the elements dictionary
                exp_dict[key] = el_dict['default_value']
            elif 'file-drop-list' in type:
                # In this case the key refers to a single sub dictionary that involves opening that
                # dictionary and recursively calling this routine.

                # First append the directory and filename to denote moving to the sub dictionary
                self.append_directory_and_filename(el_dict['default_value'])

                # Open next level down dictionary and recursively add
                exp_dict = dictionary_looper(self.open_dictionary(), exp_dict)

            elif 'file-check-list' in type:
                # In this case the key asks the user to provide a list of items that correspond to
                # sub dictionaries. Inside a loop this method is called recursively.

        return exp_dict

# --------------------------------------------------------------------------------------------------
