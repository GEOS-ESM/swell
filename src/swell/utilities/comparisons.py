# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from ruamel.yaml import YAML
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------

def comparison_tags(pathspecs: list | dict,
                    logger: Logger) -> dict:
    
    '''Check for the correct number of experiments. Automatically assign tags
    if they are not already assigned.
    
    The experiment in the first position will be given the label 'CTL', and
    the experiment in the second position will be given the label 'EXP'. 
    
    Parameters:
    pathspecs: list or dictionary specifying the experiments to be compared.
    
    Returns:
    Dictionary mapping tags to experiments. If the input is a dictionary,
    no changes will be made.'''
    
    if len(pathspecs) != 2:
        logger.abort(f'Exactly 2 experiments should be specified.')

    if isinstance(pathspecs, list):
        pathspecs_out = {}
        pathspecs_out['CTL'] = pathspecs[0]
        pathspecs_out['EXP'] = pathspecs[1]
    else:
        pathspecs_out[str(pathspecs.keys()[0])] = pathspecs.values()[0]
        pathspecs_out[str(pathspecs.keys()[1])] = pathspecs.values()[1]

    return pathspecs_out

# --------------------------------------------------------------------------------------------------

def experiment_ids(experiment_paths) -> tuple:
    '''Get experiment ids from path's experiment.yaml

    Arguments:
    experiment_paths: List of two experiment paths

    Returns:
    Tuple (experiment_id_1, experiment_id_2)
    '''

    experiment_path_1 = experiment_paths[0]
    experiment_path_2 = experiment_paths[1]

    yaml = YAML(typ='safe')
    
    with open(experiment_path_1, 'r') as f:
        experiment_dict_1 = yaml.load(f)

    experiment_id_1 = experiment_dict_1['experiment_id']

    with open(experiment_path_2, 'r') as f:
        experiment_dict_2 = yaml.load(f)

    experiment_id_2 = experiment_dict_2['experiment_id']

    return experiment_id_1, experiment_id_2

# --------------------------------------------------------------------------------------------------