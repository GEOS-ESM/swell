
from swell.utilities.sat_db_utils import get_active_channels 

use_flags = [-1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1]

cycle_time = '20211212T000000Z'
active_channel_yaml = 'active_channels_test_files/amsua_n19.yaml' 
observation = 'active_channels_test_files/amsua_n19_active_channels.yaml'

generated_use_flags = get_active_channels(observation, active_channel_yaml, cycle_time)

assert(use_flags == generated_use_flags)
