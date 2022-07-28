from swell.configuration.configuration import return_configuration_path
import os

def retrieve_obs_list:
    obs_ops_path = return_configuration_path()+'/observation_operators/'
    obs_ops_list = []

    for f_name in os.listdir(obs_ops_path):
        if f_name.endswith('.yaml'):
            obs_name = os.path.splitext(f_name)[0]
            obs_name = obs_name.replace('_', ' ')
            obs_ops_list.append(obs_name)

    return obs_ops_list
