# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

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