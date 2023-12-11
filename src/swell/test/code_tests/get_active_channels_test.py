from swell.utilities.get_active_channels import get_active_channels

use_flags = [-1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1]

cycle_time = '20211212T000000Z'
path_to_observing_sys_yamls = 'active_channels_test_files/'
path_to_configs = 'active_channels_test_files/'
observation = 'amsua_n19'

generated_use_flags = get_active_channels(path_to_observing_sys_yamls,
                                          path_to_configs, observation, cycle_time)
assert (use_flags == generated_use_flags)
