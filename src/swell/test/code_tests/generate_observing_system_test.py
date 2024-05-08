import os
from swell.utilities.observing_system_records import ObservingSystemRecords

observations = ['airs_aqua']
observing_system_records_path = './yaml_output/'

# Clone Geos_mksi
os.system('git clone https://github.com/GEOS-ESM/GEOS_mksi.git')
path_to_gsi_records = os.path.join('GEOS_mksi/', 'sidb')
sat_records = ObservingSystemRecords()
sat_records.parse_records(path_to_gsi_records)
sat_records.save_yamls(observing_system_records_path, observations)
