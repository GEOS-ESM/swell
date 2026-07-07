# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import subprocess
from pathlib import Path

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

obs_builder_dict = {
    '1bamua': 'radiance_amsua_1bamua.py',
    '1bmhs': 'radiance_mhs_1bmhs.py',
    'atms': 'radiance_atms.py',

    # avhrr
    'avhrr': 'radiance_avhrr.py',
    'ncep_avcsam_bufr': 'radiance_avhrr.py',
    'ncep_avcspm_bufr': 'radiance_avhrr.py',
    'avcsam': 'radiance_avhrr.py',
    'avcspm': 'radiance_avhrr.py',

    # cris
    # 'cris': 'spoc_radiance_cris-fsr.py',
    # 'crisf4': 'spoc_radiance_cris-fsr.py',
    # 'ncep_crisfsr_bufr': 'spoc_radiance_cris-fsr.py',

    'mtiasi': 'radiance_iasi.py',
    'ssmis': 'radiance_ssmis.py',
    # 'ssmisu': 'spoc_radiance_ssmis.py',

    # gpsro
    'ncep_gpsro_bufr': 'gnssro.py',
    'gpsro': 'gnssro.py',

    # prepbufr
    'ncep_acftpfl_bufr': 'prepbufr_aircraft.py',
    'acftpfl': 'prepbufr_aircraft.py',
    'acft_profiles': 'prepbufr_aircraft.py',

    # Rest of obs_classes from GetBufr
    # 'gmao_amsr2_bufr': 'spoc_radiance_amsr2.py',
    # 'gmao_gmi_bufr': 'spoc_radiance_gmi.py',
    # 'ncep_1bamua_bufr': 'spoc_radiance_amsua_1bamua.py',
    # 'ncep_acftpfl_bufr': 'spoc_prepbufr_aircraft.py',
    # 'ncep_atms_bufr': 'spoc_radiance_atms.py',
    # 'ncep_aura_omi_bufr': 'spoc_retrieval_ozone_omi.py',
    # 'ncep_avcsam_bufr': 'spoc_radiance_avhrr.py',
    # 'ncep_avcspm_bufr': 'spoc_radiance_avhrr.py',
    # 'ncep_crisfsr_bufr': 'spoc_radiance_cris-fsr.py',
    # 'ncep_gpsro_bufr': 'spoc_gnssro.py',
    # 'ncep_mhs_bufr': 'spoc_radiance_mhs_1bmhs.py',
    # 'ncep_mtiasi_bufr': 'spoc_radiance_iasi.py',
    # 'ncep_ssmis_bufr': 'spoc_radiance_ssmis.py',
    # 'npp_ompsnm_bufr': 'spoc_retrieval_ozone_ompstc.py',
    # 'r21c_npp_ompslp_nc': 'spoc_retrieval_ozone_ompslp.py',
    # 'm2scr_n21_ompslp_nc': 'spoc_retrieval_ozone_ompslp.py',
    # 'disc_amsua_bufr': 'spoc_radiance_amsua_esamua.py'
}
# --------------------------------------------------------------------------------------------------


class BufrToIoda(taskBase):

    def find_obstype_match(self, bufr_path_file: Path) -> str:
        """
        Find the observation type from obs_builder_dict

        Parameters:
        bufr_path_file: Path to input bufr file (e.g. "gdas1.20231010.t00z.atms.tm00.bufr_d")

        Returns:
        obs type matching the filename (e.g. "atms")
        """

        parts = bufr_path_file.name.split('.')
        for part in parts:
            if part in obs_builder_dict:
                self.logger.info(f'Match found: {part}')
                return part

        valid_obs_types = list(obs_builder_dict.keys())
        self.logger.info(f"No match found in file `{bufr_path_file}`. "
                         f"A valid obs_type part must be one of {valid_obs_types}")
        return None

    # --------------------------------------------------------------------------------------------------

    def get_obs_builder_file(self,
                             spoc_script_path: Path,
                             obs_type: str) -> Path:
        """
        Returns the path to the ObsBuilder python file

        Parameters:
        spoc_script_path: Path to the spoc scripts

        Returns:
        Path to the specific ObsBuilder python file
        """

        obs_builder_file = obs_builder_dict[obs_type]
        obs_builder_glob = list(spoc_script_path.glob(obs_builder_file))
        if len(obs_builder_glob) > 0:
            return obs_builder_glob[0]
        else:
            self.logger.info(f'ObsBuilder file `{obs_builder_file}` not '
                             'found in config directory.')

        return None

    # --------------------------------------------------------------------------------------------------

    def execute(self):
        """
        Converts collected bufr files to ioda using ObsBuilder python files
        """

        bufr_dir = Path(self.cycle_dir()) / 'bufr'

        ioda_dir = Path(self.cycle_dir()) / 'ioda'

        ioda_dir.mkdir(mode=0o755, parents=True, exist_ok=True)

        spoc_script_path = Path(self.experiment_path()) / 'spoc' / 'dump' / 'scripts' / 'atmosphere'

        # Get the list of bufr files to convert
        bufr_path_files = list(bufr_dir.glob('*bufr*'))

        for bufr_path_file in bufr_path_files:
            obs_type = self.find_obstype_match(bufr_path_file)
            obs_builder_file = self.get_obs_builder_file(spoc_script_path, obs_type)

            if obs_builder_file is None:
                self.logger.info(f'SKIPPING: No valid observation type '
                                 f'mapping found for {bufr_path_file}')
                continue

            self.logger.info(f' MATCH FOUND: [ {obs_builder_file} ]')

            # Get the name of the output directory
            obs_type_dir = ioda_dir / obs_type
            obs_type_dir.mkdir(mode=0o755, exist_ok=True)
            self.logger.info(f'obs_type_dir: {obs_type_dir}')

            if bufr_path_file.suffix == '.bufr_d':
                bufr_file_parts = bufr_path_file.name.rsplit('.', 2)
                base_name = bufr_path_file.name.rsplit('.', 2)[0]
            else:
                bufr_file_parts = bufr_path_file.name
                base_name = bufr_path_file.name

            # Output IODA filepath
            ioda_file_target = obs_type_dir / (bufr_file_parts[0] + '.{splits/satId}.tm00.nc4')

            existing_files = list(obs_type_dir.glob(f'{base_name}*'))
            if len(existing_files) > 0:
                self.logger.info(f'SKIPPING: Output files already exist for {bufr_path_file}: '
                                 f'{existing_files}')
                continue

            subprocess.run(['python', obs_builder_file, '--input', bufr_path_file,
                            '--output', ioda_file_target], check=True)

# --------------------------------------------------------------------------------------------------
