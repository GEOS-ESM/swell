# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
import os
import yaml

from swell.suites.suites import return_suite_path

# --------------------------------------------------------------------------------------------------

class PrepUsingBase(ABC):

    def __init__(self, logger, dictionary_file):

        # Store a logger for all to use
        self.logger = logger

        # Get the path and filename of the dictionary
        self.directory = return_suite_path()
        self.filename = os.path.splitext(os.path.basename(dictionary_file))[0]

        # Dictionary
        self.dictionary = self.read_dictionary_file(dictionary_file)

        # Keep track of the model, atmosphere, ocean etc
        self.model = None

        # Extension to use for dictionary files
        self.dictionary_extension = '.yaml'

        # Experiment dictionary to be created by the subclass
        self.experiment_dict = {}

        # Dictionary validation things
        self.valid_types = ['string', 'iso-datetime', 'drop-list', 'check-list', 'file-drop-list',
                            'file-check-list']

    # ----------------------------------------------------------------------------------------------

    def append_directory_and_filename(self, subname):

        self.directory = os.path.join(self.directory, subname)
        self.filename = self.filename + '-' + subname

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
        required_keys = ['default_value', 'question', 'type']
        for required_key in required_keys:
            if required_key not in dictionary.keys():
                self.logger.abort(f'Each section of the suites config files must contain the key ' +
                                  f'\''+ required_key + '\'. Offending dictionary: \n {dictionary}')

        # Check that type is supported
        type = dictionary['type']
        if type not in self.valid_types:
            self.logger.abort(f'Dictionary has a type \'{type}\' that is not one of the supported ' +
                              f'types: {self.valid_types}. Offending dictionary: \n {dictionary}')

    # ----------------------------------------------------------------------------------------------

    def add_to_experiment_dictionary(self, key, element):

        # Check that dictionary does not already contain the key
        if key in self.experiment_dict.keys():
            self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')

        # Add element
        if self.model is None:
            self.experiment_dict[key] = element
        else:
            if self.model not in self.experiment_dict.keys():
                self.experiment_dict[self.model] = {}
            self.experiment_dict[self.model][key] = element

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self):
        pass
        # The subclass has to implement an execute method since this is how it is called into
        # action.

# --------------------------------------------------------------------------------------------------
