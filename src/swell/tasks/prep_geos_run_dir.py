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
import isodate

from swell.tasks.base.task_base import taskBase

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
        self.geos_source = self.config.existing_geos_gcm_source_path()

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
        self.geosbin = os.path.join(self.geos_source, 'install-Release', 'bin')
        self.generate_extdata()

        # Get boundary conditions
        # -----------------------
        self.get_bcs()

        # Get dynamic files
        # -----------------
        self.get_dynamic()

        # Create cap_restart
        # ------------------
        with open(self.forecast_dir('cap_restart'), 'w') as file:
            file.write(dt.strftime(self.fc_dto, "%Y%m%d %H%M%S"))

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
            self.geos.copy_to_geosdir(filepath)

            # Replace source according to number of atm. vertical layers
            # ----------------------------------------------------------
            if AGCM_LM != '72':
                self.logger.info(f"Atm. vertical layers mismatch: {AGCM_LM} vs. 72")
                self.logger.info(' Modifying AMIP file ' + filename)
                self.geos.resub(self.forecast_dir(filename), 'L72', 'L' + str(AGCM_LM))
                self.geos.resub(self.forecast_dir(filename), 'z72', 'z' + str(AGCM_LM))

    # ----------------------------------------------------------------------------------------------

    def get_bcs(self):

        # Uses parsed .rc and .j files to set BCs
        # ---------------------------------------

        AGCM_IM = self.agcm_dict['AGCM_IM']
        AGCM_JM = self.agcm_dict['AGCM_JM']
        OGCM_IM = self.agcm_dict['OGCM.IM_WORLD']
        OGCM_JM = self.agcm_dict['OGCM.JM_WORLD']
        OGCM_LM = self.agcm_dict['OGCM.LM']

        geos_bcsdir = self.gcm_dict['BCSDIR']
        geos_chmdir = self.gcm_dict['CHMDIR']
        geos_bcrslv = self.gcm_dict['BCRSLV']
        geos_abcsdir = self.gcm_dict['ABCSDIR']
        # TODO: GWD directory is not explicitly stated in gcm_run template, which
        # requires an additional step to parse that information. It is hard coded
        # for now but looking at the template there are 4 potential options.
        # Might also be only relevant for cold start..
        # geos_gwdrsdir = os.path.join('/discover/nobackup/projects/gmao/osse2',
        #                              f"stage/BCS_FILES/GWD_RIDGE/gwd_internal_c{AGCM_IM}")

        # Obtain tag information from abcsdir
        # -----------------------------------
        [ATMOStag, OCEANtag, *_] = os.path.basename(geos_abcsdir).split('_')

        geos_obcsdir = self.gcm_dict['OBCSDIR'].format(OGCM_IM=OGCM_IM, OGCM_JM=OGCM_JM)
        geos_obcsdir = geos_obcsdir.replace('$', '')

        pchem_clim_years = self.agcm_dict['pchem_clim_years']

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
            os.path.join(geos_abcsdir, f"{ATMOStag}_{OCEANtag}-Pfafstetter.til"):
                'tile.data',
            os.path.join(geos_abcsdir, f"{ATMOStag}_{OCEANtag}-Pfafstetter.TRN"):
                'runoff.bin',
            os.path.join(geos_obcsdir, f"SEAWIFS_KPAR_mon_clim.{OGCM_IM}x{OGCM_JM}"):
                'SEAWIFS_KPAR_mon_clim.data',
            os.path.join(geos_obcsdir, 'MAPL_Tripolar.nc'): 'MAPL_Tripolar.nc',
            os.path.join(geos_obcsdir, f"vgrid{OGCM_LM}.ascii"): 'vgrid.ascii',
            os.path.join(geos_bcsdir, 'Shared', pchem[pchem_clim_years]):
                'species.data',
            os.path.join(geos_bcsdir, 'Shared', '*bin'): '',
            os.path.join(geos_chmdir, '*'): self.forecast_dir('ExtData'),
            os.path.join(geos_bcsdir, 'Shared', '*c2l*.nc4'): '',
            os.path.join(geos_abcsdir, f"visdf_{AGCM_IM}x{AGCM_JM}.dat"): 'visdf.dat',
            os.path.join(geos_abcsdir, f"nirdf_{AGCM_IM}x{AGCM_JM}.dat"): 'nirdf.dat',
            os.path.join(geos_abcsdir, f"vegdyn_{AGCM_IM}x{AGCM_JM}.dat"): 'vegdyn.data',
            os.path.join(geos_abcsdir, f"lai_clim_{AGCM_IM}x{AGCM_JM}.data"): 'lai.data',
            os.path.join(geos_abcsdir, f"green_clim_{AGCM_IM}x{AGCM_JM}.data"): 'green.data',
            os.path.join(geos_abcsdir, f"ndvi_clim_{AGCM_IM}x{AGCM_JM}.data"): 'ndvi.data',
            os.path.join(geos_abcsdir, f"topo_DYN_ave_{AGCM_IM}x{AGCM_JM}.data"):
                'topo_dynave.data',
            os.path.join(geos_abcsdir, f"topo_GWD_var_{AGCM_IM}x{AGCM_JM}.data"):
                'topo_gwdvar.data',
            os.path.join(geos_abcsdir, f"topo_TRB_var_{AGCM_IM}x{AGCM_JM}.data"):
                'topo_trbvar.data',
            os.path.join(geos_obcsdir, 'cice', 'kmt_cice.bin'): 'kmt_cice.bin',
            os.path.join(geos_obcsdir, 'cice', 'grid_cice.bin'): 'grid_cice.bin',
            # geos_gwdrsdir: 'gwd_internal_rst',
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
        self.geos.copy_to_geosdir(os.path.join(geos_obcsdir, 'INPUT'),
                                  self.forecast_dir('INPUT'))

        # TODO: Temporary fix for some input files in gcm_run.j
        # -----------------------------------------------------
        if self.agcm_dict['OGCM.IM_WORLD'] == '1440':
            self.logger.info(' OBTAINING EXTRA WOA13 files')

            rst_path = self.config.geos_restarts_directory()
            src = os.path.join(self.swell_static_files, 'geos', 'restarts', self.rst_path,
                               'woa13_ptemp_monthly.nc')
            self.geos.copy_to_geosdir(src, self.forecast_dir(['INPUT',
                                                              'woa13_ptemp_monthly.nc']))

            src = os.path.join(self.swell_static_files, 'geos', 'restarts', self.rst_path,
                               'woa13_s_monthly.nc')
            self.geos.copy_to_geosdir(src, self.forecast_dir(['INPUT',
                                                              'woa13_s_monthly.nc']))

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

        # TODO: install folder name changes (install vs. install-Releaee)
        geos_install_path = os.path.join(self.experiment_path(), 'GEOSgcm',
                                         'source', 'install-Release', 'bin')

        src_dirs = []

        # Create list of static files
        # ---------------------------------
        src_dirs.append(self.geos_exp_dir)
        src_dirs.append(os.path.join(self.geos_exp_dir, 'RC'))
        src_dirs.append(os.path.join(geos_install_path, 'bundleParser.py'))

        for src_dir in src_dirs:
            self.geos.copy_to_geosdir(src_dir)

    # ----------------------------------------------------------------------------------------------

    def link_replay(self):

        # Linking REPLAY files according to AGCM.rc as in gcm_run.j
        # TODO: This needs another go over after GEOS Krok update
        # ---------------------------------------------------------

        if self.agcm_dict['REPLAY_MODE'] == 'Exact' or self.agcm_dict['REPLAY_MODE'] == 'Regular':
            ANA_EXPID = self.agcm_dict['REPLAY_ANA_EXPID']
            ANA_LOCATION = self.agcm_dict['REPLAY_ANA_LOCATION']
            REPLAY_FILE = self.agcm_dict['REPLAY_FILE']

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

        # AGCM.rc might require some modifications depending on the restart intervals
        # ----------------------------------------------------------------------------
        self.logger.info('Modifying AGCM.rc RECORD_* entries')
        [time_string, days] = self.geos.iso_to_time_str(self.config.forecast_duration(), half=True)

        # Prepend day information only record frequency is longer than a day
        # ------------------------------------------------------------------
        # TODO: float precision or scientific
        if days + 0.0000001 >= 1:
            time_string = f'0000{int(days):02d} ' + time_string

        rcdict['RECORD_FREQUENCY'] = time_string
        rcdict['RECORD_REF_DATE'] = self.fc_dto.strftime("%Y%m%d")
        rcdict['RECORD_REF_TIME'] = self.fc_dto.strftime("%H%M%S")

        with open(rcfile, "w") as f:
            yaml.dump(rcdict, f, default_flow_style=False, sort_keys=False)

        return self.geos.rc_to_bool(rcdict)

    # ----------------------------------------------------------------------------------------------

    def rewrite_cap(self, rcdict, rcfile):

        # CAP.rc requires modifications before job submission
        # This method returns rcdict with the bool fix
        # ---------------------------------------------
        self.logger.info('Modifying CAP.rc')
        [time_string, days] = self.geos.iso_to_time_str(self.config.forecast_duration())

        # Prepend day information
        # -----------------------
        time_string = f'0000{int(days):02d} ' + time_string

        rcdict['NUM_SGMT'] = '1'
        rcdict['JOB_SGMT'] = time_string

        with open(rcfile, "w") as f:
            yaml.dump(rcdict, f, default_flow_style=False, sort_keys=False)

        return self.geos.rc_to_bool(rcdict)

# --------------------------------------------------------------------------------------------------
