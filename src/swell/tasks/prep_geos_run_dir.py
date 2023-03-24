# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil
import os
import glob

from datetime import datetime as dt

from swell.tasks.base.geos_tasks_run_executable_base import GeosTasksRunExecutableBase


# --------------------------------------------------------------------------------------------------


class PrepGeosRunDir(GeosTasksRunExecutableBase):

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

        # Current cycle time object, useful for temporal BC constraints
        # -------------------------------------------------------------
        current_cycle = self.config_get('current_cycle')
        cc_dto = dt.strptime(current_cycle, "%Y%m%dT%H%M%SZ")

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

        if pchem_clim_years == '39' and (cc_dto > d2 or cc_dto < d1):
            self.logger.abort('MERRA2OX data non existent for the current cycle')

        self.bcs_dict = {
        # os.path.join(geos_abcsdir,'CF0012x6C_TM0072xTM0036-Pfafstetter.til'): 
        #             'tile.data',
        # os.path.join(geos_abcsdir,'CF0012x6C_TM0072xTM0036-Pfafstetter.TRN'): 
        #             'runoff.bin',
        # os.path.join(geos_obcsdir,f"SEAWIFS_KPAR_mon_clim.{self.ocn_horizontal_resolution}"): 
        #             'SEAWIFS_KPAR_mon_clim.data',
        # os.path.join(geos_obcsdir, 'MAPL_Tripolar.nc'): '',
        # os.path.join(geos_obcsdir, f"vgrid{self.ocn_vertical_resolution}.ascii"): 'vgrid.ascii',
        # os.path.join(geos_bcsdir, 'Shared', pchem[pchem_clim_years]): 
        #             'species.data',
        # os.path.join(geos_bcsdir, 'Shared', '*bin'): '',
        # os.path.join(geos_chmdir, '*'): os.path.join(self.cycle_dir, 'ExtData'),
        # os.path.join(geos_bcsdir, 'Shared', '*c2l*.nc4'): '',
        # os.path.join(geos_abcsdir, f"visdf_{AGCM_IM}x{AGCM_JM}.dat"): 'visdf.dat',
        # os.path.join(geos_abcsdir, f"nirdf_{AGCM_IM}x{AGCM_JM}.dat"): 'nirdf.dat',
        # os.path.join(geos_abcsdir, f"vegdyn_{AGCM_IM}x{AGCM_JM}.dat"): 'vegdyn.data',
        # os.path.join(geos_abcsdir, f"lai_clim_{AGCM_IM}x{AGCM_JM}.data"): 'lai.data',
        # os.path.join(geos_abcsdir, f"green_clim_{AGCM_IM}x{AGCM_JM}.data"): 'green.data',
        # os.path.join(geos_abcsdir, f"ndvi_clim_{AGCM_IM}x{AGCM_JM}.data"): 'ndvi.data',
        os.path.join(geos_abcsdir, f"topo_DYN_ave_{AGCM_IM}x{AGCM_JM}.data"): 
                    'topo_dynave.data',
        os.path.join(geos_abcsdir, f"topo_GWD_var_{AGCM_IM}x{AGCM_JM}.data"): 
                    'topo_gwdvar.data',
        os.path.join(geos_abcsdir, f"topo_TRB_var_{AGCM_IM}x{AGCM_JM}.data"): 
                    'topo_trbvar.data',
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

        agcm_dict = self.parse_rc(os.path.join(self.cycle_dir,'AGCM.rc'))
        cap_dict = self.parse_rc(os.path.join(self.cycle_dir,'CAP.rc'))
        print(cap_dict)
        exit()
                            
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
                            'common/RC'))
        src_dirs.append(os.path.join(geos_install_path,'bundleParser.py'))

        for src_dir in src_dirs:
            self.fetch_to_cycle(src_dir)

    # ----------------------------------------------------------------------------------------------

    def fetch_to_cycle(self, src_dir, dst_dir=None):

        # Destination is always (time dependent) cycle_dir if None
        # --------------------------------------------------------
        if dst_dir is None:
            dst_dir = self.cycle_dir

        try:
            if not os.path.isfile(src_dir):
                self.logger.info(' Copying files from: '+src_dir)
                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            else:
                self.logger.info(' Copying file: '+src_dir)
                shutil.copy(src_dir, dst_dir)

        except Exception:
            self.logger.abort('Copying failed, see if source files exists')

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

            - fetch_to_cycle:
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

        self.logger.info('Preparing GEOS Forecast directory')

        # Get static files
        # ----------------
        self.get_static()

        # Get boundary conditions
        # ----------------
        self.get_bcs()

        # Get dynamic files
        # ----------------
        self.get_dynamic()


# --------------------------------------------------------------------------------------------------
