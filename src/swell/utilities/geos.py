# (C) Copyright 2023- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import datetime
import f90nml
import glob
import isodate
import netCDF4
import os
import re
from typing import Tuple, Optional, Union

from swell.utilities.shell_commands import run_subprocess
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


class Geos():

    # ----------------------------------------------------------------------------------------------

    def __init__(self, logger: Logger, forecast_dir: Optional[str]) -> None:

        '''
        Intention with GEOS class is to not have any model dependent methods.
        This way both forecast only and cycle DA tasks can benefit from the same
        methods.
        '''

        self.logger = logger
        self.forecast_dir = forecast_dir

    # ----------------------------------------------------------------------------------------------

    def adjacent_cycle(
        self,
        offset: str,
        return_date: bool = False
    ) -> Union[str, datetime.datetime]:

        # Basename consists of swell datetime and model
        # ---------------------------------------------
        dt_str = os.path.basename(os.path.dirname(self.forecast_dir))
        dt_obj = datetime.datetime.strptime(dt_str, datetime_formats['directory_format'])

        # Modify datetime by using date offset
        # ------------------------------------
        modified_dt_obj = dt_obj + isodate.parse_duration(offset)

        if return_date:
            return modified_dt_obj

        # Replace datetime section in the basename with the modified datetime string
        # -----------------------------------------------------------------
        modified_dt_str = modified_dt_obj.strftime(datetime_formats['directory_format'])

        # Create new file path with modified basename
        # --------------------------------------------
        adj_cycle_dir = self.forecast_dir.replace(dt_str, modified_dt_str)

        return adj_cycle_dir

    # ----------------------------------------------------------------------------------------------

    def chem_rename(self, rcdict: dict) -> None:

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
        }

        for key, value in chem_files.items():
            fname = os.path.join(self.forecast_dir, value)

            if not rcdict[key] and os.path.isfile(fname):
                self.logger.info(' Renaming file: '+fname)
                os.system('rename .rc .rc.NOT_USED ' + fname)

    # ----------------------------------------------------------------------------------------------

    def exec_python(self, script_src: str, script: str, input: str = '') -> None:

        # Source g5_modules and execute py scripts in a new shell process then
        # return to the current one
        # Define the command to source the Bash script and run the Python command
        # -----------------------------------------------------------------------
        command = f'source {script_src}/g5_modules.sh \n' + \
            f'cd {self.forecast_dir} \n' + \
            f'{script_src}/{script} {input}'

        # Containerized run of the GEOS build steps
        # -----------------------------------------
        run_subprocess(self.logger, ['/bin/bash', '-c', command])

    # ----------------------------------------------------------------------------------------------

    def get_rst_time(self) -> datetime.datetime:

        # Obtain time information from any of the rst files listed by glob
        # ----------------------------------------------------------------
        src = os.path.join(self.forecast_dir, '*_rst')

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

    def iso_to_time_str(
        self,
        iso_duration: str,
        half: bool = False
    ) -> Tuple[str, int, datetime.timedelta]:

        # Parse the ISO duration string and get the total number of seconds
        # It is written to handle fcst_duration less than a day for now
        # ----------------------------------------------------------------
        duration = isodate.parse_duration(iso_duration)
        duration_seconds = duration.total_seconds()

        # RESTART is produced at the half of the forecast cycle
        # We will also assume that the beginning of the DA window is half of the
        # forecast cycle which is when we need the first checkpoint dumps.
        # -----------------------------------------------------------------------
        if half:
            duration = duration / 2
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

        return time_string, days, duration

    # ----------------------------------------------------------------------------------------------

    def linker(self, src: str, dst: str, dst_dir: str = None) -> None:

        # Link files from BC directories
        # ------------------------------
        if dst_dir is None:
            dst_dir = self.forecast_dir

        dst = os.path.basename(dst)

        # Assign dst name if non-existent
        # ------------------------------
        if dst == '':
            dst = os.path.basename(src)

        # Check if src file exists
        # ------------------------
        if not os.path.exists(src):
            self.logger.abort(f'Source file does not exist: {src}')

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

    def parse_gcmrun(self, jfile: str) -> dict:

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

    def parse_rc(self, rcfile: str) -> dict:

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

    def process_nml(self, cold_restart: bool = False) -> None:

        # In gcm_run.j, fvcore_layout.rc is concatenated with input.nml
        # -------------------------------------------------------------

        nml1 = f90nml.read(os.path.join(self.forecast_dir, 'input.nml'))

        if not cold_restart:
            self.logger.info('Hot start, Swell will expect rst/checkpoint files')

            # mom_input_nml needs to be 'r' for hot_restart
            # ----------------------------------------------
            nml1['mom_input_nml']['input_filename'] = 'r'

        nml2 = f90nml.read(os.path.join(self.forecast_dir, 'fvcore_layout.rc'))

        # Combine the dictionaries and write the new input.nml
        # ---------------------------------------------------
        nml_comb = {**nml1, **nml2}

        self.logger.info('Combining input.nml and fvcore_layout.rc')

        with open(os.path.join(self.forecast_dir, 'input.nml'), 'w') as f:
            f90nml.write(nml_comb, f)

    # ----------------------------------------------------------------------------------------------

    def rc_assign(self, rcdict: dict, key_inquiry: str) -> None:

        # Some of the gcm_run.j steps involve setting environment values using
        # .rc files. These files may or may not have some of the key values used
        # for environment setting. Hence, they will be assigned 'False'.
        # ----------------------------------------------------------------------

        if key_inquiry not in rcdict:
            rcdict.setdefault(key_inquiry, False)

    # --------------------------------------------------------------------------------------------------

    def rc_to_bool(self, rcdict: dict) -> dict:

        # .rc files have switch values in .TRUE. or .FALSE. format, some might
        # have T and F.
        # This method converts them to python boolean and assumes only two types
        # of input. It can also convert faulty formats (i.e., .True. , .False)
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

    # ----------------------------------------------------------------------------------------------

    def rename_checkpoints(self, next_geosdir):

        # Rename _checkpoint files to _rst
        # Move to the next geos cycle directory
        # -------------------------------------
        os.chdir(next_geosdir)

        self.logger.info('Renaming *_checkpoint files to *_rst')
        try:
            os.system('rename -v _checkpoint _rst *_checkpoint')
        except Exception:
            self.logger.abort('Renaming failed, see if checkpoint files exists')

    # --------------------------------------------------------------------------------------------------

    def resub(self, filename: str, pattern: str, replacement: str) -> None:

        # Replacing string values involving wildcards
        # -------------------------------------------
        with open(filename, 'r') as f:
            full_text = f.read()

        # Perform the substitution and write the output to a new file
        # -----------------------------------------------------------
        modified_text = re.sub(pattern, replacement, full_text, flags=re.MULTILINE)

        with open(filename, 'w') as out_file:
            out_file.write(modified_text)

# --------------------------------------------------------------------------------------------------
