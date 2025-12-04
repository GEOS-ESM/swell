# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------

# Read observation_ioda_names.yaml
def get_ioda_names_list() -> list:
    with open(os.path.join(get_swell_path(), 'configuration', 'jedi',
                           'observation_ioda_names.yaml'), 'r') as f:
        ioda_dict = yaml.safe_load(f)

    ioda_names_list = ioda_dict['ioda instrument names']

    return ioda_names_list

# -------------------------------------------------------------------------------------------------


# Gets obs providers for each observation from observation_ioda_names.yaml
def get_provider_for_observation(observation: str, ioda_names_list: list) -> list:
    for sub_dict in ioda_names_list:
        if sub_dict['ioda name'] == observation:
            if 'provider' in sub_dict.keys():
                return str(sub_dict['provider'])
            else:
                self.logger.abort(f'No provider found for observation {observation} in ' +
                                  'observation_ioda_names.yaml')

# ------------------------------------------------------------------------------------------------


def ioda_name_to_long_name(ioda_name: str, logger: Logger) -> str:

    # Get configuration path
    jedi_configuration_path = os.path.join(get_swell_path(), 'configuration', 'jedi')

    # Insturment list yaml
    obs_ioda_names_file = os.path.join(jedi_configuration_path, 'observation_ioda_names.yaml')

    # Open file and convert to dictionary
    with open(obs_ioda_names_file, 'r') as obs_ioda_names_str:
        obs_ioda_names_dict = yaml.safe_load(obs_ioda_names_str)

    # Get the list of ioda instrument names
    obs_ioda_names = obs_ioda_names_dict['ioda instrument names']

    # Loop over list of valid names
    found = False
    for obs_ioda_name in obs_ioda_names:
        if ioda_name == obs_ioda_name['ioda name']:
            long_name = obs_ioda_name['full name']
            found = True
            break

    # Check something found
    if not found:
        logger.abort('In ioda_name_to_long_name the string \'' + ioda_name + '\' does not ' +
                     f'contain one of the valid instruments: {obs_ioda_names} . Additional ' +
                     'instruments can be added to swell/configuration/observation_ioda_names.yaml')

    # Return found value
    return long_name


# --------------------------------------------------------------------------------------------------
