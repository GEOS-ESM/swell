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
import shutil
# import filecmp

from swell.tasks.base.task_base import taskBase
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------

# # Dictionary linking each obs type to the appropriate yaml template
# '''
# obs_classes from GetBufr:
# -------------------------
# obs_class = "disc_airs_bufr,disc_amsua_bufr,gmao_amsr2_bufr,gmao_gmi_bufr,mls_nrt_nc,"
# + "ncep_1bamua_bufr,ncep_acftpfl_bufr,ncep_atms_bufr,ncep_aura_omi_bufr,ncep_avcsam_bufr,"
# + "ncep_avcspm_bufr,ncep_crisfsr_bufr,ncep_goesfv_bufr,ncep_gpsro_bufr,ncep_mhs_bufr,"
# + "ncep_mtiasi_bufr,ncep_prep_bufr,ncep_satwnd_bufr,ncep_ssmis_bufr,ncep_tcvitals,"
# + "npp_ompsnm_bufr,r21c_npp_ompslp_nc,m2scr_n21_ompslp_nc,gmao_mlst_bufr"
# '''

bufr2ioda_obs_type_dict = {
    '1bamua': 'spoc_radiance_1bamua.yaml',
    '1bmhs': 'spoc_radiance_1bmhs.yaml',
    'atms': 'spoc_radiance_atms.yaml',

    # avhrr
    'avhrr': 'spoc_radiance_avhrr.yaml',
    'ncep_avcsam_bufr': 'spoc_radiance_avhrr.yaml',
    'ncep_avcspm_bufr': 'spoc_radiance_avhrr.yaml',
    'avcsam': 'spoc_radiance_avhrr.yaml',
    'avcspm': 'spoc_radiance_avhrr.yaml',
    
    # cris 
    # 'cris': 'spoc_radiance_cris-fsr.yaml',
    # 'crisf4': 'spoc_radiance_cris-fsr.yaml',
    # 'ncep_crisfsr_bufr': 'spoc_radiance_cris-fsr.yaml',

    'mtiasi': 'spoc_radiance_mtiasi.yaml',
    'ssmis': 'spoc_radiance_ssmis.yaml',

    # gpsro
    'ncep_gpsro_bufr': 'spoc_gnssro.yaml',
    'gpsro': 'spoc_gnssro.yaml',

    # prepbufr
    'ncep_acftpfl_bufr': 'spoc_prepbufr_aircraft.yaml',
    'acftpfl': 'spoc_prepbufr_aircraft.yaml',
    'acft_profiles': 'spoc_prepbufr_aircraft.yaml',  

    # Rest of obs_classes from GetBufr 
    # 'gmao_amsr2_bufr': 'spoc_radiance_amsr2.yaml',
    # 'gmao_gmi_bufr': 'spoc_radiance_gmi.yaml',
    # 'ncep_1bamua_bufr': 'spoc_radiance_amsua_1bamua.yaml',
    # 'ncep_acftpfl_bufr': 'spoc_prepbufr_aircraft.yaml',
    # 'ncep_atms_bufr': 'spoc_radiance_atms.yaml',
    # 'ncep_aura_omi_bufr': 'spoc_retrieval_ozone_omi.yaml',
    # 'ncep_avcsam_bufr': 'spoc_radiance_avhrr.yaml',
    # 'ncep_avcspm_bufr': 'spoc_radiance_avhrr.yaml',
    # 'ncep_crisfsr_bufr': 'spoc_radiance_cris-fsr.yaml',
    # 'ncep_gpsro_bufr': 'spoc_gnssro.yaml',
    # 'ncep_mhs_bufr': 'spoc_radiance_mhs_1bmhs.yaml',
    # 'ncep_mtiasi_bufr': 'spoc_radiance_iasi.yaml',
    # 'ncep_ssmis_bufr': 'spoc_radiance_ssmis.yaml',
    # 'npp_ompsnm_bufr': 'spoc_retrieval_ozone_ompstc.yaml',
    # 'r21c_npp_ompslp_nc': 'spoc_retrieval_ozone_ompslp.yaml',
    # 'm2scr_n21_ompslp_nc': 'spoc_retrieval_ozone_ompslp.yaml',
    # 'disc_amsua_bufr': 'spoc_radiance_amsua_esamua.yaml'
}
# --------------------------------------------------------------------------------------------------


class BufrToIoda(taskBase):

    # python split filename by delimiter period and then search for string in the resulting list
    def find_obstype_match(self, filename):
        """
        Splits the filename by '.' and returns the first match found in obs_type_search_dict.
        Prints the match if found, otherwise prints 'No match found.'

        Dictionary:
        bufr2ioda_obs_type_dict = {
                # ... see above ...
                # ... subject to change ...
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
            self.logger.info(f'bufr_file_source_path:  {bufr_file_source_path}')
            self.logger.info(f'obsdatain:  {obsdatain}')
            self.logger.info(f'obsdataout:  {obsdataout}')
            self.logger.info(f'ioda_file_target_path:  {ioda_file_target_path}')
            self.logger.info(f'bufr_file_obs_type:  {bufr_file_obs_type}')
        except yaml.YAMLError as e:
            self.logger.info(f'Error processing find_obstype_match: {e}')

        # Determine the target path of the generated yaml file
        # ----------------------------------------------------
        if yaml_file_target is None:
            # Overwrite original if no output file is specified
            # yaml_file_target = os.path.join(self.cycle_dir(), f'bufr_mapping_{bufr_file_obs_type}.yaml')
            yaml_file_target = os.path.join(self.cycle_dir(), f'spoc_radiance_{bufr_file_obs_type}.yaml')

            self.logger.info(f'bufr_file_obs_type:  {bufr_file_obs_type}.')
            self.logger.info(f'YAML template used:  {self.cycle_dir()}.')
            self.logger.info(f'yaml_file_source:  {yaml_file_source}.')
            self.logger.info(f'yaml_file_target {yaml_file_target}.')

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
            yaml_file_target = os.path.join(self.cycle_dir(), f'spoc_radiance_{bufr_file_obs_type}.yaml')

        self.logger.info(f'YAML template used:  {yaml_file_source}.')
        self.logger.info(f'YAML file saved as {yaml_file_target}.')

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
            self.logger.info("\n" + "="*85)
            self.logger.info(f"PROCESSING FILE: {bufr_file_source_path}")

            # self.logger.info(f'bufr_file_source_path: {bufr_file_source_path}')
            # Target file ~ conversion output file name (should end in .nc4).
            # Use the same name but replace the suffix.

            # Obs Type directories
            # find the obs type from file name
            bufr_file_obs_type = self.find_obstype_match(bufr_file_source_path)

            # --- CHECK: Skip if no matching obs type was found ---
            if bufr_file_obs_type is None:
                self.logger.info(f'SKIPPING: No valid observation type mapping found for {bufr_file_source_path}.')
                continue

            self.logger.info(f' MATCH FOUND: [ {bufr_file_obs_type} ] ')

            obs_type_dir = os.path.join(ioda_dir, bufr_file_obs_type)
            os.makedirs(obs_type_dir, 0o755, exist_ok=True)
            self.logger.info(f'obs_type_dir: {obs_type_dir}')

            if bufr_file_source_path.endswith('.bufr_d'):
                # Strips off .tm00.bufr_d
                bufr_file_parts = bufr_file_source_path.rsplit('.', 2) # bufr_file_parts:    ['gdas1.231010.t00z.gpsro', 'tm00', 'bufr_d'] 
                base_name = bufr_file_source_path.rsplit('.', 2)[0]    # bufr_file_parts[0]:   gdas1.231010.t00z.gpsro   
            else:
                # Use the full name for files like gdas1.20231010.t00z.prepbufr.acft_profiles
                bufr_file_parts = bufr_file_source_path
                base_name = bufr_file_source_path

            self.logger.info(f'bufr_file_parts: {bufr_file_parts}')
            self.logger.info(f'bufr_file_parts[0]: {bufr_file_parts[0]}')
            ioda_file_target_name = bufr_file_parts[0] + '.{splits/satId}.tm00.nc4' 
            ioda_file_target_path = os.path.join(ioda_dir, ioda_file_target_name)
            ioda_file_target_path_quoted = f"'{ioda_file_target_path}'"
            self.logger.info(f'ioda_file_target_path_quoted: {ioda_file_target_path_quoted}')

            # --- CHECK: Skip if output files already exist for this bufr file ---
            # Check if any .nc4 files matching the base filename (which includes date) exist in obs_type_dir
            existing_files_pattern = os.path.join(obs_type_dir, base_name) #f"{bufr_file_parts[0]}.*.nc4")
            self.logger.info(f'Checking existing_files_pattern: {existing_files_pattern}')
            existing_files = glob.glob(existing_files_pattern)
            
            if len(existing_files) > 0:
                self.logger.info(f'SKIPPING: Output files already exist for {bufr_file_source_path}: {existing_files}')
                continue

            bufr2ioda_conv_yaml = self.get_bufr_mapping_yaml(bufr_path_file, ioda_file_target_path,
                                                              path_to_ioda_conv_yaml_tmpl_dir)
            self.logger.info(f'bufr_path_file: {bufr_path_file}')
            self.logger.info(f'bufr2ioda_conv_yaml: {bufr2ioda_conv_yaml}')
            # self.logger.info(f"ioda_file_target_path: {ioda_file_target_path}")

            # Jedi executable name (IODA Converter Name)
            # --------------------
            jedi_executable_path = 'bufr2netcdf.x'
            
            # CLI Command
            # ------------
            # bufr2netcdf.x [bufr file] [bufr_mapping.yaml] 
            # bufr2netcdf.x bufr_path_file bufr2ioda_conv_yaml 
            # cli_command = [jedi_executable_path, bufr_path_file, bufr2ioda_conv_yaml]

            # will make the ioda files in the current directory
            # later on, bufr_to_ioda.py will move them to the run directory and rename them. 
            # current work around for {splits/satid} functionality 

            try:
                self.logger.info(f'Converting {bufr_file_obs_type} bufr files')
                self.logger.info('Running '+jedi_executable_path+' with '+bufr2ioda_conv_yaml+'.')
                self.logger.info(f"Execution cli line: {jedi_executable_path} --no-gather {bufr_path_file} {bufr2ioda_conv_yaml}")
                subprocess.run([jedi_executable_path, '--no-gather', bufr_path_file, bufr2ioda_conv_yaml])
            except FileNotFoundError:
                self.logger.info(f'Error: File jedi_executable_path = "{jedi_executable_path}" not found.')
                self.logger.info(f'Error: File bufr_path_file = "{bufr_path_file}" not found.')
                self.logger.info(f'Error: File bufr2ioda_conv_yaml = "{bufr2ioda_conv_yaml}" not found.')
            except YAMLError as e:
                self.logger.info(f'Error processing YAML file: {e}')
            else:
                self.logger.info('Conversion to ioda complete, now exiting.') 
                self.logger.info(f"Execution cli line: {jedi_executable_path}, --no-gather, {bufr_path_file}, {bufr2ioda_conv_yaml}") 

            try:
                # moving the output to ioda/{obs_type_dir}
                temporary_files_pattern = os.path.join(os.getcwd(),'temporary_*.nc')
                self.logger.info(f'Moving converted {bufr_file_obs_type} files to {obs_type_dir}')
                temporary_ioda_files = glob.glob(temporary_files_pattern)
                for temporary_ioda_file in temporary_ioda_files:
                    shutil.move(str(temporary_ioda_file), str(obs_type_dir))
                               
                # change file names
                # Get list of all files named temporary_*.nc and rename them based on the name of the original bufr file 
                temporary_files_pattern = os.path.join(obs_type_dir, 'temporary_*.nc') # ex: temporary_metop-a_1777056876.nc  
                temporary_ioda_files = glob.glob(temporary_files_pattern)
                for temporary_ioda_file in temporary_ioda_files:
                    if os.path.exists(temporary_ioda_file):
                        split_satid = temporary_ioda_file.rsplit('_', 2)[1]     # ex: ['temporary', 'n18', '1777056876.nc'] ['...{cycle_dir}/geos_atmosphere/temporary', 'metop-a', '1777056876.nc']
                        self.logger.info(f'bufr_file_parts:  {bufr_file_parts} ')        
                        self.logger.info(f'bufr_file_parts[0]:  {bufr_file_parts[0]} ')        
                        new_filename = bufr_file_parts[0] + '.' + split_satid + '.tm00.nc4'                       
                        self.logger.info(f'new_filename:  {new_filename} ')        
                        new_filename = os.path.join(obs_type_dir, new_filename)
                        self.logger.info(f'new_filename as full path:  {new_filename} ')              
                        if not os.path.exists(new_filename):
                            os.rename(temporary_ioda_file, new_filename) 
                            self.logger.info(f'File {temporary_ioda_file} renamed to {new_filename}.')        
                        else:
                            self.logger.info(f'File already exists {new_filename}. File will not be renamed.')        
                    else:
                        self.logger.info(f'File {temporary_ioda_file} not found')
                
            except FileNotFoundError:
                self.logger.info(f'Error: File jedi_executable_path = "{jedi_executable_path}" not found.')
            except YAMLError as e:
                self.logger.info(f'Error processing YAML file: {e}')
            else:
                self.logger.info('Conversion to ioda complete, now exiting.') 
                self.logger.info(f"RUNNING CONVERSION CLI EXECUTION: {jedi_executable_path} --no-gather {bufr_path_file} {bufr2ioda_conv_yaml}") 
                self.logger.info(
                    f"\n"
                    "Current bufr_to_ioda workflow: {jedi_executable_path} --no-gather {bufr_path_file} {bufr2ioda_conv_yaml}. "
                    "Will make the ioda files in the current directory. bufr_to_ioda.py will then move them to the run directory and rename them. "
                    "This current method is a work around for {{splits/satid}} functionality."
                    "\n --------- "
                )
# --------------------------------------------------------------------------------------------------
