import os
from swell.utilities.observing_system_records import ObservingSystemRecords

observations = ['airs_aqua']
observing_system_records_path = './yaml_output/'

# Clone GeosAna
os.system('git clone https://github.com/GEOS-ESM/GEOSana_GridComp.git')
path_to_gsi_records = os.path.join('GEOSana_GridComp/', 'GEOSaana_GridComp',
                                   'GSI_GridComp', 'mksi', 'sidb')
sat_records = ObservingSystemRecords()
sat_records.parse_records(path_to_gsi_records)
sat_records.save_yamls(observing_system_records_path, observations)
