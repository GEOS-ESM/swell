# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob
import yaml

from datetime import datetime as dt

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import copy_to_dst_dir

# --------------------------------------------------------------------------------------------------


class PrepGeosRunDir(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """
        Parses resource files in "geos_experiment_directory" to obtain required
        directories and files. Modifies file contents using python re package
        according to cycle_date and CAP.rc,AGCM.rc, and gcm_run.j switches.

        In GEOS speak, it creates the "scratch" directory.
        """

        self.swell_static_files = self.config.swell_static_files()
        # TODO: exp. directory location requires better handling
        self.geos_exp_dir = os.path.join(self.swell_static_files, 'geos', 'run_dirs',
                                         self.config.geos_experiment_directory())
        self.geos_build = self.config.existing_geos_gcm_build_path()

        self.logger.info('Preparing GEOS Forecast directory')
        self.logger.info('Some steps involve modifying input files and replacing')
        self.logger.info(' file contents (i.e., WSUB_ExtData.*). Users are ')
        self.logger.info('encouraged to validate file modifications.')

        # Forecast start time object, useful for temporal BC constraints
        # -------------------------------------------------------------
        self.fc_dto = self.geos.get_rst_time()

        # Get static files
        # ----------------
        self.get_static()

        # Augment MOM_oda_incupd (IAU) with MOM_input IF it exists and IF mom6_increment.nc
        # file is located inside the INPUT directory. This allows not having a mom6_iau
        # switch in the cycling suite file.
        # --------------------------------------------------------------------------
        if os.path.exists(self.forecast_dir('INPUT/mom6_increment.nc')):
            if os.path.exists(self.forecast_dir('MOM_oda_incupd')):

                self.logger.info('MOM6 Increment file found in INPUT directory')
                self.logger.info('Augmenting MOM_oda_incupd with MOM_input')

                mom_input = self.forecast_dir('MOM_input')
                mom_oda_incupd = self.forecast_dir('MOM_oda_incupd')

                with open(mom_input, 'r') as inp_f, open(mom_oda_incupd, 'r') as append_f:
                    mom_input_txt = inp_f.read()
                    mom_oda_txt = append_f.read()

                with open(mom_input, 'w') as out_f:
                    out_f.write(mom_input_txt + mom_oda_txt)
            else:
                self.logger.info('MOM6 Increment file found in INPUT directory')
                self.logger.abort('MOM_oda_incupd not found. Failed augmentation')

        # Combine input.nml and fvcore_layout
        # Modify input.nml if not cold start (default)
        # --------------------------------------------
        self.geos.process_nml()

        # Parse .rc files and convert bool.s to Python format
        # ---------------------------------------------------
        self.cap_dict = self.geos.parse_rc(self.forecast_dir('CAP.rc'))
        self.cap_dict = self.rewrite_cap(self.cap_dict, self.forecast_dir('CAP.rc'))

        self.agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))

        # This ensures a bool entry for USE_EXTDATA2G exists
        # --------------------------------------------------
        self.geos.rc_assign(self.cap_dict, 'USE_EXTDATA2G')

        # Link replay files if active TODO
        # --------------------------------
        if 'REPLAY_MODE' in self.agcm_dict:
            self.logger.info('Replay Mode is Active')
            self.link_replay()

        # Set AGCM.rc record ref_date to fcst start time
        # TODO: This needs rethinking for forecast_geos vs cycle cases
        # ------------------------------------------------------------
        if 'RECORD_FREQUENCY' in self.agcm_dict:
            self.rewrite_agcm(self.agcm_dict, self.forecast_dir('AGCM.rc'))

        # Parse gcm_run.j and get a dictionary based upon setenv
        # ------------------------------------------------------
        self.gcm_dict = self.geos.parse_gcmrun(self.forecast_dir('gcm_run.j'))

        # Beginning GEOSgcm v11.6.0, linkbcs is a separate file from gcm_run.j.
        # So parse linkbcs file using parse_gcmrun method and update gcm_dict
        # -----------------------------------------------------------------------
        self.gcm_dict.update(self.geos.parse_gcmrun(self.forecast_dir('linkbcs')))

        # Select proper AMIP GOCART Emission RC Files as done in gcm_run.j
        # If AMIP_EMISSIONS, arrange proper sources (i.e., AMIP vs AMIP.20c)
        # ------------------------------------------------------------------
        if self.gcm_dict['EMISSIONS'] == 'AMIP_EMISSIONS':
            self.get_amip_emission()

        # Rename GEOS Chem files
        # ----------------------
        chem_dict = self.geos.parse_rc(self.forecast_dir('GEOS_ChemGridComp.rc'))
        self.geos.chem_rename(chem_dict)

        # Rename settings according to .rc switches
        # -----------------------------------------
        self.restructure_rc()

        # Generate the complete ExtData.rc
        # TODO: Fix install folders, update task_questions
        # --------------------------------
        self.geosbin = os.path.join(self.geos_build, 'bin')
        self.generate_extdata()

        # Get boundary conditions
        # -----------------------
        self.get_bcs()

        # Get dynamic files
        # -----------------
        self.get_dynamic()

        # Create cap_restart in GEOSgcm preferred format
        # ----------------------------------------------
        with open(self.forecast_dir('cap_restart'), 'w') as file:
            file.write(self.fc_dto.strftime("%Y%m%d %H%M%S"))

        # Run bundleParser
        # ------------------
        self.geos.exec_python(self.geosbin, 'bundleParser.py')

    # ----------------------------------------------------------------------------------------------

    def generate_extdata(self):

        # Generate ExtData.rc according to emissions and EXTDATA2G options
        # 'w' option overwrites the contents or creates a new file
        # --------------------------------------------------------

        if not self.cap_dict['USE_EXTDATA2G']:
            self.logger.info('Generating ExtData.rc')
            rc_paths = self.forecast_dir('*_ExtData.rc')
            with open(self.forecast_dir('ExtData.rc'), 'w') as extdata:
                for filepath in list(glob.glob(rc_paths)):
                    with open(filepath, 'r') as file:
                        extdata.write(file.read())

            # Switch to MODIS v6.1 data after Nov 2021
            # ----------------------------------------
            d1 = dt.strptime('01112021', '%d%m%Y')

            if self.gcm_dict['EMISSIONS'] == 'OPS_EMISSIONS' and self.fc_dto > d1:

                # 'r' indicates raw string
                # ------------------------
                pattern = r'(qfed2.emis_.*).006.'
                replacement = r'\g<1>.061.'
                self.logger.info('Switching to MODIS v6.1 (OPS_EMISSIONS)')
                self.geos.resub(self.forecast_dir('ExtData.rc'), pattern, replacement)
        else:
            self.logger.info('Creating extdata.yaml')
            self.geos.exec_python(self.geosbin, 'construct_extdata_yaml_list.py',
                                  './GEOS_ChemGridComp.rc')
            open(self.forecast_dir('ExtData.rc'), 'w').close()

    # ----------------------------------------------------------------------------------------------

    def get_amip_emission(self):

        # Select proper AMIP GOCART Emission RC Files
        # -------------------------------------------

        # Taken from gcm_run.j:

        # Before 2000-03-01, we need to use AMIP.20C which has different
        # emissions (HFED instead of QFED) valid before 2000-03-01. Note
        # that if you make a change to anything in /RC/AMIP or /RC/AMIP.20C,
        # you might need to make a change in the other directory to be
        # consistent. Some files in AMIP.20C are symlinks to that in AMIP but
        # others are not.

        # AMIP EMISSIONS Transition window and number of vertical layers
        # --------------------------------------------------------------
        d1 = dt.strptime('01032000', '%d%m%Y')
        AGCM_LM = self.agcm_dict['AGCM_LM']

        src_dir = self.forecast_dir(['AMIP', '*'])

        if not self.cap_dict['USE_EXTDATA2G']:
            if self.fc_dto < d1:
                src_dir = self.forecast_dir(['AMIP.20C', '*'])

        for filepath in list(glob.glob(src_dir)):
            filename = os.path.basename(filepath)
            copy_to_dst_dir(self.logger, filepath, self.forecast_dir())

            # Replace source according to number of atm. vertical layers
            # ----------------------------------------------------------
            if AGCM_LM != '72':
                self.logger.info(f"Atm. vertical layers mismatch: {AGCM_LM} vs. 72")
                self.logger.info(' Modifying AMIP file ' + filename)
                self.geos.resub(self.forecast_dir(filename), 'L72', 'L' + str(AGCM_LM))
                self.geos.resub(self.forecast_dir(filename), 'z72', 'z' + str(AGCM_LM))

    # ----------------------------------------------------------------------------------------------

    def get_bcs(self):

        # This methods is highly dependent on the GEOSgcm version, currently
        # tested with GEOSgcm v11.6.0. It uses parsed .rc and .j files to define
        # folders for the boundary conditions.
        # ----------------------------------------------
        AGCM_IM = self.agcm_dict['AGCM_IM']
        AGCM_JM = self.agcm_dict['AGCM_JM']
        OGCM_IM = self.agcm_dict['OGCM.IM_WORLD']
        OGCM_JM = self.agcm_dict['OGCM.JM_WORLD']
        OGCM_LM = self.agcm_dict['OGCM.LM']

        geos_bcsdir = self.gcm_dict['BCSDIR']
        geos_chmdir = self.gcm_dict['CHMDIR']
        geos_bcrslv = self.gcm_dict['BCRSLV']
        geos_cpldir = self.gcm_dict['CPLDIR']

        # Define the Ocean boundary conditions directory
        # -----------------------------------
        geos_obcsdir = os.path.join(geos_cpldir, f'{OGCM_IM}x{OGCM_JM}')
        [ATMOStag, *_] = os.path.basename(geos_bcrslv).split('_')

        # Define the path to the geometry directory
        # -----------------------------------------
        geos_geomdir = os.path.join(geos_bcsdir, 'geometry', geos_bcrslv)

        # Define the path to the land directory
        # -------------------------------------
        geos_landdir = os.path.join(geos_bcsdir, 'land', geos_bcrslv)

        # Define the path to the TOPO directory
        # -------------------------------------
        geos_topodir = os.path.join(geos_bcsdir, 'TOPO', 'TOPO_' + ATMOStag, 'smoothed')

        pchem_clim_years = self.agcm_dict['pchem_clim_years']
        pchem_dir = 'Shared' if 'pchem_clim_years' == '3' else 'PCHEM'

        pchem = {
            '1': 'pchem.species.Clim_Prod_Loss.z_721x72.nc4',
            '228': 'pchem.species.CMIP-5.1870-2097.z_91x72.nc4',
            '3': 'pchem.species.CMIP-6.wH2OandPL.1850s.z_91x72.nc4',
            '39': 'pchem.species.CMIP-5.MERRA2OX.197902-201706.z_91x72.nc4',
        }

        # MERRA2OX contains data only for a certain time window
        # -----------------------------------------------------
        d1 = dt.strptime('021979', '%m%Y')
        d2 = dt.strptime('062017', '%m%Y')

        if pchem_clim_years == '39' and (self.fc_dto > d2 or self.fc_dto < d1):
            self.logger.abort('MERRA2OX data non existent for the current' +
                              ' cycle. Change pchem_clim_years in AGCM.rc')

        self.bcs_dict = {
            os.path.join(geos_geomdir, f"{geos_bcrslv}-Pfafstetter.til"):
                'tile.data',
            os.path.join(geos_geomdir, f"{geos_bcrslv}-Pfafstetter.TRN"):
                'runoff.bin',
            os.path.join(geos_obcsdir, f"SEAWIFS_KPAR_mon_clim.{OGCM_IM}x{OGCM_JM}"):
                'SEAWIFS_KPAR_mon_clim.data',
            os.path.join(geos_geomdir, 'MAPL_Tripolar.nc'): 'MAPL_Tripolar.nc',
            os.path.join(geos_obcsdir, f"vgrid{OGCM_LM}.ascii"): 'vgrid.ascii',
            os.path.join(geos_bcsdir, pchem_dir, pchem[pchem_clim_years]):
                'species.data',
            # os.path.join(geos_bcsdir, 'Shared', '*bin'): '',
            os.path.join(geos_chmdir, '*'): self.forecast_dir('ExtData'),
            # os.path.join(geos_bcsdir, 'Shared', '*c2l*.nc4'): '',
            os.path.join(geos_landdir, f"visdf_{AGCM_IM}x{AGCM_JM}.dat"): 'visdf.dat',
            os.path.join(geos_landdir, f"nirdf_{AGCM_IM}x{AGCM_JM}.dat"): 'nirdf.dat',
            os.path.join(geos_landdir, f"vegdyn_{AGCM_IM}x{AGCM_JM}.dat"): 'vegdyn.data',
            os.path.join(geos_landdir, f"lai_clim_{AGCM_IM}x{AGCM_JM}.data"): 'lai.data',
            os.path.join(geos_landdir, f"green_clim_{AGCM_IM}x{AGCM_JM}.data"): 'green.data',
            os.path.join(geos_landdir, f"ndvi_clim_{AGCM_IM}x{AGCM_JM}.data"): 'ndvi.data',
            os.path.join(geos_topodir, f"topo_DYN_ave_{AGCM_IM}x{AGCM_JM}.data"):
                'topo_dynave.data',
            os.path.join(geos_topodir, f"topo_GWD_var_{AGCM_IM}x{AGCM_JM}.data"):
                'topo_gwdvar.data',
            os.path.join(geos_topodir, f"topo_TRB_var_{AGCM_IM}x{AGCM_JM}.data"):
                'topo_trbvar.data',
            os.path.join(geos_obcsdir, 'cice6', 'cice6_grid.nc'): '',
            os.path.join(geos_obcsdir, 'cice6', 'cice6_kmt.nc'): '',
            os.path.join(geos_obcsdir, 'cice6', 'cice6_global.bathy.nc'): '',
        }

        # Conditional BCs that don't break the model
        # ------------------------------------------
        conditional_bcs = {
            os.path.join(geos_bcsdir, geos_bcrslv, f"Gnomonic_{geos_bcrslv}.dat"): '',
        }

        for src, dst in conditional_bcs.items():
            if os.path.isfile(src):
                self.logger.info(' Including conditional file: ' + src)
                self.bcs_dict.update({
                    src: dst,
                    })

        # Fetch more resolution dependent files
        # -------------------------------------
        copy_to_dst_dir(self.logger, os.path.join(geos_obcsdir, 'INPUT'),
                        self.forecast_dir('INPUT'))

    # ----------------------------------------------------------------------------------------------

    def get_dynamic(self):

        # Creating symlinks to BCs dictionary
        # Unlinks existing ones first
        # ---------------------------------------

        for src, dst in self.bcs_dict.items():
            if "*" in src:

                # Copy src files to cycle directory
                # ---------------------------------
                self.logger.info(' Linking file(s) from: ' + src)
                for filepath in list(glob.glob(src)):
                    filename = os.path.basename(filepath)
                    if len(dst) > 0:
                        os.makedirs(dst, 0o755, exist_ok=True)
                        self.geos.linker(filepath, filename, dst_dir=dst)

                    self.geos.linker(filepath, filename)

            else:
                self.logger.info(' Linking file: ' + src)
                self.geos.linker(src, dst)

    # ----------------------------------------------------------------------------------------------

    def get_static(self):

        # Obtain experiment input files created by GEOS gcm_setup
        # --------------------------------------------------
        geos_install_path = os.path.join(self.experiment_path(), 'GEOSgcm', 'build', 'bin')

        src_dirs = []

        # Create list of static files
        # ---------------------------------
        src_dirs.append(self.geos_exp_dir)
        src_dirs.append(os.path.join(self.geos_exp_dir, 'RC'))
        src_dirs.append(os.path.join(geos_install_path, 'bundleParser.py'))

        for src_dir in src_dirs:
            copy_to_dst_dir(self.logger, src_dir, self.forecast_dir())

    # ----------------------------------------------------------------------------------------------

    def link_replay(self):

        # Linking REPLAY files according to AGCM.rc as in gcm_run.j
        # TODO: This needs another go over after GEOS Krok update
        # ---------------------------------------------------------

        if self.agcm_dict['REPLAY_MODE'] == 'Exact' or self.agcm_dict['REPLAY_MODE'] == 'Regular':
            # ANA_EXPID = self.agcm_dict['REPLAY_ANA_EXPID']
            ANA_LOCATION = self.agcm_dict['REPLAY_ANA_LOCATION']
            # REPLAY_FILE = self.agcm_dict['REPLAY_FILE']

        rply_dict = {
            os.path.join(ANA_LOCATION, 'aod'): '',
            os.path.join(ANA_LOCATION, 'ana'): '',
        }

        # if 'REPLAY_FILE09' in self.agcm_dict:
        #     REPLAY_FILE09 = self.agcm_dict['REPLAY_FILE09']
        #     self.logger.info(' Including REPLAY_FILE09: ' + src)
        #     self.rply_dict.update({
        #         os.path.join(ANA_LOCATION): '',
        #         })

        for src, dst in rply_dict.items():
            self.logger.info(' Linking file: ' + src)
            self.geos.linker(src, dst)

    # ----------------------------------------------------------------------------------------------

    def restructure_rc(self):

        # 1MOM and GFDL microphysics do not use WSUB_NATURE
        # -------------------------------------------------

        # Modifying file templates
        # -------------------------
        if not self.cap_dict['USE_EXTDATA2G']:
            self.logger.info('Modifying WSUB_ExtData.rc')

            # Only modify the line starts with WSUB_CLIM
            # --------------------------------------------
            pattern = r'^(WSUB_CLIM.*)ExtData.*'
            replacement = r'\g<1>/dev/null'
            self.geos.resub(self.forecast_dir('WSUB_ExtData.rc'), pattern, replacement)

        else:
            self.logger.info('Modifying WSUB_ExtData.yaml')

            with open(self.forecast_dir('WSUB_ExtData.yaml'), 'r') as f:
                wsub = yaml.safe_load(f)

            # Modifying one particular value
            # -----------------------------
            wsub['Exports']['WSUB_CLIM']['collection'] = '/dev/null'

            # Write the updated YAML back to the file
            with open(self.forecast_dir('WSUB_ExtData.yaml'), 'w') as f:
                yaml.dump(wsub, f, sort_keys=False)

    # ----------------------------------------------------------------------------------------------

    def rewrite_agcm(self, rcdict, rcfile):

        # This part is relevant for move_da_restart task. Be mindful of your changes
        # and what impacts they might have on others (also a good motto in life).

        # AGCM.rc might require some modifications depending on the restart intervals
        # ----------------------------------------------------------------------------
        self.logger.info('Modifying AGCM.rc RECORD_* entries')
        forecast_dur = self.config.forecast_duration()
        [time_string, days, half_duration] = self.geos.iso_to_time_str(forecast_dur, half=True)

        # We are assuming the beginning of the DA window is half of the forecast
        # duration. We don't need DA information in GEOS preparation tasks (for now).
        # --------------------------------------------------------------------------
        da_begin_dto = self.fc_dto + half_duration

        # Prepend day information only record frequency is longer than a day
        # ------------------------------------------------------------------
        # TODO: float precision or scientific
        if days + 0.0000001 >= 1:
            time_string = f'0000{int(days):02d} ' + time_string

        rcdict['RECORD_FREQUENCY'] = time_string
        rcdict['RECORD_REF_DATE'] = da_begin_dto.strftime("%Y%m%d")
        rcdict['RECORD_REF_TIME'] = da_begin_dto.strftime("%H%M%S")

        with open(rcfile, "w") as f:
            yaml.dump(rcdict, f, default_flow_style=False, sort_keys=False)

        return self.geos.rc_to_bool(rcdict)

    # ----------------------------------------------------------------------------------------------

    def rewrite_cap(self, rcdict, rcfile):

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

        with open(rcfile, "w") as f:
            yaml.dump(rcdict, f, default_flow_style=False, sort_keys=False)

        return self.geos.rc_to_bool(rcdict)

# --------------------------------------------------------------------------------------------------
