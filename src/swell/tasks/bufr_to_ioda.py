# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import subprocess
import yaml

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------

# Dictionary linking each obs type to the appropriate yaml template
bufr2ioda_obs_type_dict = {
    '1bmhs': 'bufr_ncep_1bmhs.yaml',
    'amsua': 'bufr_ncep_1bamua_ta.yaml',
    '1bamua': 'bufr_ncep_1bamua_ta.yaml',
    'ncep_1bamua_bufr': 'bufr_ncep_1bamua_ta.yaml',
    'atms': 'bufr_ncep_atms.yaml',
    'mtiasi': 'bufr_ncep_mtiasi.yaml',
    'ncep_mtiasi_bufr': 'bufr_ncep_mtiasi.yaml',
    'satwind': 'bufr_ncep_satwind_avhrr.yaml',
    'aircft': 'bufr_ncep_prepbufr_aircft.yaml',
    'sevcsr': 'bufr_ncep_sevcsr.yaml'
}

# --------------------------------------------------------------------------------------------------

task_name = 'BufrToIoda'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.is_cycling = True
        self.is_model = True

# --------------------------------------------------------------------------------------------------


class BufrToIoda(taskBase):

    # python split filename by delimiter period and then search for string in the resulting list
    def find_obstype_match(self, filename):
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

        parts = filename.split('.')
        for part in parts:
            if part in bufr2ioda_obs_type_dict:
                self.logger.info(f"Match found: {part}")
                return part
        self.logger.info("No match found.")
        return None

    # --------------------------------------------------------------------------------------------------

    def generate_iodaconv_yaml(self,
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
        # Value to insert into the yaml file as the value for 'obsdatain'.
        # Source file ~ bufr file to be converted
        obsdatain = bufr_file_source_path

        # Value to insert into the yaml file as the value for 'obsdataout'.
        # Target file ~ conversion output file name
        obsdataout = ioda_file_target_path

        # find the obs type from file name
        bufr_file_obs_type = self.find_obstype_match(obsdatain)

        # -----------------------------------------------------------------------------------------

        if yaml_file_source is None:
            # Path to use as the yaml template
            yaml_file_source = os.path.join(path_to_ioda_conv_yaml_tmpl_dir,
                                            f'{bufr2ioda_obs_type_dict[bufr_file_obs_type]}')

        # Determine the target path of the generated yaml file
        # ----------------------------------------------------
        if yaml_file_target is None:
            # Overwrite original if no output file is specified
            yaml_file_target = os.path.join(self.cycle_dir(), 'generated_iodaconv_input.yaml')

        self.logger.info(f'YAML template used:  {yaml_file_source}.------------------------------ ')
        self.logger.info(f'YAML file saved as {yaml_file_target}. ------------------------------ ')

        # Copy the yaml file
        subprocess.run(['cp', yaml_file_source, yaml_file_target])

        # Generate the yaml file that will be used in the conversion step ~ bufr2ioda.x [yaml file]
        # -----------------------------------------------------------------------------------------
        try:
            # Load the YAML template file
            with open(yaml_file_source, 'r') as file:
                yaml_str = file.read()

            # Construct dictionary to fill yaml file
            template_dictionary = {'obsdatain': obsdatain,
                                   'obsdataout': obsdataout}

            # Apply the replacements for input and output file paths
            yaml_str = template_string_jinja2(self.logger,
                                              templated_string=yaml_str,
                                              dictionary_of_templates=template_dictionary)

            # Load the dictionary
            yaml_content = yaml.safe_load(yaml_str)

            with open(yaml_file_target, 'w') as file:
                yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)
                self.logger.info(f'Updated YAML file content: {yaml_file_target}')

        except FileNotFoundError:
            self.logger.info(f'Error: File "{yaml_file_source}" not found.')
        except yaml.YAMLError as e:
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
                                                       'configuration/jedi/bufr2ioda')

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

            # Target file ~ conversion output file name (should end in .nc4).
            # Use the same name but replace the suffix.
            parts = bufr_file_source_path.rsplit('.', 2)
            ioda_file_target_name = parts[0] + '.{splits/satId}.tm00.nc4'
            ioda_file_target_path = os.path.join(ioda_dir, ioda_file_target_name)

            bufr2ioda_conv_yaml = self.generate_iodaconv_yaml(bufr_path_file, ioda_file_target_path,
                                                              path_to_ioda_conv_yaml_tmpl_dir)

            # Jedi executable name (IODA Converter Name)
            # --------------------
            jedi_executable = 'bufr2ioda.x'
            jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                                'build', 'bin', jedi_executable)

            # Run the JEDI executable
            # -----------------------
            try:
                self.logger.info('Running '+jedi_executable_path+' with '+bufr2ioda_conv_yaml+'.')
                subprocess.run([jedi_executable_path, bufr2ioda_conv_yaml])
            except FileNotFoundError:
                self.logger.info(f'Error: File "{bufr2ioda_conv_yaml}" not found.')
            except yaml.YAMLError as e:
                self.logger.info(f'Error processing YAML file: {e}')
            else:
                self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
