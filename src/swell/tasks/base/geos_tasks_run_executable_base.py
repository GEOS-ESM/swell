# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime
import f90nml, netCDF4
import isodate
import os, glob, re
import shutil
import subprocess

from abc import ABC, abstractmethod

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess


# --------------------------------------------------------------------------------------------------


class GeosTasksRunExecutableBase(taskBase):

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self):

        # This class does not execute, it provides helper function for the children
        # ------------------------------------------------------------------------
        pass


    # ----------------------------------------------------------------------------------------------


    def at_cycle(self, paths):

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        # Combining list of paths with cycle dir for script brevity 
        # ---------------------------------------------------------
        full_path = os.path.join(self.cycle_dir, *paths)
        return full_path


    # ----------------------------------------------------------------------------------------------


    def fetch_to_cycle(self, src_dir, dst_dir=None):

        self.cycle_dir = self.config_get('cycle_dir')

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


    def exec_python(self, script_src, script, input = '', dev = False):

        # Source g5_modules then execute py scripts
        # -----------------------------------------

        # This allows executing python scripts within the cycle_dir
        # ---------------------------------------------------------
        if dev:
            os.chdir(self.cycle_dir)

        # Define the command to source the Bash script and run the Python command
        # -----------------------------------------------------------------------
        command = [
            f'source {script_src}/g5_modules.sh && ' + \
            f'python {script_src}/{script} {input}'
        ]

        # Run the command using subprocess. No need for logger here
        # ---------------------------------------------------------
        subprocess.run(command, shell=True)


    # ----------------------------------------------------------------------------------------------


    def geos_chem_rename(self, rcdict):

        # Some files are renamed according to bool. switches in GEOS_ChemGridComp.rc 
        # -------------------------------------------------------------------------

        # Convert rc bool.s to python 
        # ---------------------------
        rcdict = self.rc_to_bool(rcdict)

        self.cycle_dir = self.config_get('cycle_dir')

        # GEOS Chem filenames, shares same keys as rcdict
        # -----------------------------------------------
        chem_files = {
            'ENABLE_STRATCHEM' : 'StratChem_ExtData.rc',
            'ENABLE_GMICHEM' : 'GMI_ExtData.rc',
            'ENABLE_GEOSCHEM' : 'GEOSCHEMchem_ExtData.rc',
            'ENABLE_CARMA' : 'CARMAchem_GridComp_ExtData.rc',
            'ENABLE_DNA' : 'DNA_ExtData.rc',
            'ENABLE_ACHEM' : 'GEOSachem_ExtData.rc',
            'ENABLE_GOCART_DATA' : 'GOCARTdata_ExtData.rc',
        }

        for key, value in chem_files.items():
            fname = self.at_cycle(value)
            
            if not rcdict[key] and os.path.isfile(fname):
                self.logger.info(' Renaming file: '+fname)
                os.system('rename .rc .rc.NOT_USED ' + fname)


    # ----------------------------------------------------------------------------------------------


    def geos_linker(self, src, dst, dst_dir=None):

        # Link files from BC directories
        # ------------------------------

        if dst_dir is None:
            dst_dir = self.cycle_dir

        if os.path.exists(os.path.join(dst_dir, dst)):
            os.unlink(os.path.join(dst_dir, dst))

        try:
            os.symlink(src, os.path.join(dst_dir, dst))
        except Exception:
            self.logger.abort('Linking failed, see if source files exists')
    # ----------------------------------------------------------------------------------------------


    def get_rst_time(self):

        # Obtain time information from any of the rst files listed by the
        # glob method
        # --------------------------------------------------------------------

        src = self.at_cycle('*_rst')

        # Open the NetCDF file and read the time and units
        # ------------------------------------------------
        ncfile = netCDF4.Dataset(list(glob.glob(src))[0])
        time_var = ncfile.variables['time']
        units = time_var.units

        # Convert the time values to datetime objects
        # ---------------------------------------------
        times = netCDF4.num2date(time_var[:], units=units, calendar='standard')

        self.logger.info('This is not used yet')
        ncfile.close()


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


    def previous_cycle(self, cycle_dir, forecast_duration):

        # Basename consists of swell datetime and model
        # ---------------------------------------------
        basename = os.path.basename(cycle_dir)
        dt_str = basename.split('-')[0]
        dt_obj = datetime.strptime(dt_str, self.get_datetime_format())

        # Modify datetime by subtracting forecast duration
        # -----------------------------------------------
        modified_dt_obj = dt_obj - isodate.parse_duration(forecast_duration)

        # Replace datetime section in the basename with the modified datetime string
        # -----------------------------------------------------------------
        modified_dt_str = modified_dt_obj.strftime(self.get_datetime_format())
        modified_basename = basename.replace(dt_str, modified_dt_str)

        # Create new file path with modified basename
        # --------------------------------------------
        previous_cycle_dir = os.path.join(os.path.dirname(cycle_dir), modified_basename)

        return previous_cycle_dir


    # ----------------------------------------------------------------------------------------------


    def process_nml(self, cold_restart=False):

    # In gcm_run.j, fvcore_layout.rc is concatenated with input.nml
    # -------------------------------------------------------------

        nml1 = f90nml.read(self.at_cycle('input.nml'))

        if not cold_restart:
            self.logger.info('Hot start, will require rst/checkpoint files')

            # mom_input_nml needs to be 'r' for hot_restart
            # ----------------------------------------------
            nml1['mom_input_nml']['input_filename'] = 'r'

        nml2 = f90nml.read(self.at_cycle('fvcore_layout.rc'))

        # Combine the dictionaries and write the new input.nml
        # ---------------------------------------------------
        nml_comb = {**nml1, **nml2}

        self.logger.info('Combining input.nml and fvcore_layout.rc')

        with open(self.at_cycle('input.nml'), 'w') as f:
            f90nml.write(nml_comb, f)


    # ----------------------------------------------------------------------------------------------


    def rc_assign(self, rcdict, key_inquiry):

        # Some of the gcm_run.j steps involve setting environment values using
        # .rc files. These files may or may not have some of the key values used
        # for environment setting. Hence, they will be assigned 'False'.
        # ----------------------------------------------------------------------

        # Check if the 'key_inquiry' exists in the dictionary
        # ----------------------------------------------------
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

        # Move to the cycle directory
        # ---------------------------
        os.chdir(cycle_dir)

        command = f'source {geos_modules} && ' + \
        f'mpirun -np {np} {geos_executable} ' + \
        f'--logging_config logging.yaml'

        # Run command within bash environment 
        # -----------------------------------
        run_track_log_subprocess(self.logger, ['/bin/bash', '-c', command], output_log=output_log)

# --------------------------------------------------------------------------------------------------
