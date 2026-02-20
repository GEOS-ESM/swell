# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import isodate
import re

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import copy_to_dst_dir

# --------------------------------------------------------------------------------------------------


class PrepCoupledGeosRunDir(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Copies GEOS HOMDIR files to the cycle forecast directory to prepare before executing
        gcm_run.j.
        Modifies certain resource files using python's re package according to cycle_date such as:
        CAP.rc, AGCM.rc, input.nml, and gcm_run.j.

        As the name suggests, this task is geared towards coupled GEOSgcm simulations but
        the only difference between this and dataOcean ones should be in the get_static() method.

        xx) Changes HOMDIR and EXPDIR in gcm_run.j to point to the forecast directory
        xx) Provides consistency for GEOSgcm version by copying GEOSgcm.x from EXPDIR
        xx) (Optional) Checks GEOSDIR, GEOSBIN, GEOSETC, GEOSUTIL are consistent with
            experiment.yaml value if the override switch is on
        xx) Modifies CAP.rc according to cycle_date and forecast_duration
        """

        # These links were created in get_*_geos_restart task. This step will copy experiment
        # config.s to the cycle forecast directory
        self.geos_homdir = os.path.join(self.experiment_path(), 'GEOSgcm', 'GEOS_homdir')

        if self.config.geos_expdir_different():
            self.geos_expdir = os.path.join(self.experiment_path(), 'GEOSgcm', 'GEOS_expdir')
        else:
            self.geos_expdir = self.geos_homdir

        self.geos_build = self.config.existing_geos_gcm_build_path()

        self.logger.info('Preparing GEOS Forecast directory......')
        self.logger.info('Some steps involve modifying input files and replacing file contents.')
        self.logger.info('Users are encouraged to validate file modifications.')

        # Forecast start time can be calculated from cycle_date and forecast_duration
        # This task doesn't have access to DA window lengths since it could be used without the DA
        # context. So forecast start will be assigned as cycle_date - forecast_duration * 3/4
        # Need to convert forecast_duration to a datetime object first
        # -------------------------------------------------------------
        self.forecast_duration = self.config.forecast_duration()
        self.fc_dto = self.cycle_time_dto() - isodate.parse_duration(self.forecast_duration) * 3 / 4

        # Get static files
        # ----------------
        self.get_static()

        # IAU augment for MOM6
        # --------------------
        if 'geos_marine' == self.get_model():
            self.mom6_iau()

        # Modify input.nml if not cold start (default)
        # --------------------------------------------
        self.geos.process_nml()

        # Parse .rc files and convert bool.s to Python format
        # ---------------------------------------------------
        self.cap_dict = self.geos.parse_rc(self.forecast_dir('CAP.rc'))

        # Define the new directories you want to use
        with open(self.forecast_dir('gcm_run.j'), "r") as infile:
            lines = infile.readlines()

        with open(self.forecast_dir('gcm_run.j'), "w") as outfile:
            for line in lines:
                # Match setenv EXPDIR with any whitespace
                if re.match(r'^\s*setenv\s+EXPDIR\b', line):
                    outfile.write(f"setenv EXPDIR {self.forecast_dir()}\n")
                # Match setenv HOMDIR with any whitespace
                elif re.match(r'^\s*setenv\s+HOMDIR\b', line):
                    outfile.write(f"setenv HOMDIR {self.forecast_dir()}\n")
                else:
                    outfile.write(line)

        # with open(self.forecast_dir('gcm_run.j'), "r") as infile:
        #     lines = infile.readlines()

        # TODO: If, in the future, an override switch is introduced, additional logic can be
        # added here to update GEOSDIR, GEOSBIN, GEOSETC, and GEOSUTIL paths in gcm_run.j
        # so that a different GEOSgcm build can be used than the one that created the
        # experiment directory.
        # ------------------------------------------------------------------------------------------
        # with open(self.forecast_dir('gcm_run.j'), "w") as outfile:
        #     for line in lines:
        #         # Match setenv GEOSDIR, GEOSBIN, GEOSETC, GEOSUTIL and replace only the
        #         # first path segment
        #         match = re.match(r'^(\s*setenv\s+GEOS(DIR|BIN|ETC|UTIL)\s+)(\S+)', line)
        #         if match:
        #             var_prefix = match.group(1)
        #             full_path = match.group(3)
        #             # Split the path into main path and subpath (e.g., /bin, /etc)
        #             parts = full_path.split('/')
        #             # Find index of 'install' in the path and keep everything after it as subpath
        #             try:
        #                 idx = parts.index('install')
        #                 subpath = '/' + '/'.join(parts[idx+1:]) if idx+1 < len(parts) else ''
        #             except ValueError:
        #                 # If 'install' not found, replace the whole path
        #                 subpath = ''
        #             new_line = f"{var_prefix}{self.geos_build}{subpath}\n"
        #             outfile.write(new_line)
        #         else:
        #             outfile.write(line)

        # TODO: Still need to rewrite CAP.rc here for now to make sure END_TIME is long enough
        self.cap_dict = self.rewrite_cap(self.cap_dict, self.forecast_dir('CAP.rc'))

        self.agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))

        # Set AGCM.rc record ref_date to fcst start time
        # RECORD_FREQUENCY is used for dropping restart files at specific intervals
        # The values needs to be rewrittent according to the forecast and DA window lengths
        # TODO: This may need rethinking for forecast_coupled_geos vs cycle cases
        # ------------------------------------------------------------
        if 'RECORD_FREQUENCY' in self.agcm_dict:
            self.rewrite_agcm(self.agcm_dict, self.forecast_dir('AGCM.rc'))

        # Create cap_restart in GEOSgcm preferred format
        # ----------------------------------------------
        with open(self.forecast_dir('cap_restart'), 'w') as file:
            file.write(self.fc_dto.strftime("%Y%m%d %H%M%S"))

    # ----------------------------------------------------------------------------------------------

    def get_static(self) -> None:

        # Obtain experiment input files created by GEOS gcm_setup
        # Keep in mind that GEOSgcm uses .HOMDIR and .EXPDIR to define paths to the experiment
        # folders
        # --------------------------------------------------
        src_dirs = []

        # Make a list of required files to copy, so not everything in HOMDIR gets copied.
        # This part will eventually be handled with a modern gcm_setup script but for now these are
        # model specific
        req_files = ['AGCM.rc', 'CAP.rc', 'data_table', 'diag_table', 'fvcore_layout.rc',
                     'gcm_emip.setup', 'gcm_run.j', 'HISTORY.rc', '__init__.py', 'input.nml',
                     'logging.yaml', 'ice_in', 'MOM_input', 'MOM_override']

        # Optional files in the sense that these are optional MOM6 modules that might be used in
        # forecast or IAU mode that won't break the model if not present. This will also depend on
        # the input.nml configuration
        opt_files = ['MOM_oda_incupd', 'MOM_saltrestore']

        # Append required files to src_dirs with geos_homdir
        for file in req_files:
            src_dirs.append(os.path.join(self.geos_homdir, file))

        # Append optional files to src_dirs with geos_homdir only if they exist
        for file in opt_files:
            src_path = os.path.join(self.geos_homdir, file)
            if os.path.exists(src_path):
                self.logger.info(f'Adding optional file: {file}')
                src_dirs.append(src_path)

        # Finalize the list of source directories
        # TODO: Where do we want the GEOSgcm.x binary to come from?
        # ---------------------------------------
        src_dirs.append(os.path.join(self.geos_expdir, 'GEOSgcm.x'))
        src_dirs.append(os.path.join(self.geos_expdir, 'linkbcs'))

        for src_dir in src_dirs:
            copy_to_dst_dir(self.logger, src_dir, self.forecast_dir())

        # Copy RC directory as a whole
        # ---------------------------------------------------
        copy_to_dst_dir(self.logger, os.path.join(self.geos_expdir, 'RC'), self.forecast_dir('RC'))

    # ----------------------------------------------------------------------------------------------

    def mom6_iau(self) -> None:

        # Augment MOM_oda_incupd (IAU) with MOM_input IF mom6_iau is true and IF mom6_increment.nc
        # file is located inside the INPUT directory. At the first cycle, mom6_increment.nc may not
        # be present in the INPUT directory, so this step is skipped.
        # --------------------------------------------------------------------------
        if self.config.get_key_for_model('mom6_iau', 'geos_marine', False):
            if os.path.exists(self.forecast_dir('RESTART/mom6_increment.nc')):

                self.logger.info('MOM6 Increment file found in RESTART directory')
                self.logger.info('Augmenting MOM_oda_incupd with MOM_input')

                mom_input = self.forecast_dir('MOM_input')
                mom_oda_incupd = self.forecast_dir('MOM_oda_incupd')
                mom6_config = self.geos.parse_mom6_input(mom_oda_incupd)
                # P50D is just a random input for get_key_for_model to function
                mom6_iau_nhours = self.config.get_key_for_model('mom6_iau_nhours', 'geos_marine',
                                                                'PT50D')

                # convert ISO to 3.0
                duration = isodate.parse_duration(mom6_iau_nhours)
                hours = duration.total_seconds() / 3600
                mom6_config["ODA_INCUPD_NHOURS"] = hours

                # Write the updated configuration back to a file
                output_path = self.forecast_dir('MOM_oda_incupd')
                self.geos.write_mom6_input(mom6_config, output_path)

                with open(mom_input, 'r') as inp_f, open(mom_oda_incupd, 'r') as append_f:
                    mom_input_txt = inp_f.read()
                    mom_oda_txt = append_f.read()

                with open(mom_input, 'w') as out_f:
                    out_f.write(mom_input_txt + mom_oda_txt)
            else:
                self.logger.warning('MOM6 Increment file was not found in RESTART directory')

    # ----------------------------------------------------------------------------------------------

    def rewrite_agcm(self, rcdict: dict, rcfile: str) -> dict:

        # This part is relevant for move_da_restart task. Be mindful of your changes
        # and what impacts they might have on others (also a good motto in life).

        # AGCM.rc might require some modifications depending on the restart intervals
        # ----------------------------------------------------------------------------
        self.logger.info('Modifying AGCM.rc RECORD_* entries')
        [time_string, _, half_duration] = self.geos.iso_to_time_str(self.forecast_duration,
                                                                    half=True,
                                                                    agcm=True)

        # We are assuming the beginning of the DA window is half of the forecast
        # duration. We don't need DA information in GEOS preparation tasks (for now).
        # --------------------------------------------------------------------------
        da_begin_dto = self.fc_dto + half_duration

        rcdict['RECORD_FREQUENCY'] = time_string
        rcdict['RECORD_REF_DATE'] = da_begin_dto.strftime("%Y%m%d")
        rcdict['RECORD_REF_TIME'] = da_begin_dto.strftime("%H%M%S")

        self.geos.write_rc(rcdict, rcfile)
        return self.geos.rc_to_bool(rcdict)

    # ----------------------------------------------------------------------------------------------

    def rewrite_cap(self, rcdict: dict, rcfile: str) -> dict:

        # CAP.rc requires modifications before job submission
        # This method returns rcdict with the bool fix
        # ---------------------------------------------
        self.logger.info('Modifying CAP.rc')
        [time_string, days, _] = self.geos.iso_to_time_str(self.config.forecast_duration())

        # Prepend day information
        # -----------------------
        time_string = f'0000{int(days):04d} ' + time_string

        rcdict['NUM_SGMT'] = '1'
        rcdict['JOB_SGMT'] = time_string
        # END_DATE is set far into the future, we only want to run one segment for DA cycles
        rcdict['END_DATE'] = '50010101 000000'

        self.geos.write_rc(rcdict, rcfile)
        return self.geos.rc_to_bool(rcdict)

# --------------------------------------------------------------------------------------------------
