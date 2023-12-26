from swell.utilities.datetime import Datetime
from swell.utilities.run_jedi_executables import check_observation
from swell.utilities.render_jedi_interface_files import JediConfigRendering
from swell.utilities.logger import Logger

'''
    Testing three observation checks:
        1. The observation file exists
        2. The observation file is not empty
        3. If applicable, the active channels are nonzero for cycle time
'''

# Set fields
path_to_observing_sys_yamls = 'missing_obs_test/experiment/run/20211212T000000Z/geos_atmosphere/observing_system_records'
logger = Logger('Missing Obs Test')
cycle_time = 'missing_obs_test'
experiment_root = 'missing_obs_test'
experiment_id = 'experiment'
cycle_dir = 'missing_obs_test/experiment/run/20211212T000000Z/geos_atmosphere'
model = 'geos_atmosphere'
datetime_input = '2021-12-12T00:00:00Z'
datetime = Datetime(datetime_input)

# Instantiate jedi_rendering
jedi_rendering = JediConfigRendering(logger, experiment_root,
                                     experiment_id, cycle_dir,
                                     datetime, model)
jedi_rendering.add_key('window_begin', '20211211T210000Z')
jedi_rendering.add_key('background_time', '20211211T150000Z')
jedi_rendering.set_obs_records_path(path_to_observing_sys_yamls)

# Test 1: Observation file does not exist
# ---------------------------------------
observation = 'aircraft'
obs_dict = jedi_rendering.render_interface_observations(observation)
use_obs = check_observation(path_to_observing_sys_yamls, observation, 
                            obs_dict, cycle_time)
assert(use_obs == False)

# Test 2: Observation file exists but is empty
# --------------------------------------------
#observation = 'satwind'
#obs_dict = jedi_rendering.render_interface_observations(observation)
#use_obs = check_observation(path_to_observing_sys_yamls, observation, 
#                            obs_dict, cycle_time)
#assert(use_obs == False)

# Test 3: Observation file exists but is not empty
# ------------------------------------------------
observation = 'scatwind'
obs_dict = jedi_rendering.render_interface_observations(observation)
use_obs = check_observation(path_to_observing_sys_yamls, observation,
                            obs_dict, cycle_time)
assert(use_obs == True)

# Test 4: Observation file exists, is not empty, but no active channels
# ---------------------------------------------------------------------
observation = 'amsua_n19'
obs_dict = jedi_rendering.render_interface_observations(observation)
use_obs = check_observation(path_to_observing_sys_yamls, observation,
                            obs_dict, cycle_time)
assert(use_obs == False)

# Test 5: Observation file exists, is not empty, has active channels
# ------------------------------------------------------------------
observation = 'amsua_metop-b'
obs_dict = jedi_rendering.render_interface_observations(observation)
use_obs = check_observation(path_to_observing_sys_yamls, observation,
                            obs_dict, cycle_time)
assert(use_obs == True)

