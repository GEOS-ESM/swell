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


class UseAcquire(taskBase):

    def execute(self) -> None:

        swell_exp_path = self.experiment_path()
        perl_executable_path = os.path.join(swell_exp_path, 'GMAO_perllib')

        env_dict = {"PATH": os.environ.get('PATH') + ":" +perl_executable_path}

        subprocess.run(['acquire_obsys'], env=env_dict)

        """
        Translated c-shell to python:
        satbfrdb = os.path.join(swell_exp_path, "GEOS_mksi", "ObsClass")
        my_exp = "/gpfsm/dnb05/projes/p139/rtodling/TEST/GETBUFR/"

        work = os.path.join(my_exp, "work")
        spool = os.path.join(my_exp, "spool")

        obs_class = "disc_airs_bufr,disc_amsua_bufr,gmao_amsr2_bufr,gmao_gmi_bufr,mls_nrt_nc,ncep_1bamua_bufr,ncep_acftpfl_bufr,ncep_atms_bufr,ncep_aura_omi_bufr,ncep_avcsam_bufr,ncep_avcspm_bufr,ncep_crisfsr_bufr,ncep_goesfv_bufr,ncep_gpsro_bufr,ncep_mhs_bufr,ncep_mtiasi_bufr,ncep_prep_bufr,ncep_satwnd_bufr,ncep_ssmis_bufr,ncep_tcvitals,npp_ompsnm_bufr,r21c_npp_ompslp_nc,m2scr_n21_ompslp_nc,gmao_mlst_bufr"

        nymd = "20231010"
        nhms = "120000"

        nfreq = "060000"
        nstep = "1"

        subprocess.run(["acquire_obsys", "-v", "-d", work, "-s", spool, "strict", "-ssh", nymd, nhms, nfreq, nstep, obs_class])

        """

# --------------------------------------------------------------------------------------------------
