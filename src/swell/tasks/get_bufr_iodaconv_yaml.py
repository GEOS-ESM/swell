#swell-ioda-workflow/tasks/get_bufr_iodaconv_yaml.py
import yaml
import os

# Path to yaml templates for bufr2ioda.x conversion
bufr_to_ioda_yaml_dir = 'jedi_bundle/build/iodaconv/test/testinput/'

# Dictionary linking each obs type to the appropriate yaml template
bufr_to_ioda_yaml_dict = {
    '1bmhs': 'bufr_ncep_1bmhs.yaml',
    'amsua': 'bufr_ncep_1bamua_ta.yaml',
    'atms': 'bufr_ncep_atms.yaml',
    'mtiasi': 'bufr_ncep_mtiasi.yaml',
    'satwind': 'bufr_ncep_satwind_avhrr.yaml',
    'aircft': 'bufr_ncep_prepbufr_aircft.yaml',
    'sevcsr': 'bufr_ncep_sevcsr.yaml'
}


def create_iodaconv_yaml(obsdatain,obsdataout,obs_type,yaml_template_path=None,output_yaml=None):
    '''
    obsdatain: input file path to be inserted into the conversion yaml
    obsdataout: output file path to be inserted into the conversion yaml
    obs_type: observation type ~ 'amsua,atms,1bmhs...'
    yaml_template_path:path ; yaml file to use to replicate the structure for the specific obs_type
    output_yaml:str

    # Test/Example
    create_iodaconv_yaml(
        obsdatain = './AMSUA/Y2021/M11/gdas1.211101.t00z.1bamua.tm00.bufr_d',
        obsdataout = './ioda/gdas1.211101.t00z.1bamua.tm00.nc4' ,
        obs_type = 'amsua'
        yaml_template_path='/Users/sicohen/Documents/GitHub/swell/bufr_amsua.yaml',
        output_yaml=None)
    '''
    
    # Determine the yaml template file path
    if yaml_template_path is None:
        # Path to use as the yaml template
        yaml_template_path = os.path.join(bufr_to_ioda_yaml_dir,
                                          f'{bufr_to_ioda_yaml_dict[obs_type]}')
    
    try:
            # Load the YAML template file 
            with open(yaml_template_path, 'r') as file:
                yaml_content = yaml.safe_load(file)
    
            # Apply the replacements for input and output file paths
            yaml_content['observations'][0]['obs space']['obsdatain'] = obsdatain # input bufr file path.
            yaml_content['observations'][0]['ioda']['obsdataout'] = obsdataout # output path and/or filename for the converted ioda file.
    
            # Determine the output file path
            if output_yaml is None:
                output_yaml = f'{bufr_to_ioda_yaml_dict[obs_type]}'  # Overwrite original if no output file is specified
        
            # Write the updated data to the specified output file
            with open(output_yaml, 'w') as file:
                yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)
                print('Updated YAML file content:')
                print(yaml.dump(yaml_content, default_flow_style=False, sort_keys=False))        
            
            print(f'YAML file saved as '"output_yaml}".')
    
    except FileNotFoundError:
        print(f'Error: File "{file_path}" not found.')
    except yaml.YAMLError as e:
        print(f'Error processing YAML file: {e}')


