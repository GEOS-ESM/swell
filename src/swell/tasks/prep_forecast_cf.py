# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import math
import os
import shutil

import isodate
import xarray as xr

from swell.configuration.jedi.interfaces.geos_cf.model.r2d2 import forecast_history
from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
import swell.configuration.question_defaults as qd

from swell.utilities.shell_commands import run_subprocess

# --------------------------------------------------------------------------------------------------

task_name = 'PrepForecastCf'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.task_time_limit = True
        self.is_cycling = True
        self.model_dep = True
        self.questions = [
            qd.analysis_variables(),
            qd.forecast_length(),
            qd.forecast_output_frequency(),
            qd.geos_cf_install_dir(),
            qd.geos_cf_run_dir(),
            qd.geosfp_exp(),
            qd.geosfp_path(),
            qd.horizontal_resolution(),
            qd.iau(),
            qd.inc_template(),
            qd.window_length(),
            qd.rst_experiment()
        ]


# --------------------------------------------------------------------------------------------------

class PrepForecastCf(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Prepares scratch directory for running the model by creating the directory
        within the run directory and updating the .rc files.
        """

        # Create scratch directory under the current cycle run directory
        # ------------------------------------------------------------------------------------
        cycle_dir = self.cycle_dir()
        self.scratch_dir = os.path.join(cycle_dir, 'scratch')

        if os.path.isdir(self.scratch_dir):
            shutil.rmtree(self.scratch_dir)
            self.logger.info(f'Remove existing {self.scratch_dir}')

        os.makedirs(self.scratch_dir, mode=0o755)
        self.logger.info(f'Creating scratch directory: {self.scratch_dir}')

        # Gather config values
        # --------------------
        self.expid = self.experiment_id()
        self.window_length = self.config.window_length()
        self.forecast_length = self.config.forecast_length()
        self.forecast_output_frequency = self.config.forecast_output_frequency()
        self.resolution = self.config.horizontal_resolution()
        self.an_vars_long = self.config.analysis_variables()

        self.geos_cf_run_dir = self.config.geos_cf_run_dir()
        self.geos_cf_install_dir = self.config.geos_cf_install_dir()

        self.namelists_dir = os.path.join(self.experiment_config_path(),
                                          'jedi', 'interfaces', 'geos_cf', 'namelists')

        self.fp_exp = self.config.geosfp_exp()
        self.fp_loc = self.config.geosfp_path()

        # Derive window times
        # -------------------
        self.parse_andate = self.cycle_time_dto()
        self.parse_wbegin = self.da_window_params.window_begin(self.window_length, dto=True)
        self.parse_wend = self.da_window_params.window_end_iso(self.window_length, dto=True)
        self.parse_wlen = isodate.parse_duration(self.window_length)
        self.parse_fclen = isodate.parse_duration(self.forecast_length)

        # Determine analysis variables for GEOS-CF (NO2 and CO)
        # -------------------------------------------------------
        an_vars_long_tg = ['volume_mixing_ratio_of_no2',
                           'volume_mixing_ratio_of_co',
                           'volume_mixing_ratio_of_o3']
        self.an_vars_compo = []
        for an_var in an_vars_long_tg:
            if an_var in self.an_vars_long:
                self.an_vars_compo.append(an_var.split('_')[-1].upper())

        # Section 2: Create GEOS-CF increment files
        # ------------------------------------------
        self.logger.info('Creating GEOS-CF increment files')
        self.create_geos_cf_increments()

        # Section 3: Get GEOS FP analysis files for replay
        # -----------------------------------------------
        self.logger.info('Fetching GEOS FP analysis files for replay')
        self.get_geosfp_replay_files()

        # Section 4: Copy and update GEOS-CF namelist files
        # ---------------------------------------------------
        self.logger.info('Copying and updating GEOS-CF namelist/RC files')
        self.prepare_namelists()

    # ----------------------------------------------------------------------------------------------

    def replace_string(self, filename: str, string1: str, string2: str) -> None:
        """Replace string1 with string2 in-place in filename."""

        with open(filename, 'r') as f:
            content = f.read()
        with open(filename, 'w') as f:
            f.write(content.replace(string1, string2))

    # ----------------------------------------------------------------------------------------------

    def create_geos_cf_increments(self) -> None:
        """Convert JEDI increment files to GEOS-CF format using the increment template."""

        inc_template = self.config.inc_template()

        tstring_date = (self.parse_andate.strftime('%Y-%m-%d') + ' ' +
                        self.parse_andate.strftime('%H:%M:%S'))
        tstring = f'minutes since {tstring_date}'

        # jedi.inc.%y4%m2%d2.%h2z.nc
        output_date = (self.parse_andate.strftime('%Y%m%d') + '.' +
                       self.parse_andate.strftime('%H') + 'z')

        jedi_date = self.parse_andate.strftime('%Y%m%d_%H%M%Sz')
        jedifile = os.path.join(self.cycle_dir(), f'{self.expid}.inc.{jedi_date}.nc4')
        jedigeosfile = os.path.join(self.scratch_dir, f'jedi.inc.{output_date}.nc')

        if not os.path.exists(jedifile):
            self.logger.info(f'Increment file {jedifile} not found, skipping increment creation')
            return

        inc = xr.open_dataset(jedifile)
        template_ds = xr.open_dataset(inc_template)
        out = template_ds.copy()
        for var in self.an_vars_compo:
            if var in inc and var in out:
                out[var].values[:] = inc[var].values[:]
        out.to_netcdf(jedigeosfile)

        run_subprocess(self.logger, ['/bin/bash', '-c',
                                     f'ncatted -O -a units,time,o,c,"{tstring}" {jedigeosfile}'])

    # ----------------------------------------------------------------------------------------------

    def get_geosfp_replay_files(self) -> None:
        """Fetch GEOS FP analysis files needed for replay over the forecast length."""

        n_win_step = math.ceil(self.parse_fclen / self.parse_wlen)
        for wstep in range(n_win_step):
            fc_date = self.parse_andate + wstep * self.parse_wlen
            anYYYY = fc_date.strftime('%Y')
            anMM = fc_date.strftime('%m')
            anDD = fc_date.strftime('%d')
            anHH = fc_date.strftime('%H')
            date_path = f'Y{anYYYY}/M{anMM}'

            fp_path = f'{self.fp_loc}/{self.fp_exp}/ana/{date_path}'
            fp_file = (f'{self.fp_exp}.ana.eta.'
                       f'{anYYYY}{anMM}{anDD}_{anHH}00z.nc4')
            shutil.copy(f'{fp_path}/{fp_file}', self.scratch_dir)

    # ----------------------------------------------------------------------------------------------

    def prepare_namelists(self) -> None:
        """Copy GEOS-CF namelist/RC files into scratch_dir and update placeholders."""

        scratch_dir = self.scratch_dir
        namelists_dir = self.namelists_dir

        resolution = self.resolution
        fp_exp = self.fp_exp
        parse_wbegin = self.parse_wbegin
        parse_wend = self.parse_wend
        parse_fclen = self.parse_fclen

        # Copy all static files in RC/ in GEOS-CF run directory to scratch
        # ----------------------------------------------------------------
        src_rc = os.path.join(self.geos_cf_run_dir, 'RC')
        self.logger.info(f'Copy files from {src_rc} to {scratch_dir}')

        for item in os.listdir(src_rc):
            src = os.path.join(src_rc, item)
            dst = os.path.join(scratch_dir, item)

            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

        # Copy template namelist files
        # --------------------------
        for fname in ['logging.yaml', 'GEOSCHEMchem_ExtData.yaml',
                      'HEMCO_Config.rc', 'geoschem_config.yml']:

            src = os.path.join(namelists_dir, fname)
            self.logger.info(f'Copy {src} to {scratch_dir}')

            if os.path.exists(src):
                shutil.copy(src, scratch_dir)

        shutil.copy(os.path.join(namelists_dir, f'AGCM_{resolution}.rc'),
                    os.path.join(scratch_dir, 'AGCM.rc'))

        # Update AGCM.rc placeholders
        # ---------------------------
        agcm_rc = os.path.join(scratch_dir, 'AGCM.rc')
        self.replace_string(agcm_rc, '>>>SWELL_FP_EXP<<<', fp_exp)
        self.replace_string(agcm_rc, '>>>SWELL_SCRATCHDIR<<<', scratch_dir)

        weYYYY = parse_wend.strftime('%Y')
        weMM = parse_wend.strftime('%m')
        weDD = parse_wend.strftime('%d')
        weHH = parse_wend.strftime('%H')
        self.replace_string(agcm_rc, '>>>SWELL_FC6H_DATE<<<', f'{weYYYY}{weMM}{weDD}')
        self.replace_string(agcm_rc, '>>>SWELL_FC6H_H<<<', f'{weHH}0000')

        # Update HISTORY.rc placeholders
        # ------------------------------
        history_src = os.path.join(namelists_dir, 'HISTORY.rc')
        history_dst = os.path.join(scratch_dir, 'HISTORY.rc')
        shutil.copy(history_src, history_dst)
        history = forecast_history()
        self.replace_string(history_dst, '>>>SWELL_GEOSCF_FORECAST_EXPID<<<',
                            history['expid'])
        self.replace_string(history_dst, '>>>SWELL_GEOSCF_FORECAST_COLLECTION<<<',
                            history['collection'])
        self.replace_string(history_dst, '>>>SWELL_GEOSCF_FORECAST_TEMPLATE<<<',
                            history['template'])

        if resolution == 'c90':
            grid_label = 'PE90x540-CF'
        elif resolution == 'c360':
            grid_label = 'PE360x2160-CF'
        else:
            raise ValueError(
                f'Unsupported horizontal resolution for '
                f'HISTORY.rc grid label: {resolution}'
            )

        self.replace_string(history_dst, '>>>SWELL_GEOSCF_JEDI_GRID<<<', grid_label)

        freq_dur = isodate.parse_duration(self.forecast_output_frequency)
        freq_total_secs = int(freq_dur.total_seconds())
        freq_hh = freq_total_secs // 3600
        freq_mm = (freq_total_secs % 3600) // 60
        freq_ss = freq_total_secs % 60
        freq_geoscf = f'{freq_hh:02d}{freq_mm:02d}{freq_ss:02d}'
        self.replace_string(history_dst, '>>>SWELL_FC_OUTPUT_FREQ<<<', freq_geoscf)

        # Update GEOSCHEMchem_GridComp.rc placeholders
        # --------------------------------------------
        num_an_vars = len(self.an_vars_compo)
        gridcomp_src = os.path.join(namelists_dir, 'GEOSCHEMchem_GridComp.rc')
        gridcomp_dst = os.path.join(scratch_dir, 'GEOSCHEMchem_GridComp.rc')
        shutil.copy(gridcomp_src, gridcomp_dst)
        self.replace_string(gridcomp_dst, '>>>SWELL_NUM_AN_VARS<<<', str(num_an_vars))

        for index, an_var in enumerate(self.an_vars_compo):
            self.replace_string(gridcomp_dst,
                                f'#Analysis_Settings_Spec00{index + 1}:',
                                f'Analysis_Settings_Spec00{index + 1}: '
                                f'GEOSCHEMchem_AnaSettings_{an_var}.rc')

        # Update GEOSCHEMchem_AnaSettings_<var>.rc files placeholders
        # -----------------------------------------------------------
        for an_var in self.an_vars_compo:
            ana_src = os.path.join(namelists_dir, f'GEOSCHEMchem_AnaSettings_{an_var}.rc')
            ana_dst = os.path.join(scratch_dir, f'GEOSCHEMchem_AnaSettings_{an_var}.rc')
            if os.path.exists(ana_src):
                shutil.copy(ana_src, ana_dst)
                self.replace_string(ana_dst, '>>>SWELL_RUNDIR<<<', scratch_dir)

        # Write cap_restart with window begin date
        # -----------------------------------------
        cap_restart = os.path.join(scratch_dir, 'cap_restart')
        forecast_date = (parse_wbegin.strftime('%Y%m%d') + ' ' +
                         parse_wbegin.strftime('%H%M%S'))
        with open(cap_restart, 'w') as f:
            f.write(forecast_date)

        # Copy and configure gcm_run.j
        # -----------------------------
        gcm_run_src = os.path.join(namelists_dir, f'gcm_run_geoscf_{resolution}.j')
        gcm_run_dst = os.path.join(scratch_dir, 'gcm_run_geoscf.j')
        shutil.copy(gcm_run_src, gcm_run_dst)
        self.replace_string(gcm_run_dst, '>>>SWELL_CYCLEDIR<<<', scratch_dir)
        self.replace_string(gcm_run_dst, '>>>SWELL_GEOSINSTALL<<<', self.geos_cf_install_dir)

        # used in handling Saltwater Restart only
        self.replace_string(gcm_run_dst, '>>>SWELL_GEOSRUN<<<', self.geos_cf_run_dir)
        os.chmod(gcm_run_dst, 0o755)

        # Update CAP.rc with forecast length
        # ------------------------------------
        fc_days = str(parse_fclen.days).zfill(8)
        sub_day_secs = int(parse_fclen.total_seconds()) % 86400
        fc_hh = sub_day_secs // 3600
        fc_mm = (sub_day_secs % 3600) // 60
        fc_ss = sub_day_secs % 60
        fc_len_geoscf = f'{fc_days} {fc_hh:02d}{fc_mm:02d}{fc_ss:02d}'
        cap_src = os.path.join(namelists_dir, f'CAP_{resolution}.rc')
        cap_dst = os.path.join(scratch_dir, 'CAP.rc')
        shutil.copy(cap_src, cap_dst)
        self.replace_string(cap_dst, '>>>SWELL_FC_LENGTH<<<', fc_len_geoscf)

# --------------------------------------------------------------------------------------------------
