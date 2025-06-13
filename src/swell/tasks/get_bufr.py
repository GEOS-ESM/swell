# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess

from swell.utilities.datetime_util import datetime_formats
from swell.tasks.base.task_base import taskBase
import datetime

# --------------------------------------------------------------------------------------------------

class GetBufr(taskBase):
    '''

    bymd = '20211212'
    bhms = '120000'
    ihms = '060000' # window_length in experiment.yaml
    nstep = '1'
    obsclass = 'ncep_1bamua_bufr'
    geos_mksi_obsysrc_path = '/SwellExperiments/swell-convert_bufr/GEOS_mksi/ObsClass/obsys-nccs.rc' 
    bufr_dir = '/SwellExperiments/swell-convert_bufr/run/20211212T000000Z/geos_atmosphere/bufr/.'

    '''

    def execute(self) -> None:

        # experiment directory in SwellExperiments
        swell_exp_path = self.experiment_path()
        # use_acquire
        perl_executable_path = os.path.join(swell_exp_path, 'GMAO_perllib')
        # CloneGeosMksi
        geos_mksi  = os.path.join(swell_exp_path, 'GEOS_mksi')
        # .rc database 
        geos_mksi_obsysrc_path = os.path.join(swell_exp_path, 'GEOS_mksi/ObsClass/obsys-nccs.rc')

        # 
        env_dict = os.environ
        env_dict['PATH'] = env_dict["PATH"] + ":" + perl_executable_path


        # --------------------------------------------------------------

        print(self.cycle_time_dto())
        #print(self.observations())

        # Convert cycle time datetime object to string with format yyyymmdd
        bymd = datetime.datetime.strftime(self.cycle_time_dto(),
                                                      datetime_formats['ymd_format'])
        # Convert cycle time datetime object to string with format HHmmss
        bhms = datetime.datetime.strftime(self.cycle_time_dto(),
                                                      datetime_formats['hms_format'])


        # --------------------------------------------------------------

        bufr_dir = os.path.join(self.cycle_dir(), 'bufr/.')
        os.makedirs(bufr_dir, 0o755, exist_ok=True)


        ihms = '060000' # window_length in experiment.yaml
        nstep = '1'
        obsclass = 'ncep_1bamua_bufr' # ['ncep_1bamua_bufr','ncep_1bamub_bufr']
        #obsclass = self.observations()

        #spool = os.path.join(swell_exp_path, "spool")
        #bymd = '20211212'
        #bhms = '120000'
        #geos_mksi_obsysrc_path = 'SwellExperiments/swell-convert_bufr/GEOS_mksi/ObsClass/obsys-nccs.rc' 
        #bufr_dir = 'SwellExperiments/swell-convert_bufr/run/20211212T000000Z/geos_atmosphere/bufr/.'

        subprocess.run(["acquire_obsys", "-drc", geos_mksi_obsysrc_path, "-d", bufr_dir, bymd, bhms, ihms, nstep, obsclass], env=env_dict)

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
 
# --------------------------------------------------------------------------------------------------
