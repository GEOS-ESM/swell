# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil, os, glob

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class PrepGeosRunDir(taskBase):

    #TODO: this dict could be kept out of this code
    # ---------------------------------------------
    def get_bcs(self):

        geos_bcsdir = self.config_get('geos_bcsdir')
        geos_chmdir = self.config_get('geos_chmdir')
        geos_bcrslv = self.config_get('geos_bcrslv')
        geos_abcsdir = self.config_get('geos_abcsdir')
        geos_obcsdir = self.config_get('geos_obcsdir')

        self.bcs_dict = {
        os.path.join(geos_bcsdir,'Shared','pchem.species.Clim_Prod_Loss.z_721x72.nc4'): 
                    'species.data',
        os.path.join(geos_bcsdir,'Shared','*bin'): '',
        # os.path.join(geos_chmdir,'*'): os.path.join(self.cycle_dir,'ExtData'),
        os.path.join(geos_bcsdir,'Shared','*c2l*.nc4'): '',
        }

    def get_dynamic(self):

        for src, dst in self.bcs_dict.items():
            if "*" in src:

                # Copy src files to cycle directory
                # ---------------------------------
                self.logger.info(' Linking file(s) from: '+src)
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
                self.logger.info(' Linking file: '+src)
                try:
                    os.system('ln -sf ' + src + ' ' + self.cycle_dir + '/' + dst)
                except Exception:
                    self.logger.abort('Linking failed, see if source file exists')


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

    def fetch_to_cycle(self, src_dir, dst_dir=None):

        # Destination is always (time dependent) cycle_dir
        # --------------------------------------------------
        dst_dir = self.cycle_dir

        try:
            if not os.path.isfile(src_dir):
                self.logger.info(' Fetching files from: '+src_dir)
                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            else:
                self.logger.info(' Fetching file: '+src_dir)
                shutil.copy(src_dir, dst_dir)

        except Exception:
            self.logger.abort('Copying failed, see if source files exists')

    def execute(self):

        """Obtains necessary directories from the Static Swell directory (as 
        defined by 'swell_static_files'):

            - fetch_to_cycle:
            Copies source files required for GEOS forecast to time dependent 
            cycle_dir.

            - fetch_to_cycle:
            Copies source files required for GEOS forecast to time dependent 
            cycle_dir.

            - TODO: source files to -> {src_dir}

        Parameters
        ----------
            All inputs are extracted from the suite configurations.
        """

        self.ocn_horizontal_resolution = self.config_get('ocn_horizontal_resolution')
        self.ocn_vertical_resolution = self.config_get('ocn_vertical_resolution')
        self.swell_static_files = self.config_get('swell_static_files')
        self.cycle_dir = self.config_get('cycle_dir')
        npx_proc = self.config_get('npx_proc')  # Used in eval(total_processors)
        npy_proc = self.config_get('npy_proc')  # Used in eval(total_processors)
        total_processors = self.config_get('total_processors')
        self.experiment_dir = self.config_get('experiment_dir')

        self.logger.info('Preparing GEOS Forecast directory')


        # Compute number of processors
        # ----------------------------
        total_processors = total_processors.replace('npx_proc', str(npx_proc))
        total_processors = total_processors.replace('npy_proc', str(npy_proc))
        np = eval(total_processors)

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
