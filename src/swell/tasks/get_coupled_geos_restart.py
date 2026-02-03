# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import copy_to_dst_dir, check_if_files_exist_in_path

# --------------------------------------------------------------------------------------------------


class GetCoupledGeosRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Copies coupled GEOS restart files to the cycle forecast directory, which are:

        - *_rst files (including the atmosphere restart file)
        - iced.nc (CICE6 restart, mandatory)
        - MOM.res.nc (MOM6 restart, mandatory)
        - mom6_increment.nc (optional)

        Restart files can be obtained by three different ways:

        1) From a previous GEOS forecast experiment (geos_homdir or geos_expdir)
        2) R2D2 retrieval (not implemented yet)
        3) External folder (user is expected to copy them manually before running the experiment)

        geos_expdir can be different from geos_homdir, in which case must be specified in the config
        file. Not it can be absolute path, however MOM6 and CICE6 restarts are expected to be in
        the RESTART subdirectory of geos_expdir.

        xx) Creates HOMDIR and EXPDIR in the experiment/GEOSgcm directory (which are names
            used by GEOS)
        xx) Obtains files from geos_homdir OR geos_expdir according to user input
        """

        self.logger.info('Obtaining GEOS restarts for a coupled simulation')

        # Get experiment directory where GEOS HOMDIR and EXPDIR will be cloned/linked
        # ---------------------------------------------------
        swell_exp_path = self.experiment_path()

        # Obtain GEOS HOMDIR and EXPDIR from user input
        self.geos_homdir = self.config.geos_homdir()
        self.geos_expdir = self.geos_homdir

        expdir_different = self.config.geos_expdir_different()

        self.logger.info('GEOS HOME directory: ' + self.geos_homdir)
        geos_homdir_path = os.path.join(swell_exp_path, 'GEOSgcm', 'GEOS_homdir')
        if os.path.exists(self.geos_homdir):
            self.logger.info('Linking GEOS HOME directory to ' + geos_homdir_path)
            # Check if link already exists, unlink first if it does
            if os.path.lexists(geos_homdir_path):
                os.unlink(geos_homdir_path)
            os.symlink(self.geos_homdir, geos_homdir_path)
            geos_expdir_path = geos_homdir_path
        else:
            self.logger.abort('GEOS_homdir does not exist: ' + self.geos_homdir)

        # If GEOS expdir is set to be different to homdir, create a link to expdir and fail if it
        # does not exist
        if expdir_different:
            self.logger.info('GEOS EXPERIMENT directory: ' + geos_expdir_path)
            self.expdir = self.config.geos_expdir()
        else:
            self.logger.info('GEOS EXPERIMENT directory is the same as GEOS HOME directory. '
                             'Set `geos_expdir_different: true` to point a different directory.')

        if expdir_different and os.path.exists(self.geos_expdir):
            geos_expdir_path = os.path.join(swell_exp_path, 'GEOSgcm', 'GEOS_expdir')
            # Check if link already exists, unlink first if it does
            if os.path.lexists(geos_expdir_path):
                self.logger.info('Unlinking existing GEOS EXPDIR link: ' + geos_expdir_path)
                os.unlink(geos_expdir_path)
            self.logger.info('Linking GEOS EXPDIR to ' + geos_expdir_path)
            os.symlink(self.expdir, geos_expdir_path)
        elif expdir_different and not os.path.exists(self.expdir):
            self.logger.abort('GEOS_expdir directory does not exist: ' + self.expdir)

        # Create forecast_dir and RESTART
        # ----------------------------
        os.makedirs(self.forecast_dir('RESTART'), 0o755, exist_ok=True)

        # Restarts should be in the EXPDIR or HOMDIR
        # -----------------------------------------
        self.initial_restarts(geos_expdir_path)

    # ----------------------------------------------------------------------------------------------

    def initial_restarts(self, geos_expdir_path: str) -> None:

        # Coupled GEOS restarts can be obtained from:
        # 1) a GEOS experiment directory
        # 2) (Inactive) Via R2D2
        # ----------------------------------------------------
        initial_restarts_method = self.config.initial_restarts_method('directory')

        if initial_restarts_method == 'directory':
            self.initial_restarts_from_directory(geos_expdir_path)
        elif initial_restarts_method == 'r2d2':
            self.initial_restarts_from_r2d2()
        else:
            self.logger.abort(f'Unknown method for initial restarts: {initial_restarts_method}')

    # ----------------------------------------------------------------------------------------------

    def initial_restarts_from_directory(self, geos_expdir_path: str) -> None:

        # GEOS forecast checkpoint files are created in advance
        # -------------------------------------------------------------------
        self.logger.info('GEOS restarts are copied from an existing GEOS experiment directory')

        src = os.path.join(geos_expdir_path, '*_rst')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            copy_to_dst_dir(self.logger, filepath, self.forecast_dir(filename))

        # Create a dictionary of src/dst for the single files
        # Special handling of CICE6 and MOM6 outputs
        # ---------------------------------------------------
        src_dst = {'RESTART/iced.nc': '',
                   }

        # Create a dictionary for optional src/dst for the single files, and combine them with the
        # src_dst dictionary if they exist
        src_dst_optional = {'RESTART/mom6_increment.nc': ''
                            }

        for src, dst in src_dst_optional.items():
            if os.path.isfile(os.path.join(geos_expdir_path, src)):
                self.logger.info(' Found optional file: ' + src)
                src_dst.update({src: dst})

        for src, dst in src_dst.items():
            dst = os.path.join(dst, src)
            copy_to_dst_dir(self.logger, os.path.join(geos_expdir_path, src),
                            self.forecast_dir(dst))

        # Consider the case of multiple MOM restarts
        # -------------------------------------------
        src = os.path.join(geos_expdir_path, 'RESTART', 'MOM.res*nc')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            copy_to_dst_dir(self.logger, filepath, self.forecast_dir(['RESTART', filename]))

    # ----------------------------------------------------------------------------------------------

    def initial_restarts_from_r2d2(self) -> None:

        # GEOS restarts can be obtained from R2D2
        # --------------------------------------
        self.logger.info('Obtaining GEOS restarts from R2D2')
        self.logger.abort('R2D2 retrieval not implemented yet')

# --------------------------------------------------------------------------------------------------
