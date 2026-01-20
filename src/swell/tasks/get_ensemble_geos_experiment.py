# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import isodate
import os
import tarfile

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.utilities.datetime_util import datetime_formats

# --------------------------------------------------------------------------------------------------

task_name = 'GetEnsembleGeosExperiment'

@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.is_cycling = True
        self.is_model = True
        self.questions = [
            qd.background_experiment(),
            qd.background_time_offset(),
            qd.geos_x_ensemble_directory()
        ]

# --------------------------------------------------------------------------------------------------


class GetEnsembleGeosExperiment(taskBase):

    def execute(self):

        """Acquires background files from a previous GEOS-FP experiment. This task
        is specific to a 6-hour DA window and GEOS-FP experiment. Hence, it makes
        certain assumptions about the file structure and naming conventions
        (examples are provided for the x0048 experiment):

            - Background archive file:       x0050.atmens_ebkgx.20231009_21z.tar
            - First background file:         ensbkgx/mem001/x0050.bkg_clcv.20231009_2100z.nc4
            .
            .
            .
            - Last background file:          ensbkgx/mem001/x0050.bkg_clcv.20231010_0300z.nc4

        The name of the *bkgcrst.*.tar files correspond to the forecast start time.
        The file names in these tar archives corresponds to the background files
        within the DA window, therefore 7 background files are extracted for a
        6-hour window.

        """

        # Parse config
        # ------------
        background_experiment = self.config.background_experiment()
        geos_x_ensemble_directory = self.config.geos_x_ensemble_directory()
        background_time_offset = self.config.background_time_offset()

        # Since this is an optional task, check if the geos_x_ensemble_directory is
        # set to /dev/null, if so fail the task
        # ---------------------------------------------------------------------
        if (
                (geos_x_ensemble_directory is None) or
                (geos_x_ensemble_directory.startswith("/dev/null"))
        ):
            self.logger.abort('No X ensemble location specified, failing task')
            return

        # Convert to datetime duration
        # ----------------------------
        background_time_offset_dur = isodate.parse_duration(background_time_offset)

        # Get the ensemble experiment start time
        # -----------------------------------------
        bkg_exp_start_dto = self.cycle_time_dto()-background_time_offset_dur
        bkg_exp_start_geos = bkg_exp_start_dto.strftime(datetime_formats['gsi_nc_diag_format'])

        # Create cycle directory if needed
        # --------------------------------
        if not os.path.exists(self.cycle_dir()):
            os.makedirs(self.cycle_dir(), 0o755, exist_ok=True)

        # Define the source tar folder and file
        # -------------------------------------
        ens_tar_file = f'{background_experiment}.atmens_ebkgx.{bkg_exp_start_geos}.tar'
        ens_tar = os.path.join(geos_x_ensemble_directory,
                               background_experiment,
                               'atmens',
                               bkg_exp_start_dto.strftime('Y%Y'),
                               bkg_exp_start_dto.strftime('M%m'),
                               ens_tar_file)

        # Link the ensemble tar archive to the cycle directory
        # ------------------------------------------------------
        self.logger.info(' Linking GEOS-FP archive file: ' + ens_tar)
        self.geos.linker(ens_tar, ens_tar_file, dst_dir=self.cycle_dir())

        # Drop the suffix from the filename
        ens_tar_folder = os.path.splitext(ens_tar_file)[0]

        # Path to restarts in the cycle directory
        # ---------------------------------------
        cycle_tar = os.path.join(self.cycle_dir(), ens_tar_file)

        with tarfile.open(cycle_tar) as cycle_tar_file:
            all_members = cycle_tar_file.getmembers()
            # Filter for top-level mem* directories
            member_dirs = [m for m in all_members if m.isdir() and
                           m.name.startswith(ens_tar_folder + '/ensbkgx/mem')]

            for member_dir in member_dirs:
                # Extract member number (e.g., '008' from 'x0050.atmens_ebkg.20231009_21z/mem008')
                member_num = member_dir.name.split('/')[-1][3:]  # Skip 'mem' prefix

                # Create member-specific directory
                member_path = os.path.join(self.cycle_dir(), 'ebkg', f'mem{member_num}')
                os.makedirs(member_path, exist_ok=True)

                # Get all files within this member directory
                member_files = [m for m in all_members if
                                m.name.startswith(member_dir.name + '/') and
                                not m.isdir()]

                # Process each file in the member directory
                for member_file in member_files:
                    # Get date from filename
                    member_date_str = member_file.name.split('.')[-2]
                    member_date_dto = dt.strptime(member_date_str, '%Y%m%d_%H00z')

                    # Create JEDI filename with member info
                    jedi_date = member_date_dto.strftime(datetime_formats["ensemble_format"])
                    ens_filename_jedi = f'geos.mem{member_num}.{jedi_date}.nc4'

                    # Extract file to member directory
                    member_file.name = ens_filename_jedi
                    cycle_tar_file.extract(member_file, member_path)
                    eff_path = member_path.split('/')[-2:] + [ens_filename_jedi]
                    self.logger.info(f' Extracted and renamed file to: {"/".join(eff_path)}')
# --------------------------------------------------------------------------------------------------
