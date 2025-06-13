# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess

from swell.utilities.datetime_util import datetime_formats
#from swell.utilities.copy_to_dst_dir import copy_to_dst_dir
from swell.tasks.base.task_base import taskBase

import datetime

import glob
import yaml
# --------------------------------------------------------------------------------------------------

# Dictionary linking each obs type to the appropriate yaml template
#path_to_ioda_conv_yaml_tmpl_dir = os.path.join(self.experiment_path(), 'configuration/iodaconv')

#bufr_to_ioda_yaml_obs_type_dict = {
bufr2ioda_obs_type_dict = {
    '1bmhs': 'bufr_ncep_1bmhs.yaml',
    'amsua': 'bufr_ncep_1bamua_ta.yaml',
    '1bamua': 'bufr_ncep_1bamua_ta.yaml',
    'atms': 'bufr_ncep_atms.yaml',
    'mtiasi': 'bufr_ncep_mtiasi.yaml',
    'satwind': 'bufr_ncep_satwind_avhrr.yaml',
    'aircft': 'bufr_ncep_prepbufr_aircft.yaml',
    'sevcsr': 'bufr_ncep_sevcsr.yaml'
}


# python split filename by delimiter period and then search for string in the resulting list
def find_obstype_match(filename):
    """
    Splits the filename by '.' and returns the first match found in obs_type_search_dict.
    Prints the match if found, otherwise prints 'No match found.'

    Dictionary:
    bufr2ioda_obs_type_dict = {
        '1bmhs': 'bufr_ncep_1bmhs.yaml',
        'amsua': 'bufr_ncep_1bamua_ta.yaml',
        '1bamua': 'bufr_ncep_1bamua_ta.yaml',
        'atms': 'bufr_ncep_atms.yaml',
        'mtiasi': 'bufr_ncep_mtiasi.yaml',
        'satwind': 'bufr_ncep_satwind_avhrr.yaml',
        'aircft': 'bufr_ncep_prepbufr_aircft.yaml',
        'sevcsr': 'bufr_ncep_sevcsr.yaml'
    }
    
    """
    # 
    obs_type_search_dict = bufr2ioda_obs_type_dict
    parts = filename.split('.')
    for part in parts:
        if part in obs_type_search_dict:
            print(f"Match found: {part}")
            return part
    print("No match found.")
    return None

# 
def generate_iodaconv_yaml(bufr_file_source_path, ioda_file_target_path, path_to_ioda_conv_yaml_tmpl_dir,
                            swell_exp_path, cycle_dir, ioda_dir,
                            yaml_file_source=None, yaml_file_target=None):
#def generate_iodaconv_yaml(obsdatain, obsdataout, obs_type, yaml_file_source=None, yaml_file_target=None):
    '''
    obsdatain: input file path to be inserted into the conversion yaml
    obsdataout: output file path to be inserted into the conversion yaml
    obs_type: observation type ~ 'amsua,atms,1bmhs...'
    yaml_file_source: yaml file to use to replicate the structure for the specific obs_type
    yaml_file_target:
    '''
    #path_to_ioda_conv_yaml_tmpl_dir = os.path.join(self.experiment_path(), 'configuration/iodaconv') # where the yaml 'templates' are stored

    # Keep?
    # ------            
    #yaml_file_source =  # in case user wants to user an alternative (custom) yaml file
    #yaml_file_target =  # in case user wants to user an alternative (custom) yaml file
    #ioda_file_target_path =  
    obsdatain = bufr_file_source_path # Value to insert into the yaml file as the value for 'obsdatain'. Source file ~ bufr file to be converted 
    obsdataout = ioda_file_target_path # Value to insert into the yaml file as the value for 'obsdataout'. Target file ~ conversion output file name

    # find the obs type from file name
    bufr_file_obs_type = find_obstype_match(obsdatain)

    # Testing
    # -------
    #print(f'''obsdatain: {obsdatain} -----------------------------------''')
    #print(f'''obsdataout: {obsdataout} -----------------------------------''')
    #print(f'''path_to_ioda_conv_yaml_tmpl_dir: {path_to_ioda_conv_yaml_tmpl_dir} -----------------------------------''')
    #print(f'''bufr_file_obs_type: {bufr_file_obs_type} -----------------------------------''')
    
    # Determine which yaml template to use based on the found 'obs_type' and set the file path
    # -----------------------------------------------------------------------------------------
    if yaml_file_source is None:
        # Path to use as the yaml template
        yaml_file_source = os.path.join(path_to_ioda_conv_yaml_tmpl_dir,
                                            f'{bufr2ioda_obs_type_dict[bufr_file_obs_type]}')

    # Determine the target path of the generated yaml file 
    # ----------------------------------------------------
    if yaml_file_target is None:
        yaml_file_target = os.path.join(cycle_dir, 'generated_iodaconv_input.yaml')  # Overwrite original if no output file is specified

    print(f'YAML template used:  {yaml_file_source}.------------------------------ ')
    print(f'YAML file saved as {yaml_file_target}. ------------------------------ ')

    # Copy the yaml file 
    # copy_to_dst_dir(logger, yaml_file_source, yaml_file_target)
    #os.system(f"cp {yaml_file_source} {yaml_file_target}")
    subprocess.run(['cp', yaml_file_source, yaml_file_target])

    # Generate the yaml file that will be used in the conversion step ~ bufr2ioda.x [yaml file]
    # -----------------------------------------------------------------------------------------
    try:
            # Load the YAML template file 
            with open(yaml_file_source, 'r') as file:
                yaml_content = yaml.safe_load(file)
                file.close()

            print(yaml.dump(yaml_content, default_flow_style=False, sort_keys=False))  

            # Apply the replacements for input and output file paths
            yaml_content['observations'][0]['obs space']['obsdatain'] = obsdatain # Source file ~ bufr file to be converted (must be a bufr or prepbufr file) 
            yaml_content['observations'][0]['ioda']['obsdataout'] = obsdataout # Target file ~ conversion output file name (should end in .nc4)

            
            with open(yaml_file_target, 'w') as file:
                yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)
                print('Updated YAML file content:')
                print(yaml.dump(yaml_content, default_flow_style=False, sort_keys=False))  
                     
            # Testing
            # -------

            print(f'----------------------------------- 136            --------------------------------------------------------')
            print(f'''obsdatain: {yaml_content['observations'][0]['obs space']['obsdatain']} -----------------------------------''')
            print(f'''obsdataout: {yaml_content['observations'][0]['ioda']['obsdataout']} -----------------------------------''')
            print(f'YAML template used:  {yaml_file_source}.')
            print(f'YAML file saved as {yaml_file_target}.')
            
            # Assert that the files were all found
            #self.logger.assert_abort(yaml_file_source is not None, f'In BufrToIoda no YAML template file found in {path_to_ioda_conv_yaml_tmpl_dir}.')
            #self.logger.assert_abort(satbiaspc_file_index is not None,
            #                         f'In BufrToIoda no satbiaspc file found in {gsi_bc_dir}.')
            #if 'aircraft' in observations:
            #    self.logger.assert_abort(acftbias_file_index is not None,
            #                             f'In BufrToIoda no acftbias file found in {gsi_bc_dir}.')

    except FileNotFoundError:
        print(f'Error: File "{yaml_file_source}" not found.')
    except yaml.YAMLError as e:
        print(f'Error processing YAML file: {e}')
    return yaml_file_target # returns the path of the yaml file the function generated

# --------------------------------------------------------------------------------------------------
class BufrToIoda(taskBase):

    def execute(self) -> None:
        # 1. Task Configuration and directory setup & init
        # ------------------------------------------------------------------------------------------
        # experiment directory in SwellExperiments
        swell_exp_path = self.experiment_path()
        cycle_dir = self.cycle_dir()

        # Get cycle dir and create if needed
        # ----------------------------------
        # Set Bufr File Directory (Input)
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr')

        # Set Ioda File Directory (Output) and create if needed
        ioda_dir = os.path.join(self.cycle_dir(), 'ioda')
        os.makedirs(ioda_dir, 0o755, exist_ok=True)
        # GOOD ~ print(f'ioda_dir: {ioda_dir}')

        # Set the Bufr2Ioda Yaml Template Directory 
        path_to_ioda_conv_yaml_tmpl_dir = os.path.join(self.experiment_path(), 'configuration/jedi/iodaconv')

        # 2. Find Bufr files to converter
        # ------------------------------------------------------------------------------------------
        # Get list of all files in cycle dir  with .bufr_d suffix or *bufr* 
        # --------------------------------
        bufr_path_files_pattern = os.path.join(bufr_dir, '*bufr*')
        bufr_path_files = glob.glob(bufr_path_files_pattern)
        
        # Assert that some files were found
        self.logger.assert_abort(len(bufr_path_files) != 0 is not None, f'No bufr ' +
                                    f'files found in the source directory ' +
                                    f'\'{bufr_path_files_pattern}\'')
        

        # 3. Convert Bufr Files (one by one)
        # ------------------------------------------------------------------------------------------
        for bufr_path_file in bufr_path_files:
            #print(f'----------------------------------- 193 bufr_path_file ---------------------------------------------------------')
            #print(f'bufr_path_file: {bufr_path_file}')  # GOOD ~ 
            # bufr_path_file: /discover/nobackup/sicohen/SwellExperiments/swell-convert_bufr/run/20211212T000000Z/geos_atmosphere/bufr/gdas1.211212.t00z.1bamua.tm00.bufr_d
            #print(f'logger: {self.logger}')  # GOOD ~ 


            #print(f'----------------------------------- 200 find_obstype_match ---------------------------------------------------------')
            # find the obs type within the filename
            obs_type = find_obstype_match(bufr_path_file)
            #print(f'obs_type: {obs_type}') # GOOD ~ 

            # Source file ~ bufr file to be converted 
            bufr_file_source_path = os.path.basename(bufr_path_file)
            #print(f'bufr_file_source_path: {bufr_file_source_path}')
            #   bufr_file_source_path: gdas1.211212.t00z.1bamua.tm00.bufr_d
            #print(f'----------------------------------- 206 # Source file ~ bufr file to be converted  ---------------------------------------------------------')

            # Target file ~ conversion output file name (should end in .nc4). Use the same name but replace the suffix.
            parts = bufr_file_source_path.rsplit('.', 2)
            print(f'ioda file name parts: {parts}')
            ioda_file_target_name = parts[0] + '.{splits/satId}.tm00.nc4'
            print(f'ioda file name parts: {parts}')
            ioda_file_target_path = os.path.join(ioda_dir, ioda_file_target_name)
            #print(f'----------------------------------- 212 # Target file ~ conversion output file name--------------------------------------------------------')
            #print(f'parts: {parts}')
            #print(f'ioda_file_target_name: {ioda_file_target_name}')
            #print(f'ioda_file_target_path: {ioda_file_target_path}')

            print(f'----------------------------------- 216 generate_iodaconv_yaml ---------------------------------------------------------')
            # Generate the yaml file that will be used in the conversion step ~ bufr2ioda.x [yaml file]
            print(f'ioda_file_target_path: {bufr_path_file}')
            print(f'ioda_file_target_path: {ioda_file_target_path}')
            print(f'ioda_file_target_path: {path_to_ioda_conv_yaml_tmpl_dir}')
            print(f'ioda_file_target_path: {swell_exp_path}')
            print(f'ioda_file_target_path: {cycle_dir}')
            print(f'ioda_file_target_path: {ioda_dir}')
            bufr2ioda_conv_yaml = generate_iodaconv_yaml(bufr_path_file, ioda_file_target_path, path_to_ioda_conv_yaml_tmpl_dir,swell_exp_path,cycle_dir, ioda_dir)

            print(f'----------------------------------- 223 bufr2ioda_conv_yaml--------------------------------------------------------')

            #current_directory = os.getcwd()
            #print(f' CURRENT DIRECTORY: {current_directory} ---------------------------------------------' )
            #print(f'ioda_file_target_path: {bufr2ioda_conv_yaml}')

            subprocess.run(['bufr2ioda.x', bufr2ioda_conv_yaml])



# --------------------------------------------------------------------------------------------------
# For later
"""

1.--------------------------------------------------------------------------------------------------

        # Directory containing the bufr files
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr/.')
        ioda_dir = os.path.join(self.cycle_dir(), 'ioda/.')
        #ioda_conv_yaml_dir = os.path.join(self.cycle_dir(), 'ioda_conv_yaml/.')
        #path_to_ioda_conv_yaml_tmpl = os.path.join(self.cycle_dir(), 'ioda_conv_yaml_tmpl/.') # yamls used for bufr2ioda.x
        #bufr2ioda_yaml_dir = os.path.join(self.cycle_dir(), 'ioda_conv_yaml/.') # yamls used for bufr2ioda.x

.--------------------------------------------------------------------------------------------------

            # Determine the target path of the generated yaml file 
            if yaml_file_target is None:
                yaml_file_target = f'{bufr2ioda_obs_type_dict[bufr_file_obs_type]}'  # Overwrite original if no output file is specified
            # Determine the output file path
            if yaml_file_target is None:
                yaml_file_target = os.path.join(bufr2ioda_obs_type_dict,'generated_iodaconv_input.yaml')  # Overwrite original if no output file is specified

.--------------------------------------------------------------------------------------------------
        ...

        # Get list of all files in cycle dir  with .bufr_d suffix or *bufr* 
        # --------------------------------
        bufr_path_files_pattern = os.path.join(bufr_path, '*bufr*')
        bufr_path_files = glob.glob(bufr_path_files_pattern)
        
        # more complete version (for later)
        #bufr_filename_template = 'gdas1.' + cycle_time_dto.strftime('%y%d%m.t%Hz.') + '1bamua' + '.tm00.bufr_d'
        #bufr_path = cycle_time_dto.strftime(bufr_path)
        #bufr_filename_template = 'gdas1.' + cycle_time_dto.strftime('%y%d%m.t%Hz.') + obs_type + '.tm00.bufr_d'
        #bufr_path_files_pattern = os.path.join(bufr_path, bufr_filename_template) 

"""
