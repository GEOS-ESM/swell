# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.configuration.configuration import return_configuration_path


# --------------------------------------------------------------------------------------------------


def find_instrument_from_string(full_string, logger):

    # Get configuration path
    configuration_path = return_configuration_path()

    # Insturment list yaml
    obs_ioda_names_file = os.path.join(configuration_path, 'observation_ioda_names.yaml')

    # Open file and convert to dictionary
    with open(obs_ioda_names_file, 'r') as obs_ioda_names_str:
        obs_ioda_names_dict = yaml.safe_load(obs_ioda_names_str)

    # Get the list of ioda instrument names
    obs_ioda_names = obs_ioda_names_dict['ioda instrument names']

    # Set default outputs
    key = None
    variable = None

    # Loop over list of valid names
    obs_ioda_name_found = None
    for obs_ioda_name in obs_ioda_names:
        if obs_ioda_name in full_string:
            obs_ioda_name_found = obs_ioda_name

    # Check something found
    if obs_ioda_name_found is None:
        logger.abort('In find_instrument_from_string the string ' + full_string + 'does not ' +
                     f'contain one of the valid instruments: {obs_ioda_names} . Additional ' +
                     'instruments can be added to swell/configuration/observation_ioda_names.yaml')

    # Return found value
    return obs_ioda_name_found


# --------------------------------------------------------------------------------------------------
