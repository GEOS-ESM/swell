# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob

from datetime import datetime as dt

from swell.tasks.base.geos_tasks_run_executable_base import *

# --------------------------------------------------------------------------------------------------


class PrepGeosRunDir(GeosTasksRunExecutableBase):

    # ----------------------------------------------------------------------------------------------

    def generate_extdata(self):

        # Generate ExtData.rc according to emissions and EXTDATA2G options
        # This is likely change with *.yaml vs *.rc considerations
        # ----------------------------------------------------------------

        if not self.cap_dict['EXTDATA2G_TRUE']:
            # Switch to MODIS v6.1 data after Nov 2021
            # ----------------------------------------
            d1 = dt.strptime('01112021', '%d%m%Y')

            if self.emissions == 'OPS_EMISSIONS' and self.cc_dto < d1:
                #TODO: Only relevant if EXTDATA2G is false
                self.logger.abort('This setting is not developed yet.')
            
            else:
                rc_paths = os.path.join(self.cycle_dir,'*_ExtData.rc')
                with open(os.path.join(self.cycle_dir,'ExtData.rc'), 'w') as extdata:
                    for filepath in list(glob.glob(rc_paths)):
                        with open(filepath, 'r') as file:
                            extdata.write(file.read())

        if self.cap_dict['EXTDATA2G_TRUE']:
            self.exec_python(self.geosbin, 'construct_extdata_yaml_list.py', 
                            './GEOS_ChemGridComp.rc', True)
            open(os.path.join(self.cycle_dir,'ExtData.rc'), 'w').close()

    # ----------------------------------------------------------------------------------------------

    def get_amip_emission(self):

        # Taken from gcm_run.j:

        # Before 2000-03-01, we need to use AMIP.20C which has different
        # emissions (HFED instead of QFED) valid before 2000-03-01. Note
        # that if you make a change to anything in /RC/AMIP or /RC/AMIP.20C, 
        # you might need to make a change in the other directory to be 
        # consistent. Some files in AMIP.20C are symlinks to that in AMIP but 
        # others are not.

        # AMIP EMISSIONS Transition window and no of vertical layers
        # ----------------------------------------------------------
        d1 = dt.strptime('01032000', '%d%m%Y')
        AGCM_LM = self.config_get('AGCM_LM')

        if not self.cap_dict['EXTDATA2G_TRUE']:
            src_dir = os.path.join(self.cycle_dir, 'AMIP','*')
            if self.cc_dto < d1:
                src_dir = os.path.join(self.cycle_dir, 'AMIP.20C','*')

            for filepath in list(glob.glob(src_dir)):
                filename = os.path.basename(filepath)
                self.fetch_to_cycle(filepath)

                # Replace source according to number of atm. vertical layers
                # ----------------------------------------------------------
                if(AGCM_LM != '72'):
                    self.logger.info(f"No. atm. vertical layers mismatch: {AGCM_LM} vs. 72")
                    self.logger.info(' Modifying AMIP file ' + filename)
                    self.replace_str(os.path.join(self.cycle_dir, filename), 'L72', 'L' + str(AGCM_LM))
                    self.replace_str(os.path.join(self.cycle_dir, filename), 'z72', 'z' + str(AGCM_LM))

    # ----------------------------------------------------------------------------------------------

    #TODO: this dict could be kept outside of this code
    # -------------------------------------------------
    def get_bcs(self):

        geos_bcsdir = self.config_get('geos_bcsdir')
        geos_chmdir = self.config_get('geos_chmdir')
        geos_bcrslv = self.config_get('geos_bcrslv')
        geos_abcsdir = self.config_get('geos_abcsdir')
        geos_obcsdir = os.path.join(self.config_get('geos_obcsdir'), self.ocn_horizontal_resolution)

        AGCM_IM = self.config_get('AGCM_IM')
        AGCM_JM = self.config_get('AGCM_JM')

        pchem_clim_years = self.config_get('pchem_clim_years')

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

        if pchem_clim_years == '39' and (self.cc_dto > d2 or self.cc_dto < d1):
            self.logger.abort('MERRA2OX data non existent for the current cycle')

        self.bcs_dict = {
        os.path.join(geos_abcsdir,'CF0012x6C_TM0072xTM0036-Pfafstetter.til'): 
                    'tile.data',
        os.path.join(geos_abcsdir,'CF0012x6C_TM0072xTM0036-Pfafstetter.TRN'): 
                    'runoff.bin',
        os.path.join(geos_obcsdir,f"SEAWIFS_KPAR_mon_clim.{self.ocn_horizontal_resolution}"): 
                    'SEAWIFS_KPAR_mon_clim.data',
        os.path.join(geos_obcsdir, 'MAPL_Tripolar.nc'): '',
        os.path.join(geos_obcsdir, f"vgrid{self.ocn_vertical_resolution}.ascii"): 'vgrid.ascii',
        os.path.join(geos_bcsdir, 'Shared', pchem[pchem_clim_years]): 
                    'species.data',
        os.path.join(geos_bcsdir, 'Shared', '*bin'): '',
        os.path.join(geos_chmdir, '*'): os.path.join(self.cycle_dir, 'ExtData'),
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
        os.path.join(geos_obcsdir, 'cice', 'kmt_cice.bin'): '',
        os.path.join(geos_obcsdir, 'cice', 'grid_cice.bin'): '',
        }

        #Conditional BCs that don't break the model
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
        self.fetch_to_cycle(os.path.join(geos_obcsdir, 'INPUT'), 
                            os.path.join(self.cycle_dir,'INPUT'))

    # ----------------------------------------------------------------------------------------------

    def get_dynamic(self):

        for src, dst in self.bcs_dict.items():
            if "*" in src:

                # Copy src files to cycle directory
                # ---------------------------------
                self.logger.info(' Linking file(s) from: ' + src)
                for filepath in list(glob.glob(src)):
                    filename = os.path.basename(filepath)
                    if len(dst) > 0:
                        os.makedirs(dst, 0o755, exist_ok=True)
                        try:
                            os.system('ln -sf ' + filepath + ' ' + dst + '/' + filename)
                        except Exception:
                            self.logger.abort('Linking failed, see if source files exists')
                        continue

                    try:
                        os.system('ln -sf ' + filepath + ' ' + self.cycle_dir + '/' + filename)
                    except Exception:
                        self.logger.abort('Linking failed, see if source files exists')
            else:
                self.logger.info(' Linking file: ' + src)
                try:
                    os.system('ln -sf ' + src + ' ' + self.cycle_dir + '/' + dst)
                except Exception:
                    self.logger.abort('Linking failed, see if source file exists')

    # ----------------------------------------------------------------------------------------------

    def get_static(self):

        # Folder name contains both horizontal and vertical resolutions
        # ----------------------------
        resolution = self.ocn_horizontal_resolution + 'x' + self.ocn_vertical_resolution

        geos_install_path = os.path.join(self.experiment_dir, 'GEOSgcm/source/install/bin')

        src_dirs = []

        # Create list of common source dirs
        # ---------------------------------
        src_dirs.append(os.path.join(self.swell_static_files, 'geos', 'static', 
                            resolution))
        src_dirs.append(os.path.join(self.swell_static_files, 'geos', 'static', 
                            resolution, 'RC'))
        src_dirs.append(os.path.join(geos_install_path,'bundleParser.py'))

        for src_dir in src_dirs:
            self.fetch_to_cycle(src_dir)

    # ----------------------------------------------------------------------------------------------

    def link_replay(self):

        # Linking REPLAY files according to AGCM.rc
        # -----------------------------------------
        pass
        # print('placeholder')

    # ----------------------------------------------------------------------------------------------

    def restructure_rc(self):

        # Modifying file templates
        # -------------------------

        if not self.cap_dict['EXTDATA2G_TRUE']:
            self.replace_str(os.path.join(self.cycle_dir, 'WSUB_ExtData.rc'), 
            'ExtData/g5gcm/moist/L72/Wvar_positive_05hrdeg_2006%m2.nc4', 
            '/dev/null'
            )
        else:
            self.replace_str(os.path.join(self.cycle_dir, 'WSUB_ExtData.yaml'), 
            'WSUB_Wvar_positive_05hrdeg_2006%m2.nc4', 
            '/dev/null'
            )

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """Obtains necessary directories and files from the static directories 
        (most are defined in gcm_run.j script):

            - get_bcs:
            Defines boundary conditions for different components of the coupled
            system and creates a bc dictionary.

            - get_dynamic:
            Links dynamic boundary conditions defined by the get_bcs method

            - get_static:
            Copies source files required for GEOS forecast to time dependent 
            cycle_dir.

        Parameters
        ----------
            All inputs are extracted from the suite configurations.
        """

        self.ocn_horizontal_resolution = self.config_get('ocn_horizontal_resolution')
        self.ocn_vertical_resolution = self.config_get('ocn_vertical_resolution')
        self.swell_static_files = self.config_get('swell_static_files')
        self.cycle_dir = self.config_get('cycle_dir')
        self.experiment_dir = self.config_get('experiment_dir')
        self.geos_source = self.config_get('existing_geos_source_directory')

        self.logger.info('Preparing GEOS Forecast directory')

        # Current cycle time object, useful for temporal BC constraints
        # -------------------------------------------------------------
        self.current_cycle = self.config_get('current_cycle')
        self.cc_dto = dt.strptime(self.current_cycle, "%Y%m%dT%H%M%SZ")

        # Get static files
        # ----------------
        self.get_static()

        # Parse .rc files
        # ----------------
        self.cap_dict = self.parse_rc(os.path.join(self.cycle_dir,'CAP.rc'))
        self.rc_assign(self.cap_dict, 'EXTDATA2G_TRUE') 

        # Select proper AMIP GOCART Emission RC Files as done in gcm_run.j
        # ----------------------------------------------------------------
        self.emissions = self.config_get('emissions')

        # If AMIP_EMISSIONS, arrange proper sources (i.e., AMIP vs AMIP.20c)
        # ------------------------------------------------------------------
        if self.emissions == 'AMIP_EMISSIONS':
            self.get_amip_emission()

        # Rename GEOS Chem files
        # ----------------------
        chem_dict = self.parse_rc(os.path.join(self.cycle_dir,'GEOS_ChemGridComp.rc'))
        self.geos_chem_rename(chem_dict)

        # Rename settings according to .rc switches
        # -----------------------------------------
        self.restructure_rc()

        # Generate the complete ExtData.rc
        # --------------------------------
        self.geosbin = os.path.join(self.geos_source, 'install', 'bin') 
        self.generate_extdata()

        # Get boundary conditions
        # ----------------
        self.get_bcs()

        # Get dynamic files
        # ----------------
        self.get_dynamic()

        # Create cap_restart
        # ------------------
        with open(os.path.join(self.cycle_dir,'cap_restart'), 'w') as file:
            file.write(dt.strftime(self.cc_dto, "%Y%m%d %H%M%S"))

        # Link replay files TODO
        # -----------------
        # agcm_dict = self.parse_rc(os.path.join(self.cycle_dir,'AGCM.rc'))
        # self.link_replay()

        self.exec_python(script_src = self.geosbin, script = 'bundleParser.py', 
                        dev = True)

# --------------------------------------------------------------------------------------------------
