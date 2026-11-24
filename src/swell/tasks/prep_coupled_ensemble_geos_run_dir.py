# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import glob
import os
import isodate
import re
import shutil

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import copy_to_dst_dir
from swell.utilities.geos import Geos

# --------------------------------------------------------------------------------------------------


class PrepCoupledEnsembleGeosRunDir(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:
        """Prepares ensemble member forecast directories for a coupled GEOSgcm ensemble run.

        For each member 1..ensemble_num_members, creates
        ``<experiment_path>/GEOSgcm/mem{NNN}/`` with all required experiment files
        and applies per-member stochastic perturbation flags (SPPT, SKEB,
        STOCH_shutoff, MEMID in AGCM.rc). If ``MOM_stoch`` exists in geos_homdir,
        its content is prepended to each member's MOM_override.

        On the first cycle (no ``*_rst`` files in the member directory), restarts
        are copied from ``forecast/``, which was populated by GetCoupledGeosRestart.
        """

        self.geos_homdir = os.path.join(self.experiment_path(), 'GEOSgcm', 'GEOS_homdir')

        if self.config.geos_expdir_different():
            self.geos_expdir = os.path.join(self.experiment_path(), 'GEOSgcm', 'GEOS_expdir')
        else:
            self.geos_expdir = self.geos_homdir

        self.geos_build = self.config.existing_geos_gcm_build_path()

        self.forecast_duration = self.config.forecast_duration()
        self.fc_dto = self.cycle_time_dto() - isodate.parse_duration(self.forecast_duration) * 3 / 4

        self.num_members = self.config.ensemble_num_members()

        # deterministic forecast dir is the restart staging area for cycle 1
        self.det_forecast_dir = os.path.join(self.experiment_path(), 'GEOSgcm', 'forecast')

        self.logger.info(f'Preparing {self.num_members} ensemble member directories')

        for member_id in range(1, self.num_members + 1):
            self.logger.info(f'Processing ensemble member {member_id:03d}')
            self._prep_member(member_id)

    # ----------------------------------------------------------------------------------------------

    def _ens_dir(self, member_id: int, *paths) -> str:
        """Returns the absolute path to an ensemble member directory.

        Args:
            member_id: 1-based ensemble member index.
            *paths: Optional sub-path components appended via os.path.join.

        Returns:
            Absolute path to ``GEOSgcm/mem{NNN}/`` or a sub-path within it.
        """
        base = os.path.join(self.experiment_path(), 'GEOSgcm', f'mem{member_id:03d}')
        if paths:
            return os.path.join(base, *paths)
        return base

    # ----------------------------------------------------------------------------------------------

    def _prep_member(self, member_id: int) -> None:
        """Prepares the run directory for a single ensemble member.

        Creates the member directory and RESTART sub-directory, copies static
        experiment files, seeds initial restarts on the first cycle, rewrites
        gcm_run.j, CAP.rc, and AGCM.rc, appends stochastic flags, optionally
        prepends MOM_stoch, and writes cap_restart.

        Args:
            member_id: 1-based ensemble member index.
        """
        ens_dir = self._ens_dir(member_id)
        os.makedirs(ens_dir, 0o755, exist_ok=True)
        os.makedirs(os.path.join(ens_dir, 'RESTART'), 0o755, exist_ok=True)

        # Copy static experiment files from homdir/expdir
        self._get_static(ens_dir)

        # First cycle: no *_rst files present in mem dir — copy from deterministic forecast/
        rst_files = glob.glob(os.path.join(ens_dir, '*_rst'))
        if not rst_files:
            self.logger.info(f'No restarts found in mem{member_id:03d}/ — copying from forecast/')
            self._copy_initial_restarts(ens_dir)

        # IAU augment for MOM6
        if 'geos_marine' == self.get_model():
            geos_member = Geos(self.logger, ens_dir)
            self._mom6_iau(ens_dir, geos_member)

        geos_member = Geos(self.logger, ens_dir)

        # Modify input.nml
        geos_member.process_nml()

        # Rewrite gcm_run.j EXPDIR/HOMDIR to point to ens dir
        gcm_run = os.path.join(ens_dir, 'gcm_run.j')
        with open(gcm_run, 'r') as f:
            lines = f.readlines()
        with open(gcm_run, 'w') as f:
            for line in lines:
                if re.match(r'^\s*setenv\s+EXPDIR\b', line):
                    f.write(f'setenv EXPDIR {ens_dir}\n')
                elif re.match(r'^\s*setenv\s+HOMDIR\b', line):
                    f.write(f'setenv HOMDIR {ens_dir}\n')
                else:
                    f.write(line)

        # Rewrite CAP.rc
        cap_dict = geos_member.parse_rc(os.path.join(ens_dir, 'CAP.rc'))
        cap_dict = self._rewrite_cap(geos_member, cap_dict, os.path.join(ens_dir, 'CAP.rc'))

        # Rewrite AGCM.rc + add stochastic flags
        agcm_dict = geos_member.parse_rc(os.path.join(ens_dir, 'AGCM.rc'))
        if 'RECORD_FREQUENCY' in agcm_dict:
            agcm_dict = self._rewrite_agcm(geos_member, agcm_dict,
                                           os.path.join(ens_dir, 'AGCM.rc'))

        self._add_stochastic_flags(geos_member, agcm_dict, os.path.join(ens_dir, 'AGCM.rc'),
                                   member_id)

        # Prepend MOM_stoch to MOM_override if MOM_stoch exists in homdir
        mom_stoch_src = os.path.join(self.geos_homdir, 'MOM_stoch')
        if os.path.exists(mom_stoch_src):
            self.logger.info(f'Prepending MOM_stoch to mem{member_id:03d}/MOM_override')
            self._prepend_mom_stoch(mom_stoch_src, os.path.join(ens_dir, 'MOM_override'))

        # Write cap_restart
        with open(os.path.join(ens_dir, 'cap_restart'), 'w') as f:
            f.write(self.fc_dto.strftime('%Y%m%d %H%M%S'))

    # ----------------------------------------------------------------------------------------------

    def _get_static(self, ens_dir: str) -> None:
        """Copies required static experiment files from geos_homdir/geos_expdir into a member dir.

        Required files (AGCM.rc, CAP.rc, gcm_run.j, etc.) are always copied.
        Optional files (MOM_oda_incupd, MOM_saltrestore) are copied only if present.
        The RC/ sub-directory and linkbcs script are copied from geos_expdir.

        Args:
            ens_dir: Absolute path to the ensemble member directory.
        """
        req_files = ['AGCM.rc', 'CAP.rc', 'data_table', 'diag_table', 'fvcore_layout.rc',
                     'gcm_emip.setup', 'gcm_run.j', 'HISTORY.rc', '__init__.py', 'input.nml',
                     'logging.yaml', 'ice_in', 'MOM_input', 'MOM_override']

        opt_files = ['MOM_oda_incupd', 'MOM_saltrestore']

        src_paths = [os.path.join(self.geos_homdir, f) for f in req_files]

        for f in opt_files:
            src = os.path.join(self.geos_homdir, f)
            if os.path.exists(src):
                self.logger.info(f'Adding optional file: {f}')
                src_paths.append(src)

        # src_paths.append(os.path.join(self.geos_expdir, 'GEOSgcm.x'))
        src_paths.append(os.path.join(self.geos_expdir, 'linkbcs'))

        for src in src_paths:
            copy_to_dst_dir(self.logger, src, ens_dir)

        copy_to_dst_dir(self.logger, os.path.join(self.geos_expdir, 'RC'),
                        os.path.join(ens_dir, 'RC'))

    # ----------------------------------------------------------------------------------------------

    def _copy_initial_restarts(self, ens_dir: str) -> None:
        """Copies initial restart files from the deterministic forecast directory.

        Used only on the first cycle, when no ``*_rst`` files are present in the
        member directory. Copies all ``*_rst`` files and the contents of RESTART/
        from ``GEOSgcm/forecast/`` (populated by GetCoupledGeosRestart) into the
        member directory.

        Args:
            ens_dir: Absolute path to the ensemble member directory.
        """
        # Copy *_rst files from deterministic forecast/ to ens dir
        for rst in glob.glob(os.path.join(self.det_forecast_dir, '*_rst')):
            shutil.copy2(rst, ens_dir)

        # Copy RESTART/ contents
        src_restart = os.path.join(self.det_forecast_dir, 'RESTART')
        dst_restart = os.path.join(ens_dir, 'RESTART')
        if os.path.isdir(src_restart):
            for item in os.listdir(src_restart):
                shutil.copy2(os.path.join(src_restart, item), dst_restart)

    # ----------------------------------------------------------------------------------------------

    def _mom6_iau(self, ens_dir: str, geos_member: Geos) -> None:
        """Augments MOM_input with MOM6 IAU settings if an ocean increment is present.

        If ``mom6_iau`` is enabled in the geos_marine model config and a
        ``RESTART/mom6_increment.nc`` file exists in the member directory,
        updates ``ODA_INCUPD_NHOURS`` in MOM_oda_incupd and appends that file
        to MOM_input.

        Args:
            ens_dir: Absolute path to the ensemble member directory.
            geos_member: Geos utility instance initialised for this member.
        """
        if self.config.get_key_for_model('mom6_iau', 'geos_marine', False):
            increment_path = os.path.join(ens_dir, 'RESTART', 'mom6_increment.nc')
            if os.path.exists(increment_path):

                self.logger.info('MOM6 Increment found — augmenting MOM_oda_incupd with MOM_input')

                mom_input = os.path.join(ens_dir, 'MOM_input')
                mom_oda_incupd = os.path.join(ens_dir, 'MOM_oda_incupd')
                mom6_config = geos_member.parse_mom6_input(mom_oda_incupd)
                mom6_iau_nhours = self.config.get_key_for_model('mom6_iau_nhours', 'geos_marine',
                                                                'PT50D')
                duration = isodate.parse_duration(mom6_iau_nhours)
                hours = duration.total_seconds() / 3600
                mom6_config['ODA_INCUPD_NHOURS'] = hours
                geos_member.write_mom6_input(mom6_config, mom_oda_incupd)

                with open(mom_input, 'r') as inp_f, open(mom_oda_incupd, 'r') as append_f:
                    mom_input_txt = inp_f.read()
                    mom_oda_txt = append_f.read()

                with open(mom_input, 'w') as out_f:
                    out_f.write(mom_input_txt + mom_oda_txt)
            else:
                self.logger.warning('MOM6 Increment file not found in RESTART directory')

    # ----------------------------------------------------------------------------------------------

    def _rewrite_agcm(self, geos_member: Geos, rcdict: dict, rcfile: str) -> dict:
        """Rewrites RECORD_* timing entries in AGCM.rc for the current forecast cycle.

        Args:
            geos_member: Geos utility instance for the member directory.
            rcdict: Parsed key-value dict from AGCM.rc.
            rcfile: Absolute path to the AGCM.rc file to overwrite.

        Returns:
            Updated rcdict with boolean-coerced values (from ``Geos.rc_to_bool``).
        """
        self.logger.info(f'Modifying AGCM.rc RECORD_* entries: {rcfile}')
        [time_string, _, half_duration] = geos_member.iso_to_time_str(self.forecast_duration,
                                                                       half=True,
                                                                       agcm=True)
        da_begin_dto = self.fc_dto + half_duration

        rcdict['RECORD_FREQUENCY'] = time_string
        rcdict['RECORD_REF_DATE'] = da_begin_dto.strftime('%Y%m%d')
        rcdict['RECORD_REF_TIME'] = da_begin_dto.strftime('%H%M%S')

        geos_member.write_rc(rcdict, rcfile)
        return geos_member.rc_to_bool(rcdict)

    # ----------------------------------------------------------------------------------------------

    def _rewrite_cap(self, geos_member: Geos, rcdict: dict, rcfile: str) -> dict:
        """Rewrites CAP.rc segment/duration entries for the current forecast cycle.

        Sets NUM_SGMT, JOB_SGMT, and END_DATE based on forecast_duration.

        Args:
            geos_member: Geos utility instance for the member directory.
            rcdict: Parsed key-value dict from CAP.rc.
            rcfile: Absolute path to the CAP.rc file to overwrite.

        Returns:
            Updated rcdict with boolean-coerced values (from ``Geos.rc_to_bool``).
        """
        self.logger.info(f'Modifying CAP.rc: {rcfile}')
        [time_string, days, _] = geos_member.iso_to_time_str(self.forecast_duration)
        time_string = f'0000{int(days):04d} ' + time_string

        rcdict['NUM_SGMT'] = '1'
        rcdict['JOB_SGMT'] = time_string
        rcdict['END_DATE'] = '50010101 000000'

        geos_member.write_rc(rcdict, rcfile)
        return geos_member.rc_to_bool(rcdict)

    # ----------------------------------------------------------------------------------------------

    def _add_stochastic_flags(self, geos_member: Geos, rcdict: dict, rcfile: str,
                               member_id: int) -> None:
        """Appends stochastic perturbation flags to a member's AGCM.rc.

        Sets SPPT=1, SKEB=0, STOCH_shutoff=0, and MEMID=<member_id> in rcdict,
        then writes the updated dict back to rcfile.

        Args:
            geos_member: Geos utility instance for the member directory.
            rcdict: Parsed key-value dict from AGCM.rc (may already have RECORD_* entries).
            rcfile: Absolute path to the AGCM.rc file to overwrite.
            member_id: 1-based ensemble member index written as MEMID.
        """
        self.logger.info(f'Adding stochastic AGCM flags for member {member_id:03d}')
        rcdict['SPPT'] = '1'
        rcdict['SKEB'] = '0'
        rcdict['STOCH_shutoff'] = '0'
        rcdict['MEMID'] = str(member_id)

        geos_member.write_rc(rcdict, rcfile)

    # ----------------------------------------------------------------------------------------------

    def _prepend_mom_stoch(self, mom_stoch_src: str, mom_override_dst: str) -> None:
        """Prepends MOM_stoch content to a member's MOM_override file.

        Reads the stochastic ocean parameter file and writes it before the
        existing MOM_override content, separated by a blank line.

        Args:
            mom_stoch_src: Absolute path to the ``MOM_stoch`` source file in geos_homdir.
            mom_override_dst: Absolute path to the member's ``MOM_override`` file.
        """
        with open(mom_stoch_src, 'r') as f:
            stoch_content = f.read()

        with open(mom_override_dst, 'r') as f:
            override_content = f.read()

        with open(mom_override_dst, 'w') as f:
            f.write(stoch_content + '\n' + override_content)

# --------------------------------------------------------------------------------------------------
