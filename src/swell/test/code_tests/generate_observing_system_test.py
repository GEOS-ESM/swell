import os
from swell.utilities.observing_system_records import ObservingSystemRecords

observations = ['amsua_n19']
observing_system_records_path = './yaml_output/'
path_to_geosana_gridcomp = '/discover/nobackup/asewnath/github/GEOSana_GridComp/'
path_to_gsi_records = os.path.join(path_to_geosana_gridcomp, 'GEOSaana_GridComp',
                                   'GSI_GridComp', 'mksi', 'sidb')
sat_records = ObservingSystemRecords()
sat_records.parse_records(path_to_gsi_records)
sat_records.save_yamls(observing_system_records_path, observations)
