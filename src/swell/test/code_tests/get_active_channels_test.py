from swell.utilities.get_channels import get_channels
from datetime import datetime as dt

# Use flags
amsua_n19_use_flags = [-1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1]
avhrr3_n18_use_flags = [-1, 1, 1]
gmi_gpm_use_flags = [-1, -1, -1, -1, 1, 1, 1, -1, -1, 1, -1, 1, 1]
mhs_metop_c_use_flags = [1, 1, 1, 1, 1]

use_flags = [amsua_n19_use_flags, avhrr3_n18_use_flags, 
             gmi_gpm_use_flags, mhs_metop_c_use_flags]

# Observation list
observations = ['amsua_n19', 'avhrr3_n18', 'gmi_gpm', 'mhs_metop-c']

cycle_time = '20211212T000000Z'
dt_cycle_time = dt.strptime(cycle_time, '%Y%m%dT%H%M%SZ')
path_to_observing_sys_yamls = 'active_channels_test_files/'

for idx, _ in enumerate(observations):
    avail, generated_use_flags = get_channels(path_to_observing_sys_yamls, observations[idx], dt_cycle_time)
    assert (use_flags[idx] == generated_use_flags)
