from swell.utilities.get_channels import get_channels
from datetime import datetime as dt

use_flags = [-1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1]

cycle_time = '20211212T000000Z'
dt_cycle_time = dt.strptime(cycle_time, '%Y%m%dT%H%M%SZ')
path_to_observing_sys_yamls = 'active_channels_test_files/'
observation = 'amsua_n19'

avail, generated_use_flags = get_channels(path_to_observing_sys_yamls, observation, dt_cycle_time)

assert (use_flags == generated_use_flags)
