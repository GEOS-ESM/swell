# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import shutil
import subprocess
from datetime import datetime
import isodate

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
            fname = os.path.join(self.cycle_dir, value)
            
            if not rcdict[key] and os.path.isfile(fname):
                self.logger.info(' Renaming file: '+fname)
                os.system('rename .rc .rc.NOT_USED ' + fname)

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

            # Split the line to ignore any comment after #
            # ---------------------------------------------
            parts = line.split('#', 1)
            line = parts[0]

            # Split the line into key and value using the first occurrence of ":" as the delimiter
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

        # .rc files have switch values in .TRUE. or .FALSE. format.
        # This method converts it to python boolean and assumes only two types
        # of input. It can also accept faulty formats (i.e., .True. , .False) 
        # ----------------------------------------------------------------------

        for key, value in rcdict.items():
            if rcdict[key].strip('.').lower() == 'true':
                rcdict[key] = True
            elif rcdict[key].strip('.').lower() == 'false':
                rcdict[key] = False
            else:
                continue

        return rcdict

    # --------------------------------------------------------------------------------------------------

    def replace_str(self, filename, instr, outstr):

        # Replacing string values
        # ------------------------

        with open(os.path.join(self.cycle_dir,filename), 'r') as file:
            # Find and replace the contents of the file
            # -----------------------------------------
            file_contents = file.read()
            try:
                modified_contents = file_contents.replace(instr, outstr)
            except Exception:
                self.logger.abort('Modifying file failed. GCM wont execute')

        with open(os.path.join(self.cycle_dir,filename), 'w') as file:
            file.write(modified_contents)

    # ----------------------------------------------------------------------------------------------

    def run_executable(self, cycle_dir, np, geos_executable_path, geos_source, output_log):

        # Run the GEOS executable
        # -----------------------
        self.logger.info('Running '+geos_executable_path+' with '+str(np)+' processors.')

        command = [
            'source', f'{geos_source}', '&&',
            'mpirun', '-np', str(np), f'{geos_executable_path}',
            '--logging_config', 'logging.yaml' ]

        # Move to the cycle directory
        # ---------------------------
        os.chdir(cycle_dir)

        # Run command
        # -----------
        run_track_log_subprocess(self.logger, command, output_log=output_log)

# --------------------------------------------------------------------------------------------------
