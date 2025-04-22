# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------

# ----- for later
"""
### run directory ------------------------
        # Get cycle dir and create if needed
        # ----------------------------------
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr')
        os.makedirs(bufr_dir, 0o755, exist_ok=True)
"""


class GetBufrUseAcquire(taskBase):

    def execute(self) -> None:

        swell_exp_path = self.experiment_path()
        perl_executable_path = os.path.join(swell_exp_path, 'GMAO_perllib')

        env_dict = os.environ
        env_dict['PATH'] = env_dict["PATH"] + ":" + perl_executable_path

        # add these to the config file ~ i.e. the experiment yaml
        bymd = self.config.bymd()
        bhms = self.config.bhms()
        ihms = self.config.ihms() # nfreq
        nstep = self.config.nstep()
        obsclass = self.config.obsclass()
        #path_to_obsys_rc = self.config.path_to_obsys_rc()

        #work = os.path.join(swell_exp_path, "work")
        #cycle_dir = os.path.join(swell_exp_path, 'run/20211212T000000Z/geos_atmosphere/bufr')
        # Get cycle dir and create if needed
        # ----------------------------------
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr/.')
        os.makedirs(bufr_dir, 0o755, exist_ok=True)

        path_to_obsys_rc = os.path.join(bufr_dir, 'obsys-nccs.rc')

        print(f'{bymd},{bhms},{ihms},{nstep},{obsclass},{path_to_obsys_rc},{self.cycle_dir()}')
        print(f'-- subprocess --')

        #spool = os.path.join(swell_exp_path, "spool")

        #bymd = '20211212'
        #bhms = '120000'
        ihms = '060000' # window_length in experiment.yaml
        nstep = '1'
        #obsclass = 'ncep_1bamua_bufr'
        #path_to_obsys_rc = '/discover/nobackup/sicohen/SwellExperiments/swell-convert_bufr/GEOS_mksi/ObsClass/obsys-nccs.rc' 
        #bufr_dir = '/discover/nobackup/sicohen/SwellExperiments/swell-convert_bufr/run/20211212T000000Z/geos_atmosphere/bufr/.'

        subprocess.run(["acquire_obsys", "-drc", path_to_obsys_rc, "-d", bufr_dir, bymd, bhms, ihms, nstep, obsclass], env=env_dict)

        #subprocess.run(["acquire_obsys", "-v", "-d", work, "-s", spool,
        #               "strict", "-ssh", nymd, nhms, ihms, nstep, obs_class])
        """
        # 1. cp/link obsys.rc file(s) to ____
        # Create symlink from target to source
        self.logger.info(f'Creating sym link from {bufr_path_file} to '
                         f'{bufr_file_target}')
        os.symlink(bufr_path_file, bufr_file_target)
        # Parse config
        # ------------
        path_to_geos_mksi = self.config.observing_system_records_mksi_path()
        tag = self.config.observing_system_records_mksi_path_tag()

        self.config.observing_system_records_mksi_path()
        os.path.join(self.experiment_path(), 'GEOS_mksi')
        
        # Link the source code directory
        link_path(self.config.observing_system_records_mksi_path(),
                    os.path.join(self.experiment_path(), 'GEOS_mksi/ObsClass/obsys-nccs.rc'))

        # 
        subprocess.run(['acquire_obsys', '-h'], env=env_dict)
        subprocess.run(["acquire_obsys", "-v", "-d", work, "-s", spool,
                        "strict", "-ssh", nymd, nhms, nfreq, nstep, obs_class])
        Translated c-shell to python:
        satbfrdb = os.path.join(swell_exp_path, "GEOS_mksi", "ObsClass")
        my_exp = "/gpfsm/dnb05/projes/p139/rtodling/TEST/GETBUFR/"

        work = os.path.join(my_exp, "work")
        spool = os.path.join(my_exp, "spool")

        obs_class = "disc_airs_bufr,disc_amsua_bufr,gmao_amsr2_bufr,gmao_gmi_bufr,mls_nrt_nc,"
        + "ncep_1bamua_bufr,ncep_acftpfl_bufr,ncep_atms_bufr,ncep_aura_omi_bufr,ncep_avcsam_bufr,"
        + "ncep_avcspm_bufr,ncep_crisfsr_bufr,ncep_goesfv_bufr,ncep_gpsro_bufr,ncep_mhs_bufr,"
        + "ncep_mtiasi_bufr,ncep_prep_bufr,ncep_satwnd_bufr,ncep_ssmis_bufr,ncep_tcvitals,"
        + "npp_ompsnm_bufr,r21c_npp_ompslp_nc,m2scr_n21_ompslp_nc,gmao_mlst_bufr"

        nymd = "20231010"
        nhms = "120000"

        nfreq = "060000"
        nstep = "1"

        subprocess.run(["acquire_obsys", "-v", "-d", work, "-s", spool,
                        "strict", "-ssh", nymd, nhms, nfreq, nstep, obs_class])

        acquire_obsys -drc ./obsys-nccs.rc -d . 20040615 120000 060000 6     1bamua
        acquire_obsys [...    options       ...]    bymd   bhms   ihms nstep obclass



        """
        """

#class GetBufr(taskBase):

    #def execute(self) -> None:

        # Get the build method
        # --------------------
        bufr_path = self.config.path_to_bufr()

        # Replace bufr_path datetime string with the actual datetime
        # --------------------------------------------------------------
        cycle_time_dto = self.cycle_time_dto()
        bufr_path = os.path.join(bufr_path, cycle_time_dto.strftime('Y%Y'), cycle_time_dto.strftime('M%m'))

        # Get list of bufr to test with
        # --------------------------------
        filename_dto = '*' + cycle_time_dto.strftime('%y%d%m.t%Hz') + '*'
        bufr_path_files_pattern = os.path.join(bufr_path, filename_dto)
        bufr_path_files = glob.glob(bufr_path_files_pattern)

        # Get cycle dir and create if needed
        # ----------------------------------
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr')
        os.makedirs(bufr_dir, 0o755, exist_ok=True)

        # Assert that some files were found
        self.logger.assert_abort(len(bufr_path_files) != 0 is not None, f'No bufr ' +
                                 f'files found in the source directory ' +
                                 f'\'{bufr_path_files_pattern}\'')

        # Copy all the files into the cycle directory
        # -------------------------------------------
        for bufr_path_file in bufr_path_files:

            # Source file
            bufr_file_source = os.path.basename(bufr_path_file)

            # Target file
            bufr_file_target = os.path.join(bufr_dir, bufr_file_source)

            # Remove target file if it exists (might be a link)
            if os.path.exists(bufr_file_target):
                os.remove(bufr_file_target)

            # Create symlink from target to source
            self.logger.info(f'Creating sym link from {bufr_path_file} to '
                             f'{bufr_file_target}')
            os.symlink(bufr_path_file, bufr_file_target)
        """

# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
