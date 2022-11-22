# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
import datetime
import os
import yaml

from swell.swell_path import get_swell_path

# --------------------------------------------------------------------------------------------------


class PrepConfigBase(ABC):

    def __init__(self, logger, dictionary_file):

        # Store a logger for all to use
        self.logger = logger

        # Get the path and filename of the dictionary
        self.directory = os.path.join(get_swell_path(), 'suites')
        self.filename = os.path.splitext(os.path.basename(dictionary_file))[0]

        # Dictionary
        self.dictionary = self.read_dictionary_file(dictionary_file)

        # Keep track of the model, atmosphere, ocean etc
        self.model = None

        # Extension to use for dictionary files
        self.dictionary_extension = '.yaml'

        # Experiment dictionary to be created and used in swell
        self.experiment_dict = {}

        # Comment dictionary to be created and used to add comments to config file
        self.comment_dict = {}

        # Dictionary validation things
        self.valid_types = ['string', 'iso-datetime', 'iso-duration', 'string-drop-list',
                            'string-check-list', 'file-drop-list', 'file-check-list', 'boolean']

        # Disallowed element types
        self.dis_elem_types = [datetime.datetime, datetime.date]

    # ----------------------------------------------------------------------------------------------

    def append_directory_and_filename(self, sub_dict_name):

        self.directory = os.path.join(self.directory, sub_dict_name)
        self.filename = self.filename + '-' + sub_dict_name

    # ----------------------------------------------------------------------------------------------

    def subtract_directory_and_filename(self):

        self.directory = os.path.dirname(self.directory)
        self.filename = '-'.join(self.filename.split('-')[0:-1])

    # ----------------------------------------------------------------------------------------------

    def open_dictionary(self):

        # Append the filename according the type of files
        filename_ext = os.path.join(self.directory, self.filename + self.dictionary_extension)

        # Open file into dictionary
        dictionary = self.read_dictionary_file(filename_ext)

        # Check that dictionary contained something
        if dictionary is None:
            self.logger.abort(f'Dictionary at {filename_ext} returned {None} when opened')

        return dictionary

    # ----------------------------------------------------------------------------------------------

    def read_dictionary_file(self, dictionary_file):

        # Open file and load as dictionary
        with open(dictionary_file, 'r') as dictionary_file_open:
            dictionary = yaml.safe_load(dictionary_file_open)

        return dictionary

    # ----------------------------------------------------------------------------------------------

    def validate_dictionary(self, dictionary):

        # Check for required key
        required_keys = ['default_value', 'prompt', 'type']
        for required_key in required_keys:
            if required_key not in dictionary.keys():
                self.logger.abort(f'Each section of the suites config files must contain the key ' +
                                  f'\'{required_key}\'. Offending dictionary: \n {dictionary}')

        # Check that type is supported
        type = dictionary['type']
        if type not in self.valid_types:
            self.logger.abort(f'Dictionary has type \'{type}\' that is not one of the supported ' +
                              f'types: {self.valid_types}. Offending dictionary: \n {dictionary}')

    # ----------------------------------------------------------------------------------------------

    def update_model(self, model):

        if model is None:
            self.model = None
        else:
            self.model = model

            # If models list not already in the dictionary added
            if 'models' not in self.experiment_dict.keys():
                self.experiment_dict['models'] = {}

            # If specific model dictionary not added to the list of model then add it
            if self.model not in self.experiment_dict['models'].keys():
                self.experiment_dict['models'][self.model] = {}

    # ----------------------------------------------------------------------------------------------

    def add_to_experiment_dictionary(self, key, element_dict):

        # Set the element
        # ---------------
        element = element_dict['default_value']
        prompt = element_dict['prompt']

        # Validate the element
        # --------------------

        # Ensure always a list to make following logic not need to check if list or not
        if not isinstance(element, list):
            element_items = [element]
        else:
            element_items = element

        # Check for disallowed element types
        for element_item in element_items:
            element_item_type = type(element_item)
            for dis_elem_type in self.dis_elem_types:
                if isinstance(element_item, dis_elem_type):
                    self.logger.abort(f'Element \'{element}\' has a type that is not permitted. ' +
                                      f'Type is \'{dis_elem_type}\'. Try replacing with a string ' +
                                      f'in the configuration file.')

        # Validate the key
        # ----------------

        # Ensure there are no spaces in the key
        if ' ' in key:
            self.logger.abort(f'Key \'{key}\' contains a space. For consistency across the ' +
                              f'configurations please avoid spaces and instead use _ if needed.')

        # Check that dictionary does not already contain the key
        if key in self.experiment_dict.keys():
            self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')

        # Make sure the element was not already added
        # -------------------------------------------
        if self.model is None:
            if key in self.experiment_dict.keys():
                self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')
        else:
            if key in self.experiment_dict['models'][self.model].keys():
                self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')

        # Add element
        # -----------
        if self.model is None:
            self.experiment_dict[key] = element
        else:
            self.experiment_dict['models'][self.model][key] = element

        # Add option
        # ----------
        if self.model is None:
            option_key = key
        else:
            if 'models' not in self.comment_dict.keys():
                self.comment_dict['models'] = 'Options for individual model components'
            if 'models.' + self.model not in self.comment_dict.keys():
                self.comment_dict['models.' + self.model] = f'Options for the {self.model} ' + \
                                                            f'model component'
            option_key = 'models.' + self.model + '.' + key
        self.comment_dict[option_key] = prompt

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self):
        pass
        # The subclass has to implement an execute method since this is how it is called into
        # action.


# --------------------------------------------------------------------------------------------------
