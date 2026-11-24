# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import glob
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import move_files
from swell.utilities.geos import Geos

# --------------------------------------------------------------------------------------------------


class MoveEnsembleForecastRestarts(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:
        """Moves restart files for all ensemble members to prepare for the next forecast cycle.

        Iterates over member indices 1..ensemble_num_members. For each member
        directory ``GEOSgcm/mem{NNN}/``, delegates to ``_move_member_restarts``
        to move ``_checkpoint`` files and marine model restarts out of ``scratch/``.
        """

        self.logger.info('Moving GEOS ensemble restarts for the next forecast cycle')

        self.num_members = self.config.ensemble_num_members()

        for member_id in range(1, self.num_members + 1):
            self.logger.info(f'Moving restarts for ensemble member {member_id:03d}')
            ens_dir = os.path.join(self.experiment_path(), 'GEOSgcm', f'mem{member_id:03d}')
            self._move_member_restarts(ens_dir)

    # ----------------------------------------------------------------------------------------------

    def _move_member_restarts(self, ens_dir: str) -> None:
        """Moves all restart files for a single ensemble member.

        Ensures the RESTART sub-directory exists, moves atmosphere and marine
        restarts, then calls ``Geos.rename_checkpoints`` for final renaming.

        Args:
            ens_dir: Absolute path to the ensemble member directory.
        """
        os.makedirs(os.path.join(ens_dir, 'RESTART'), 0o755, exist_ok=True)

        self._move_restarts(ens_dir)
        self._move_marine_restarts(ens_dir)

        geos_member = Geos(self.logger, ens_dir)
        geos_member.rename_checkpoints(ens_dir)

    # ----------------------------------------------------------------------------------------------

    def _move_restarts(self, ens_dir: str) -> None:
        """Moves atmosphere ``_checkpoint`` files from scratch to the member directory.

        Globs ``scratch/*_checkpoint`` and moves each file to the member root,
        stripping the extension to produce the restart filename (e.g.
        ``scratch/fvcore_internal_checkpoint`` → ``fvcore_internal_rst``
        after ``rename_checkpoints``).

        Args:
            ens_dir: Absolute path to the ensemble member directory.
        """
        self.logger.info(f'Moving _checkpoint restarts in {ens_dir}')

        src_pattern = os.path.join(ens_dir, 'scratch', '*_checkpoint')
        for filepath in list(glob.glob(src_pattern)):
            filename = os.path.basename(filepath).split('.')[0]
            move_files(self.logger, filepath, os.path.join(ens_dir, filename))

    # ----------------------------------------------------------------------------------------------

    def _move_marine_restarts(self, ens_dir: str) -> None:
        """Moves marine model restart files from scratch to their final locations.

        Moves ``scratch/tile.bin`` → ``tile.bin``,
        ``scratch/RESTART/iced.nc`` → ``RESTART/iced.nc``, and all
        ``scratch/RESTART/MOM.res*.nc`` → ``RESTART/``.

        Args:
            ens_dir: Absolute path to the ensemble member directory.
        """
        src_dst = {
            os.path.join('scratch', 'tile.bin'): '',
            os.path.join('scratch', 'RESTART', 'iced.nc'): 'RESTART',
        }

        for rel_src, rel_dst in src_dst.items():
            src = os.path.join(ens_dir, rel_src)
            dst = os.path.join(ens_dir, rel_dst, os.path.basename(rel_src))
            move_files(self.logger, src, dst)

        src_pattern = os.path.join(ens_dir, 'scratch', 'RESTART', 'MOM.res*nc')
        for filepath in list(glob.glob(src_pattern)):
            filename = os.path.basename(filepath)
            move_files(self.logger, filepath, os.path.join(ens_dir, 'RESTART', filename))

# --------------------------------------------------------------------------------------------------
