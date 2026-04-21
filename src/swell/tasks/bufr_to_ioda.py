# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import subprocess
from ruamel.yaml import YAML, YAMLError

from swell.tasks.base.task_base import taskBase
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------

# Dictionary linking each obs type to the appropriate yaml template
bufr2ioda_obs_type_dict = {
    'ncep_1bamua_bufr': 'bufr_mapping_1bamua_ta.yaml',
    '1bamua': 'bufr_mapping_1bamua_ta.yaml',
    'ncep_mhs_bufr': 'bufr_mapping_mhs.yaml',
    '1bmhs': 'bufr_mapping_mhs.yaml',
    'mhs': 'bufr_mapping_mhs.yaml',
    'ncep_mtiasi_bufr': 'bufr_mapping_mtiasi.yaml',
    'mtiasi': 'bufr_mapping_mtiasi.yaml',
}

    # '1bmhs': 'bufr_mapping_1bmhs.yaml',
    # 'ncep_1bmhs_bufr': 'bufr_mapping_1bmhs.yaml',
    # 'amsua': 'bufr_mapping_1bamua_ta.yaml',
    # '1bamua': 'bufr_mapping_1bamua_ta.yaml',
    # 'ncep_1bamua_bufr': 'bufr_mapping_1bamua_ta.yaml',
    # 'atms': 'bufr_mapping_atms.yaml',
    # # 'mtiasi': 'bufr_mapping_mtiasi.yaml',
    # 'ncep_mtiasi_bufr': 'bufr_mapping_mtiasi.yaml',
    # 'satwind': 'bufr_mapping_satwind_avhrr.yaml',
    # 'aircft': 'bufr_mapping_prepbufr_aircft.yaml',
    # 'sevcsr': 'bufr_mapping_sevcsr.yaml'
# --------------------------------------------------------------------------------------------------


class BufrToIoda(taskBase):

    # python split filename by delimiter period and then search for string in the resulting list
    def find_obstype_match(self, filename):
        """
        Splits the filename by '.' and returns the first match found in obs_type_search_dict.
        Prints the match if found, otherwise prints 'No match found.'

        Dictionary:
        bufr2ioda_obs_type_dict = {
            '1bmhs': 'bufr_mapping_1bmhs.yaml',
            'amsua': 'bufr_mapping_1bamua_ta.yaml',
            '1bamua': 'bufr_mapping_1bamua_ta.yaml',
            'atms': 'bufr_mapping_atms.yaml',
            'mtiasi': 'bufr_mapping_mtiasi.yaml',
            'satwind': 'bufr_mapping_satwind_avhrr.yaml',
            'aircft': 'bufr_mapping_prepbufr_aircft.yaml',
            'sevcsr': 'bufr_mapping_sevcsr.yaml'
        }

        """

        print(f"filename: {filename}")
        parts = filename.split('.')
        self.logger.info(f"parts: {parts}")
        print(f"parts: {parts}")

        for part in parts:
            if part in bufr2ioda_obs_type_dict:
                self.logger.info(f"Match found: {part}")
                return part
        self.logger.info("No match found.")
        return None

    # --------------------------------------------------------------------------------------------------

    def get_bufr_mapping_yaml(self,
                               bufr_file_source_path,
                               ioda_file_target_path,
                               path_to_ioda_conv_yaml_tmpl_dir,
                               yaml_file_source=None,
                               yaml_file_target=None):
        '''
        obsdatain: input file path to be inserted into the conversion yaml
        obsdataout: output file path to be inserted into the conversion yaml
        obs_type: observation type ~ 'amsua,atms,1bmhs...'
        yaml_file_source: yaml file to use to replicate the structure for the specific obs_type
        yaml_file_target:
        '''

        # Copy the yaml file
        try:
            # Value to insert into the yaml file as the value for 'obsdatain'.
            # Source file ~ bufr file to be converted
            obsdatain = bufr_file_source_path

            # Value to insert into the yaml file as the value for 'obsdataout'.
            # Target file ~ conversion output file name
            obsdataout = ioda_file_target_path

            # find the obs type from file name
            bufr_file_obs_type = self.find_obstype_match(obsdatain)
        except FileNotFoundError:
            self.logger.info(f'bufr_file_source_path:  {bufr_file_source_path} ------------------------------ ')
            self.logger.info(f'obsdatain:  {obsdatain} ------------------------------ ')
            self.logger.info(f'obsdataout:  {obsdataout} ------------------------------ ')
            self.logger.info(f'ioda_file_target_path:  {ioda_file_target_path} ------------------------------ ')
            self.logger.info(f'bufr_file_obs_type:  {bufr_file_obs_type} ------------------------------ ')
        except yaml.YAMLError as e:
            self.logger.info(f'Error processing find_obstype_match: {e}')

        # Determine the target path of the generated yaml file
        # ----------------------------------------------------
        if yaml_file_target is None:
            # Overwrite original if no output file is specified
            yaml_file_target = os.path.join(self.cycle_dir(), f'bufr_mapping_{bufr_file_obs_type}.yaml')

            self.logger.info(f'YAML template used:  {self.cycle_dir()}.------------------------------ ')
            self.logger.info(f'yaml_file_source:  {yaml_file_source}.------------------------------ ')
            self.logger.info(f'yaml_file_target {yaml_file_target}. ------------------------------ ')

        # -----------------------------------------------------------------------------------------


        # Copy the yaml file
        try:
            if yaml_file_source is None:
                # Path to use as the yaml template
                yaml_file_source = os.path.join(path_to_ioda_conv_yaml_tmpl_dir,
                                                f'{bufr2ioda_obs_type_dict[bufr_file_obs_type]}')
        except FileNotFoundError:
            self.logger.info(f'Error: File "{yaml_file_source}" not found.')
            self.logger.info(f'Error:  "{bufr2ioda_obs_type_dict}" not found.')
            self.logger.info(f'Error:  "{path_to_ioda_conv_yaml_tmpl_dir}" not found.')
            self.logger.info(f'Error:  "{bufr_file_obs_type}" not found.')
        except yaml.YAMLError as e:
            self.logger.info(f'Error processing YAML file: {e}')

        # Determine the target path of the generated yaml file
        # ----------------------------------------------------
        if yaml_file_target is None:
            # Overwrite original if no output file is specified
            yaml_file_target = os.path.join(self.cycle_dir(), f'bufr_mapping_{bufr_file_obs_type}.yaml')

        self.logger.info(f'YAML template used:  {yaml_file_source}.------------------------------ ')
        self.logger.info(f'YAML file saved as {yaml_file_target}. ------------------------------ ')

        # Copy the yaml file
        try:
            subprocess.run(['cp', yaml_file_source, yaml_file_target])
            self.logger.info(f'Copied YAML file: from {yaml_file_source} to {yaml_file_target}')

            # Dardag's changes. Old method of editing the yaml contents. For Bufr-query, yaml is copied because it does not need edits. Can delete?
            # -------------------------------------------------------------------------------------------------------------------------------------
            # # Load the YAML template file
            # with open(yaml_file_source, 'r') as file:
            #     yaml_str = file.read()

            # # Construct dictionary to fill yaml file
            # template_dictionary = {'obsdatain': obsdatain,
            #                        'obsdataout': obsdataout}

            # # Apply the replacements for input and output file paths
            # yaml_str = template_string_jinja2(self.logger,
            #                                   templated_string=yaml_str,
            #                                   dictionary_of_templates=template_dictionary)

            # # Load and write the dictionary using rt mode (preserves formatting)
            # yaml_config = YAML()
            # yaml_content = yaml_config.load(yaml_str)

            # # Write the updated content to the target yaml file
            # with open(yaml_file_target, 'w') as file:
            #     yaml_config.dump(yaml_content, file)
            #     self.logger.info(f'Updated YAML file content: {yaml_file_target}')
            # -------------------------------------------------------------------------------------------------------------------------------------
            
        except FileNotFoundError:
            self.logger.info(f'Error: File "{yaml_file_source}" not found.')
        except YAMLError as e:
            self.logger.info(f'Error processing YAML file: {e}')
        # returns the path of the yaml file the function generated
        return yaml_file_target

    # --------------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Set Bufr File Directory (Input)
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr')

        # Set Ioda File Directory (Output) and create if needed
        ioda_dir = os.path.join(self.cycle_dir(), 'ioda')
        os.makedirs(ioda_dir, 0o755, exist_ok=True)

        # Set the Bufr2Ioda Yaml Template Directory
        path_to_ioda_conv_yaml_tmpl_dir = os.path.join(self.experiment_path(),
                                                       'configuration/jedi/bufr2ioda/bufr2netcdf_x/')
        self.logger.info(f'Path to yaml files found: {path_to_ioda_conv_yaml_tmpl_dir}')

        # Get list of all files in cycle dir with .bufr_d suffix or *bufr*
        bufr_path_files_pattern = os.path.join(bufr_dir, '*bufr*')
        bufr_path_files = glob.glob(bufr_path_files_pattern)

        self.logger.info(f'Bufr files found: {bufr_path_files}')

        # Assert that some files were found
        self.logger.assert_abort(len(bufr_path_files) != 0, f'No bufr ' +
                                 f'files found in the source directory ' +
                                 f'\'{bufr_path_files_pattern}\'')

        # 3. Convert Bufr Files (one by one)
        # ------------------------------------------------------------------------------------------
        for bufr_path_file in bufr_path_files:

            # Source file ~ bufr file to be converted
            bufr_file_source_path = os.path.basename(bufr_path_file)

            self.logger.info(f'bufr_file_source_path: {bufr_file_source_path}')
            # Target file ~ conversion output file name (should end in .nc4).
            # Use the same name but replace the suffix.
            parts = bufr_file_source_path.rsplit('.', 2)
            ioda_file_target_name = parts[0] + '.tm00.nc4'
            ioda_file_target_path = os.path.join(ioda_dir, ioda_file_target_name)
            self.logger.info(f'ioda_file_target_path: {ioda_file_target_path}')

            bufr2ioda_conv_yaml = self.get_bufr_mapping_yaml(bufr_path_file, ioda_file_target_path,
                                                              path_to_ioda_conv_yaml_tmpl_dir)
            self.logger.info(f'bufr_path_file: {bufr_path_file}')
            self.logger.info(f'bufr2ioda_conv_yaml: {bufr2ioda_conv_yaml}')
            self.logger.info(f'ioda_file_target_path: {ioda_file_target_path}')

            # Jedi executable name (IODA Converter Name)
            # --------------------
            jedi_executable = 'bufr2netcdf.x'
            jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                                'build', 'bin', jedi_executable)
            
            # CLI Command
            # ------------
            # bufr2netcdf.x [bufr file] [bufr_mapping.yaml]  [output .nc file]
            # bufr2netcdf.x bufr_path_file bufr2ioda_conv_yaml ioda_file_target_path
            # cli_command = [jedi_executable_path, bufr_path_file, bufr2ioda_conv_yaml, ioda_file_target_path]

            try:
                self.logger.info('Running '+jedi_executable_path+' with '+bufr2ioda_conv_yaml+'.')
                self.logger.info(f'Execution cli line: {jedi_executable_path}, {bufr_path_file}, {bufr2ioda_conv_yaml}, {ioda_file_target_path}')
                subprocess.run([jedi_executable_path, bufr_path_file, bufr2ioda_conv_yaml, ioda_file_target_path])
            except FileNotFoundError:
                self.logger.info(f'Error: File "{bufr2ioda_conv_yaml}" not found.')
            except YAMLError as e:
                self.logger.info(f'Error processing YAML file: {e}')
            else:
                self.logger.info('Conversion to ioda complete, now exiting.') 
                self.logger.info(f'Execution cli line: {jedi_executable_path}, {bufr_path_file}, {bufr2ioda_conv_yaml}, {ioda_file_target_path}') 

# --------------------------------------------------------------------------------------------------
