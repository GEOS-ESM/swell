# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess

from datetime import datetime as dt
from swell.utilities.datetime_util import datetime_formats
from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
from swell.utilities.question_defaults import QuestionDefaults as qd

# --------------------------------------------------------------------------------------------------

task_name = 'GetBufr'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.is_cycling = True
        self.is_model = True
        self.questions = [
            qd.bufr_obs_classes()
        ]

# --------------------------------------------------------------------------------------------------


class GetBufr(taskBase):
    '''

    obs_class = "disc_airs_bufr,disc_amsua_bufr,gmao_amsr2_bufr,gmao_gmi_bufr,mls_nrt_nc,"
    + "ncep_1bamua_bufr,ncep_acftpfl_bufr,ncep_atms_bufr,ncep_aura_omi_bufr,ncep_avcsam_bufr,"
    + "ncep_avcspm_bufr,ncep_crisfsr_bufr,ncep_goesfv_bufr,ncep_gpsro_bufr,ncep_mhs_bufr,"
    + "ncep_mtiasi_bufr,ncep_prep_bufr,ncep_satwnd_bufr,ncep_ssmis_bufr,ncep_tcvitals,"
    + "npp_ompsnm_bufr,r21c_npp_ompslp_nc,m2scr_n21_ompslp_nc,gmao_mlst_bufr"

    bymd = '20211212'
    bhms = '120000'
    ihms = '060000' # window_length in experiment.yaml
    nstep = '1'

    '''

    def execute(self) -> None:

        # Define constants and other input arguments
        # ------------------------------------------
        NSTEP = '1'  # Number of steps
        IHMS = '060000'  # Window length

        perl_executable_path = os.path.join(self.experiment_path(), 'GMAO_perllib')
        geos_mksi_obsysrc_path = os.path.join(self.experiment_path(),
                                              'GEOS_mksi/ObsClass/obsys-nccs.rc')

        # Environment variables for acquire_obsys
        env_dict = os.environ
        env_dict['PATH'] = env_dict["PATH"] + ":" + perl_executable_path

        # Convert cycle times to the format BUFR script expects
        bymd = dt.strftime(self.cycle_time_dto(), datetime_formats['ymd_format'])
        bhms = dt.strftime(self.cycle_time_dto(), datetime_formats['hms_format'])

        # Create the BUFR directory
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr')
        os.makedirs(bufr_dir, 0o755, exist_ok=True)

        # Get BUFR obs classes from mksi and acquire them
        # -----------------------------------------------
        obsclasses = self.config.bufr_obs_classes()

        for obsclass in obsclasses:

            # Construct perl command to run
            command = [
                'acquire_obsys',
                '-drc', geos_mksi_obsysrc_path,
                '-d', bufr_dir,
                bymd, bhms, IHMS, NSTEP, obsclass
            ]

            subprocess.run(command, env=env_dict)

# --------------------------------------------------------------------------------------------------
