# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.deployment.prep_config_base import PrepConfigBase


# --------------------------------------------------------------------------------------------------


class PrepConfigDefaults(PrepConfigBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, dictionary=None):

        # Set dictionary to use in this scope
        if dictionary is None:
            dictionary = self.dictionary

        for key in dictionary:

            # Element dictionary
            el_dict = dictionary[key]

            if key != 'fixed_options':

                # Validate the element dictionary
                self.validate_dictionary(el_dict)

                # Extract type
                type = el_dict['type']

                # If the type is not another file add to dictionary
                if 'file' not in type:

                    # Check that the key does not have a dependency
                    depends_flag = True
                    if 'depends' in el_dict.keys():
                        dep_key = el_dict['depends']['key']
                        dep_val = el_dict['depends']['value']
                        if self.experiment_dict[dep_key] != dep_val:
                            depends_flag = False

                    # In this case the key is not expected to refer to a sub dictionary but have
                    # everything needed in the elements dictionary
                    if depends_flag:
                        self.add_to_experiment_dictionary(key, el_dict)

                elif 'file-drop-list' in type:

                    # Add the choice to the dictionary
                    self.add_to_experiment_dictionary(key, el_dict)

                    # In this case the key refers to a single sub dictionary that involves opening
                    # that dictionary and recursively calling this routine.

                    # First append the directory and filename to denote moving to the sub dictionary
                    self.append_directory_and_filename(el_dict['default_value'])

                    # Open next level down dictionary and recursively add
                    self.execute(self.open_dictionary())

                    # As we come back from the sub dictionary subtract the directory and filename
                    self.subtract_directory_and_filename()

                elif 'file-check-list' in type:

                    # Add the choice to the dictionary
                    self.add_to_experiment_dictionary(key, el_dict)

                    # In this case the key asks the user to provide a list of items that correspond
                    # to sub dictionaries. Inside a loop this method is called recursively.
                    options = el_dict['default_value']
                    for option in options:

                        # If the key is models change the internal model to match this model
                        if key == 'model_components':
                            self.update_model(option)

                        self.append_directory_and_filename(option)
                        self.execute(self.open_dictionary())
                        self.subtract_directory_and_filename()

                        if key == 'model_components':
                            self.update_model(None)

            else:

                for fixed_key in el_dict:

                    self.add_to_experiment_dictionary(fixed_key, el_dict[fixed_key])

        return


# --------------------------------------------------------------------------------------------------
