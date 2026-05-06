# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import subprocess
import shutil
from ruamel.yaml import YAML
# import filecmp

from swell.tasks.base.task_base import taskBase

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
    # 'ssmisu': 'spoc_radiance_ssmis.yaml',

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

        valid_obs_types = list(bufr2ioda_obs_type_dict.keys())
        self.logger.info(f"No match found in filename '{filename}'. "
                         f"A valid obs_type part must be one of {valid_obs_types}")

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

        # Log a summary of all input variables
        self.logger.info(
            f"\n"
            f"--- get_bufr_mapping_yaml Input Summary ---\n"
            f"  bufr_file_source_path           : {bufr_file_source_path}\n"
            f"  ioda_file_target_path           : {ioda_file_target_path}\n"
            f"  path_to_ioda_conv_yaml_tmpl_dir : {path_to_ioda_conv_yaml_tmpl_dir}\n"
            f"  yaml_file_source                : {yaml_file_source}\n"
            f"  yaml_file_target                : {yaml_file_target}\n"
            f"-------------------------------------------"
        )

        # Find the obs type from file name
        # -----------------------------------
        bufr_file_obs_type = self.find_obstype_match(bufr_file_source_path)

        if bufr_file_obs_type is None:
            self.logger.abort(f"Cannot determine obs type for {bufr_file_source_path}")

        # Determine the source YAML file path based on obs_type
        # yaml_file_source ~ default location: src/swell/configuration/jedi/bufr2ioda/bufr2netcdf_x/
        # ------------------------------------------------------------------------------------------
        if yaml_file_source is None:
            try:
                yaml_template_name = bufr2ioda_obs_type_dict[bufr_file_obs_type]
                yaml_file_source = os.path.join(path_to_ioda_conv_yaml_tmpl_dir, yaml_template_name)
            except KeyError:
                valid_obs_types = list(bufr2ioda_obs_type_dict.keys())
                self.logger.abort(f"Error: '{bufr_file_obs_type}' not found in dict. "
                                  f"obs_type must be one of {valid_obs_types}",
                                  exception=KeyError)

        # Determine the target path of the generated yaml file
        # yaml_file_target ~ location in the cycle_dir to copy the yaml_file_source to
        # ----------------------------------------------------------------------------
        yaml_file_target = os.path.join(
            self.cycle_dir(), f'spoc_radiance_{bufr_file_obs_type}.yaml')

        self.logger.info(f'bufr_file_obs_type: {bufr_file_obs_type}')
        self.logger.info(f'YAML template used: {yaml_file_source}')
        self.logger.info(f'YAML file will be saved as: {yaml_file_target}')

        # Copy the yaml file yaml_file_source to yaml_file_target
        try:
            shutil.copy(yaml_file_source, yaml_file_target)
            self.logger.info(f'Successfully copied YAML file to {yaml_file_target}')

        except FileNotFoundError:
            # If the source file doesn't actually exist on disk, abort cleanly
            self.logger.abort(f'Error: Source YAML file "{yaml_file_source}" not found.',
                              exception=FileNotFoundError)
        except PermissionError:
            self.logger.abort(f'Error: Permission denied when copying to "{yaml_file_target}".',
                              exception=PermissionError)

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
                                                       'configuration/jedi',
                                                       'bufr2ioda/bufr2netcdf_x/')
        self.logger.info(f'Path to yaml files found: {path_to_ioda_conv_yaml_tmpl_dir}')

        # Get list of all files in cycle dir with .bufr_d suffix or *bufr*
        bufr_path_files_pattern = os.path.join(bufr_dir, '*bufr*')
        bufr_path_files = glob.glob(bufr_path_files_pattern)

        self.logger.info(f'Bufr files found: {bufr_path_files}')

        # Assert that some files were found
        self.logger.assert_abort(len(bufr_path_files) != 0, f'No bufr ' +
                                 f'files found in the source directory ' +
                                 f'\'{bufr_path_files_pattern}\'')

        # Convert Bufr Files (one by one)
        # ------------------------------------------------------------------------------------------
        for bufr_path_file in bufr_path_files:

            # Source file ~ bufr file to be converted
            bufr_file_source_path = os.path.basename(bufr_path_file)
            self.logger.info("\n" + "=" * 85)
            self.logger.info(f"PROCESSING FILE: {bufr_file_source_path}")

            # Target file ~ conversion output file name (should end in .nc4).
            # Use the same name but replace the suffix.

            # Obs Type directories
            # find the obs type from file name
            bufr_file_obs_type = self.find_obstype_match(bufr_file_source_path)

            # -----------------------------------------------------
            # --- CHECK: Skip if no matching obs type was found ---
            if bufr_file_obs_type is None:
                self.logger.info(f'SKIPPING: No valid observation type mapping'
                                 ' found for {bufr_file_source_path}.')
                continue

            self.logger.info(f' MATCH FOUND: [ {bufr_file_obs_type} ] ')

            obs_type_dir = os.path.join(ioda_dir, bufr_file_obs_type)
            os.makedirs(obs_type_dir, 0o755, exist_ok=True)
            self.logger.info(f'obs_type_dir: {obs_type_dir}')

            if bufr_file_source_path.endswith('.bufr_d'):
                # Strips off .tm00.bufr_d
                bufr_file_parts = bufr_file_source_path.rsplit('.', 2)  # noqa
                base_name = bufr_file_source_path.rsplit('.', 2)[0]  # noqa
            else:
                # Use the full name for files like gdas1.20231010.t00z.prepbufr.acft_profiles
                bufr_file_parts = bufr_file_source_path
                base_name = bufr_file_source_path

            ioda_file_target_name = bufr_file_parts[0] + '.{splits/satId}.tm00.nc4'
            ioda_file_target_path = os.path.join(ioda_dir, ioda_file_target_name)

            # --------------------------------------------------------------------
            # --- CHECK: Skip if output files already exist for this bufr file ---
            # Check if any .nc4 files matching the base filename already exist in obs_type_dir
            existing_files_pattern = os.path.join(obs_type_dir, f"{base_name}*")
            self.logger.info(f'Checking existing_files_pattern: {existing_files_pattern}')
            existing_files = glob.glob(existing_files_pattern)

            if len(existing_files) > 0:
                self.logger.info('SKIPPING: Output files already exist for '
                                 f'{bufr_file_source_path} {existing_files}')
                continue

            bufr2ioda_conv_yaml = self.get_bufr_mapping_yaml(bufr_path_file, ioda_file_target_path,
                                                             path_to_ioda_conv_yaml_tmpl_dir)
            self.logger.info(f'bufr_path_file: {bufr_path_file}')
            self.logger.info(f'bufr2ioda_conv_yaml: {bufr2ioda_conv_yaml}')

            # Execute CLI Conversion
            # --------------------------------------------------------------------------------------

            # Jedi executable name (IODA Converter Name)
            # ------------------------------------------
            jedi_executable = 'bufr2netcdf.x'
            cli_execution_line = (f"{jedi_executable} --no-gather "
                                  f"{bufr_path_file} {bufr2ioda_conv_yaml}")

            # Log a summary of the execution variables for this specific file
            self.logger.info(
                f"\n"
                f"--- Conversion Execution Summary ---\n"
                f"  obs_type              : {bufr_file_obs_type}\n"
                f"  jedi_executable       : {jedi_executable}\n"
                f"  input_bufr_file       : {bufr_path_file}\n"
                f"  mapping_yaml_file     : {bufr2ioda_conv_yaml}\n"
                f"  ioda_target_path      : {ioda_file_target_path}\n"
                f"  full_cli_execution    : {cli_execution_line}\n"
                f"------------------------------------"
            )

            # CLI Command Structure
            # ---------------------
            # bufr2netcdf.x [bufr file] [bufr_mapping.yaml]     <---- omitting the target path

            try:
                subprocess.run([jedi_executable, '--no-gather', bufr_path_file,
                                bufr2ioda_conv_yaml], check=True)

            except FileNotFoundError:
                # This ONLY triggers if 'bufr2netcdf.x' is not found in the system PATH
                self.logger.abort(f'Error: Executable "{jedi_executable}" not found.',
                                  exception=FileNotFoundError)

            except subprocess.CalledProcessError as e:
                # This triggers if bufr2netcdf.x crashes, or if it can't find files passed to it
                self.logger.abort(f'Conversion failed! {jedi_executable} returned exit status '
                                  f'{e.returncode}.', exception=subprocess.CalledProcessError)

            else:
                self.logger.info(f'Conversion to ioda complete for {bufr_file_obs_type}.')

            # Rename converted output files
            # from bufr2netcdf.x standard name to name based on the input bufr file.
            # current work around for {splits/satid} functionality
            # --------------------------------------------------------------------------------------
            try:
                # moving the output to ioda/{obs_type_dir}
                temporary_files_pattern = os.path.join(os.getcwd(), 'temporary_*.nc')
                self.logger.info(f'Moving converted {bufr_file_obs_type} files to {obs_type_dir}')
                temporary_ioda_files = glob.glob(temporary_files_pattern)
                for temporary_ioda_file in temporary_ioda_files:
                    shutil.move(str(temporary_ioda_file), str(obs_type_dir))

                # change file names
                # Get list of all files named temporary_*.nc and rename them
                # based on the name of the original bufr file
                temporary_files_pattern = os.path.join(obs_type_dir, 'temporary_*.nc')
                temporary_ioda_files = glob.glob(temporary_files_pattern)
                for temporary_ioda_file in temporary_ioda_files:
                    if os.path.exists(temporary_ioda_file):

                        base_temp_name = os.path.basename(temporary_ioda_file)

                        # Example: 'temporary_cosmic2_755_1778082291.nc'
                        # Becomes: ['temporary', 'cosmic2', '755', '1778082291.nc']
                        parts = base_temp_name.split('_')
                        split_satid = '_'.join(parts[1:-1])  # 'cosmic2', '755',

                        # Construct the new filename
                        new_filename = bufr_file_parts[0] + '.' + split_satid + '.tm00.nc4'
                        new_file_path = os.path.join(obs_type_dir, new_filename)

                        # Log a summary of the renaming variables for this file
                        self.logger.info(
                            f"\n"
                            f"--- File Renaming Summary ---\n"
                            f"  temp_file_source : {temporary_ioda_file}\n"
                            f"  extracted_satid  : {split_satid}\n"
                            f"  base_bufr_name   : {bufr_file_parts[0]}\n"
                            f"  obs_type_dir    : {obs_type_dir}\n"
                            f"  new_filename    : {new_filename}\n"
                            f"  new_file_path    : {new_file_path}\n"
                            f"-----------------------------"
                        )

                        # Rename or remove if already exists
                        if not os.path.exists(new_file_path):
                            os.rename(temporary_ioda_file, new_file_path)
                            self.logger.info(
                                f'File {temporary_ioda_file} renamed to {new_filename}.')
                        else:
                            self.logger.info(
                                f'File already exists {new_file_path}. File will not be renamed.')

                            # Clean up the orphaned temporary file so it doesn't take up space
                            try:
                                os.remove(temporary_ioda_file)
                                self.logger.info('Cleaned up orphaned temporary file: '
                                                 f'{temporary_ioda_file}')
                            except OSError as e:
                                self.logger.info(f'Failed to delete temporary file '
                                                 f'{temporary_ioda_file}: {e}')

            except FileNotFoundError:
                self.logger.info(
                    f'Error: File jedi_executable = "{jedi_executable}" not found.')
            else:
                self.logger.info('Conversion to ioda complete, now exiting.')
                self.logger.info(f"RUNNING CONVERSION CLI EXECUTION: {jedi_executable} "
                                 f"--no-gather {bufr_path_file} {bufr2ioda_conv_yaml}")
                self.logger.info(
                    "\n"
                    f"Current bufr_to_ioda workflow: {jedi_executable} --no-gather "
                    f"{bufr_path_file} {bufr2ioda_conv_yaml}.\n"
                    "Will make the ioda files in the current directory. bufr_to_ioda.py "
                    "will then move them to the run directory and rename them.\n"
                    "This current method is a work around for {splits/satid} functionality.\n"
                    " --------- "
                )
# --------------------------------------------------------------------------------------------------
