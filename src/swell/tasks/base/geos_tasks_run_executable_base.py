# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime
import f90nml
import glob
import isodate
import netCDF4
import os
import re
import shutil

from abc import ABC, abstractmethod

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_subprocess, run_track_log_subprocess


# --------------------------------------------------------------------------------------------------


class GeosTasksRunExecutableBase(taskBase):

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self):

        # This class does not execute, it provides helper function for the children
        # ------------------------------------------------------------------------
        pass

    # ----------------------------------------------------------------------------------------------

    def adjacent_cycle(self, offset, return_date=False):

        # Basename consists of swell datetime and model
        # ---------------------------------------------
        # basename = os.path.basename(self.cycle_dir())
        dt_str = os.path.basename(os.path.dirname(self.cycle_dir()))
        # dt_str = basename.split('-')[0]
        dt_obj = datetime.strptime(dt_str, self.get_datetime_format())

        # Modify datetime by using date offset
        # ------------------------------------
        modified_dt_obj = dt_obj + isodate.parse_duration(offset)

        if return_date:
            return modified_dt_obj

        # Replace datetime section in the basename with the modified datetime string
        # -----------------------------------------------------------------
        modified_dt_str = modified_dt_obj.strftime(self.get_datetime_format())
        modified_basename = basename.replace(dt_str, modified_dt_str)

        # Create new file path with modified basename
        # --------------------------------------------
        adj_cycle_dir = os.path.join(os.path.dirname(self.cycle_dir()), modified_basename)

        return adj_cycle_dir

    # ----------------------------------------------------------------------------------------------

    def at_cycle_model(self, paths):

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        # Combining list of paths with cycle dir for script brevity
        # ---------------------------------------------------------
        full_path = os.path.join(self.cycle_dir(), *paths)
        return full_path

    # ----------------------------------------------------------------------------------------------

    def at_cycle_geosdir(self, paths=[]):

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        datetimedir = os.path.dirname(self.cycle_dir())

        # Combining list of paths with cycle dir for script brevity
        # ---------------------------------------------------------
        full_path = os.path.join(datetimedir, 'geosdir', *paths)
        return full_path

    # ----------------------------------------------------------------------------------------------

    def copy_to_geosdir(self, src_dir, dst_dir=None):

        # Destination is always (time dependent) cycle_dir if None
        # --------------------------------------------------------
        if dst_dir is None:
            dst_dir = self.at_cycle_geosdir()

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

    def exec_python(self, script_src, script, input=''):

        # Source g5_modules and execute py scripts in a new shell process then
        # return to the current one
        # Define the command to source the Bash script and run the Python command
        # -----------------------------------------------------------------------
        command = f'source {script_src}/g5_modules.sh \n' + \
            f'cd {self.at_cycle_geosdir()} \n' + \
            f'{script_src}/{script} {input}'

        # Containerized run of the GEOS build steps
        # -----------------------------------------
        run_subprocess(self.logger, ['/bin/bash', '-c', command])

    # ----------------------------------------------------------------------------------------------

    def geos_chem_rename(self, rcdict):

        # Some files are renamed according to bool. switches in GEOS_ChemGridComp.rc
        # -------------------------------------------------------------------------

        # Convert rc bool.s to python
        # ---------------------------
        rcdict = self.rc_to_bool(rcdict)

        # GEOS Chem filenames, shares same keys as rcdict
        # -----------------------------------------------
        chem_files = {
            'ENABLE_STRATCHEM': 'StratChem_ExtData.rc',
            'ENABLE_GMICHEM': 'GMI_ExtData.rc',
            'ENABLE_GEOSCHEM': 'GEOSCHEMchem_ExtData.rc',
            'ENABLE_CARMA': 'CARMAchem_GridComp_ExtData.rc',
            'ENABLE_DNA': 'DNA_ExtData.rc',
            'ENABLE_ACHEM': 'GEOSachem_ExtData.rc',
            'ENABLE_GOCART_DATA': 'GOCARTdata_ExtData.rc',
        }

        for key, value in chem_files.items():
            fname = self.at_cycle_geosdir(value)

            if not rcdict[key] and os.path.isfile(fname):
                self.logger.info(' Renaming file: '+fname)
                os.system('rename .rc .rc.NOT_USED ' + fname)

    # ----------------------------------------------------------------------------------------------

    def geos_linker(self, src, dst, dst_dir=None):

        # Link files from BC directories
        # ------------------------------

        if dst_dir is None:
            dst_dir = self.at_cycle_geosdir()

        dst = os.path.basename(dst)

        # Assign dst name if non-existent
        # ------------------------------
        if dst == '':
            dst = os.path.basename(src)

        # Assures existing links will be unlinked
        # -----------------------------------
        if os.path.lexists(os.path.join(dst_dir, dst)):
            self.logger.info(' Unlinking existing link: ')
            self.logger.info(os.path.join(dst_dir, dst))
            os.unlink(os.path.join(dst_dir, dst))

        try:
            os.symlink(src, os.path.join(dst_dir, dst))
        except Exception:
            self.logger.abort('Linking failed, see if source files exist')

    # ----------------------------------------------------------------------------------------------

    def get_rst_time(self):

        # Obtain time information from any of the rst files listed by glob
        # ----------------------------------------------------------------
        src = self.at_cycle_geosdir('*_rst')

        # Open any _rst file in cycle dir to read time and units
        # ------------------------------------------------------
        ncfile = netCDF4.Dataset(list(glob.glob(src))[0])
        self.logger.info(f"Getting time information from: ' {list(glob.glob(src))[0]}")

        time_var = ncfile.variables['time']
        units = time_var.units

        # Convert the time values to datetime objects
        # ---------------------------------------------
        times = netCDF4.num2date(time_var[:], units=units, calendar='standard')
        ncfile.close()

        return times[0]

    # ----------------------------------------------------------------------------------------------

    def iso_to_time_str(self, iso_duration, half=False):

        # Parse the ISO duration string and get the total number of seconds
        # It is written to handle fcst_duration less than a day for now
        # ----------------------------------------------------------------
        duration = isodate.parse_duration(iso_duration)
        duration_seconds = duration.total_seconds()

        # RESTART is produced at the half of the forecast cycle
        # -----------------------------------------------------
        if half:
            duration_seconds = duration_seconds / 2

        # Calculate days in case of long forecast time
        # --------------------------------------------
        days, remainder = divmod(duration_seconds, 60*60*24)

        # Convert the duration to a string in the format of "HHMMSS" to be used
        # with AGCM.rc and CAP.rc
        # ---------------------------------------------------------------------
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f'{int(hours):02d}{int(minutes):02d}{int(seconds):02d}'

        return time_string, days

    # ----------------------------------------------------------------------------------------------

    def parse_gcmrun(self, jfile):

        # Parse gcm_run.j line by line and snatch setenv variables. gcm_setup
        # creates gcm_run.j and handles platform dependencies.
        # ----------------------------------------------------------------------

        with open(jfile, 'r') as file:
            lines = file.readlines()

        rcdict = {}

        for line in lines:

            # Skip if the line is a comment (i.e., starts with #)
            # ------------------------------------------------------
            if line.startswith("#"):
                continue

            # Strip any leading or trailing whitespace from the line
            # ------------------------------------------------------
            line = line.strip()

            # Skips empty lines
            # ------------------
            if line:

                # Split the line and use setenv expressions for key-value pairs
                # -------------------------------------------------------------
                parts = line.split()

                if parts[0] == 'setenv':
                    key = parts[1]
                    rcdict[key] = parts[2]

        return rcdict

    # ----------------------------------------------------------------------------------------------

    def parse_rc(self, rcfile):

        # Parse AGCM.rc & CAP.rc line by line. It ignores comments and commented
        # out lines. Some values involve multiple ":" characters which required
        # some extra steps to handle them as dictionary values.
        # ----------------------------------------------------------------------

        with open(rcfile, 'r') as file:
            lines = file.readlines()

        rcdict = {}

        for line in lines:
            # Strip any leading or trailing whitespace from the line
            # ------------------------------------------------------
            line = line.strip()

            # Skip if the line is a comment (i.e., starts with #)
            # ------------------------------------------------------
            if line.startswith("#"):
                continue

            # Split the line to ignore comments after #
            # ---------------------------------------------
            parts = line.split('#', 1)
            line = parts[0]

            # Split the line into key and value using the first occurrence of ":" as the delimiter
            # This part is required because of AGCM.rc entries with confusing
            # lines (e.g., CH4_FRIENDLIES: DYNAMICS:TURBULENCE:MOIST)
            # ------------------------------------------------------------------------------------
            split_line = line.split(":", 1)
            if len(split_line) == 2:
                key, value = split_line
                # Re-join any remaining parts of the value with ":" again
                # -------------------------------------------------------
                value = value.split(":")
                value = ":".join(value)

                # Strip any whitespace from the key and value
                # --------------------------------------------
                key = key.strip()
                value = value.strip()
                rcdict[key] = value

        return rcdict

    # ----------------------------------------------------------------------------------------------

    def process_nml(self, cold_restart=False):

        # In gcm_run.j, fvcore_layout.rc is concatenated with input.nml
        # -------------------------------------------------------------

        nml1 = f90nml.read(self.at_cycle_geosdir('input.nml'))

        if not cold_restart:
            self.logger.info('Hot start, Swell expects require rst/checkpoint files')

            # mom_input_nml needs to be 'r' for hot_restart
            # ----------------------------------------------
            nml1['mom_input_nml']['input_filename'] = 'r'

        nml2 = f90nml.read(self.at_cycle_geosdir('fvcore_layout.rc'))

        # Combine the dictionaries and write the new input.nml
        # ---------------------------------------------------
        nml_comb = {**nml1, **nml2}

        self.logger.info('Combining input.nml and fvcore_layout.rc')

        with open(self.at_cycle_geosdir('input.nml'), 'w') as f:
            f90nml.write(nml_comb, f)

    # ----------------------------------------------------------------------------------------------

    def rc_assign(self, rcdict, key_inquiry):

        # Some of the gcm_run.j steps involve setting environment values using
        # .rc files. These files may or may not have some of the key values used
        # for environment setting. Hence, they will be assigned 'False'.
        # ----------------------------------------------------------------------

        if key_inquiry not in rcdict:
            rcdict.setdefault(key_inquiry, False)

    # --------------------------------------------------------------------------------------------------

    def rc_to_bool(self, rcdict):

        # .rc files have switch values in .TRUE. or .FALSE. format, some might
        # have T and F.
        # This method converts them to python boolean and assumes only two types
        # of input. It can also converts faulty formats (i.e., .True. , .False)
        # ----------------------------------------------------------------------

        for key, value in rcdict.items():
            if rcdict[key].strip('.').lower() == 'true':
                rcdict[key] = True
            elif rcdict[key].strip('.').lower() == 't':
                rcdict[key] = True
            elif rcdict[key].strip('.').lower() == 'false':
                rcdict[key] = False
            elif rcdict[key].strip('.').lower() == 'f':
                rcdict[key] = False
            else:
                continue

        return rcdict

    # --------------------------------------------------------------------------------------------------

    def resub(self, filename, pattern, replacement):

        # Replacing string values involving wildcards
        # -------------------------------------------
        with open(filename, 'r') as f:
            full_text = f.read()

        # Perform the substitution and write the output to a new file
        # -----------------------------------------------------------
        modified_text = re.sub(pattern, replacement, full_text, flags=re.MULTILINE)

        with open(filename, 'w') as out_file:
            out_file.write(modified_text)

    # ----------------------------------------------------------------------------------------------

    def run_executable(self, cycle_dir, np, geos_executable, geos_modules, output_log):

        # Run the GEOS executable
        # -----------------------
        self.logger.info('Running '+geos_executable+' with '+str(np)+' processors.')

        command = f'source {geos_modules} \n' + \
            # f'export I_MPI_ADJUST_ALLREDUCE=12 \n' + \
            # f'export I_MPI_ADJUST_GATHERV=3 \n' + \
            # f'export I_MPI_SHM_HEAP_VSIZE=512 \n' + \
            # f'export PSM2_MEMORY=large \n' + \
            # f'export I_MPI_EXTRA_FILESYSTEM=1 \n' + \
            # f'export OMP_NUM_THREADS=1 \n' + \
            # f'I_MPI_EXTRA_FILESYSTEM_FORCE=gpfs \n' + \
            f'cd {cycle_dir} \n' + \
            # f'env  LD_PRELOAD=/discover/nobackup/dardag/SwellExperiments/swell-3dvar_cycle/GEOSgcm/build/lib/libmom6.so \n' + \
            f'mpirun -np {np} {geos_executable} ' + \
            f'--logging_config logging.yaml'

        # Run command within bash environment
        # -----------------------------------
        run_track_log_subprocess(self.logger, ['/bin/bash', '-c', command], output_log=output_log)

# --------------------------------------------------------------------------------------------------
