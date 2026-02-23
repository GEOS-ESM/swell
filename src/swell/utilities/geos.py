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
import os
import re
from typing import Tuple, Optional

from swell.utilities.shell_commands import run_subprocess
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


class Geos():
    """
    Utility class for GEOS-specific operations, providing methods to parse configuration
    files, handle time conversions, manage symbolic links, and generate JEDI state
    configurations.
    """

    # ----------------------------------------------------------------------------------------------

    def __init__(
        self,
        logger: Logger,
        forecast_dir: Optional[str],
    ) -> None:
        """
        Initializes the Geos class. The intention is to share methods between forecast-only
        and cycling DA tasks without model-dependent logic.

        Args:
            logger (Logger): Logger object for reporting messages and errors.
            forecast_dir (Optional[str]): Path to the forecast directory.
        """

        self.logger = logger
        self.forecast_dir = forecast_dir

    # ----------------------------------------------------------------------------------------------

    def iso_to_time_str(
        self,
        iso_duration: str,
        half: bool = False,
        agcm: bool = False,
    ) -> Tuple[str, int, datetime.timedelta]:
        """
        Converts an ISO 8601 duration string to various time representations.

        Args:
            iso_duration (str): ISO 8601 duration string (e.g., 'PT6H').
            half (bool): If True, divides the duration by two (useful for RESTART). Defaults to False.
            agcm (bool): If True, returns hours in HHH format instead of HH. Defaults to False.

        Returns:
            Tuple[str, int, datetime.timedelta]: A tuple containing:
                - time_string (str): Time formatted as 'HHMMSS' or 'HHHMMSS'.
                - days (int): Number of days in the duration.
                - duration (datetime.timedelta): The duration as a timedelta object.
        """

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

        # Convert the duration to a string in the format of "HHMMSS" to be used in CAP.rc
        # ---------------------------------------------------------------------
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f'{int(hours):02d}{int(minutes):02d}{int(seconds):02d}'

        # If AGCM.rc is used, for RECORD_FREQUENCY the time string should be in the format
        # of "HHHMMSS", where HHH is the total number of hours so need to include days again
        # --------------------------------------------------------------------------------
        if agcm:
            hours = int(hours) + 24 * int(days)
            time_string = f'{hours:03d}{int(minutes):02d}{int(seconds):02d}'

        return time_string, days, duration

    # ----------------------------------------------------------------------------------------------

    def linker(self,
               src: str,
               dst: str,
               dst_dir: str = None
    ) -> None:
        """
        Creates a symbolic link from a source file to a destination.

        Args:
            src (str): Path to the source file.
            dst (str): Name or path of the destination link.
            dst_dir (str, optional): Directory where the link should be created.
                                     Defaults to self.forecast_dir.
        """

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

    def parse_mom6_input(self,
                         mom6_input_path: str
    ) -> dict:
        """
        Parses MOM6 input files (e.g., MOM_oda_incupd) and extracts configuration values.

        Args:
            mom6_input_path (str): Path to the MOM6 input file.

        Returns:
            dict: Dictionary containing parsed key-value pairs from the MOM6 input.
        """

        # Parses the MOM6 input file(s) (e.g., MOM_oda_incupd) and extracts configuration values.
        # ---------------------------------------------------------------------------------
        mom6_config = {}

        # check if the file exists
        if not os.path.isfile(mom6_input_path):
            self.logger.abort(f"MOM6 input file not found: {mom6_input_path}")

        self.logger.info(f"Parsing MOM6 input file: {mom6_input_path}")

        with open(mom6_input_path, 'r') as file:
            for line in file:
                # Ignore comments and empty lines
                line = line.strip()
                if not line or line.startswith('!'):
                    continue

                # Split the line into key and value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove inline comments (anything after '!')
                    if '!' in value:
                        value = value.split('!', 1)[0].strip()

                    # Remove surrounding quotes from strings
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]

                    # Convert boolean and numeric values
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value) if '.' in value else int(value)

                    # Store the key-value pair in the dictionary
                    mom6_config[key] = value

        return mom6_config

    # ----------------------------------------------------------------------------------------------

    def parse_rc(self,
                 rcfile: str
    ) -> dict:
        """
        Parses GEOS .rc files line by line, handling comments, multi-line
        sections (delimited by ::), and empty entries.

        Args:
            rcfile (str): Path to the .rc file to be parsed.

        Returns:
            dict: Dictionary containing the parsed keys and values. Multi-line sections
                  are returned as lists.
        """
        with open(rcfile, 'r') as file:
            lines = file.readlines()

        rcdict = {}
        in_multiline_section = False
        current_section_key = None
        section_content = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Check for start of multi-line section (key followed by ::)
            if line.endswith("::") and line != "::":
                current_section_key = line[:-2].strip()  # Remove :: and get the key
                in_multiline_section = True
                section_content = []
                continue

            # Check for end of multi-line section (standalone ::)
            if line == "::":
                if in_multiline_section and current_section_key:
                    # Store the multiline section as a list
                    rcdict[current_section_key] = section_content.copy()
                in_multiline_section = False
                current_section_key = None
                section_content = []
                continue

            # Collect content inside multi-line sections
            if in_multiline_section:
                section_content.append(line)
                continue

            # Regular key-value parsing
            parts = line.split('#', 1)
            clean_line = parts[0].strip()

            if not clean_line:
                continue

            if ":" in clean_line:
                key, value = clean_line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key:
                    rcdict[key] = value if value else None

        return rcdict

    # ----------------------------------------------------------------------------------------------

    def write_rc(self,
                 rcdict: dict,
                 output_file: str
    ) -> None:
        """
        Writes a dictionary back to a GEOS .rc file format, preserving multi-line sections.

        Args:
            rcdict (dict): Dictionary of RC settings to write.
            output_file (str): Path where the .rc file will be saved.
        """
        with open(output_file, 'w') as file:
            for key, value in rcdict.items():
                if isinstance(value, list):
                    # Multi-line section
                    file.write(f"{key}::\n")
                    for item in value:
                        file.write(f"{item}\n")
                    file.write("::\n")
                elif value is None:
                    # Empty value
                    file.write(f"{key}:\n")
                else:
                    # Regular key-value pair
                    file.write(f"{key}: {value}\n")

    # ----------------------------------------------------------------------------------------------

    def process_nml(self,
                    combine_fvcore: bool = False,
                    cold_restart: bool = False
    ) -> None:
        """
        Adjusts the input.nml file for hot or cold starts and optionally merges
        fvcore_layout.rc settings.

        Args:
            combine_fvcore (bool): If True, merges fvcore_layout.rc into input.nml.
                                   Defaults to False.
            cold_restart (bool): If True, configures for a cold start. Defaults to False.
        """

        # Make sure input.nml is set up properly for hot/cold restart
        nml_comb = f90nml.read(os.path.join(self.forecast_dir, 'input.nml'))

        if not cold_restart:
            self.logger.info('Hot start, Swell will expect rst/checkpoint files')

            # mom_input_nml needs to be 'r' for hot_restart
            # ----------------------------------------------
            nml_comb['mom_input_nml']['input_filename'] = 'r'

        if combine_fvcore:
            self.logger.info('Combining fvcore with input.nml')
            nml2 = f90nml.read(os.path.join(self.forecast_dir, 'fvcore_layout.rc'))
            nml_comb.update(nml2)

        with open(os.path.join(self.forecast_dir, 'input.nml'), 'w') as f:
            f90nml.write(nml_comb, f, sort=False)

    # --------------------------------------------------------------------------------------------------

    def rc_to_bool(self,
                   rcdict: dict
    ) -> dict:
        """
        Converts boolean strings in a GEOS .rc dictionary (e.g., '.TRUE.', '.FALSE.', 'T', 'F')
        to Python boolean objects.

        Args:
            rcdict (dict): Dictionary of settings parsed from an .rc file.

        Returns:
            dict: The updated dictionary with boolean strings converted to bool.
        """

        # .rc files have switch values in .TRUE. or .FALSE. format, some might
        # have T and F.
        # This method converts them to python boolean and assumes only two types
        # of input. It can also convert faulty formats (i.e., .True. , .False)
        # ----------------------------------------------------------------------

        for key, value in rcdict.items():
            # Skip None values and non-string values
            if value is None or not isinstance(value, str):
                continue

            # Strip dots and convert to lowercase for comparison
            normalized_value = value.strip('.').lower()

            if normalized_value == 'true' or normalized_value == 't':
                rcdict[key] = True
            elif normalized_value == 'false' or normalized_value == 'f':
                rcdict[key] = False
            # If it's not a boolean value, keep it as is

        return rcdict

    # ----------------------------------------------------------------------------------------------

    def rename_checkpoints(self,
                           forecast_dir: str
    ) -> None:
        """
        Renames all files ending in '_checkpoint' to '_rst' in the specified directory.

        Args:
            forecast_dir (str): Path to the directory containing checkpoint files.
        """

        # Validate directory exists
        if not os.path.exists(forecast_dir):
            self.logger.abort(f'Directory does not exist: {forecast_dir}')

        self.logger.info(f'Renaming *_checkpoint files to *_rst in {forecast_dir}')

        # Use glob to find checkpoint files instead of relying on shell commands
        checkpoint_pattern = os.path.join(forecast_dir, '*_checkpoint')
        checkpoint_files = glob.glob(checkpoint_pattern)

        if not checkpoint_files:
            self.logger.abort(f'No _checkpoint files found in {forecast_dir}')

        # Rename each file individually for better error handling
        for checkpoint_file in checkpoint_files:
            try:
                # Generate the new filename by replacing _checkpoint with _rst
                rst_file = checkpoint_file.replace('_checkpoint', '_rst')
                # Rename the file
                os.rename(checkpoint_file, rst_file)
                self.logger.info(f'Renamed {os.path.basename(checkpoint_file)}')
                self.logger.info(f'    to {os.path.basename(rst_file)}')

            except OSError as e:
                self.logger.abort(f'Failed to rename {checkpoint_file}: {e}')

    # --------------------------------------------------------------------------------------------------

    def states_generator(self,
                         background_frequency: str,
                         window_length: str,
                         window_begin_iso: str,
                         model: str = 'geos_marine',
                         marine_models: list = []
    ) -> list:
        """
        Generates a list of states for JEDI configuration based on the model type.

        Args:
            background_frequency (str): ISO 8601 duration between background states.
            window_length (str): ISO 8601 duration of the DA window.
            window_begin_iso (str): ISO 8601 datetime string for the start of the window.
            model (str): Model component name (e.g., 'geos_marine'). Defaults to 'geos_marine'.
            marine_models (list): List of active marine model components (e.g., ['cice6']).

        Returns:
            list: A list of dictionaries, each representing a state with its date and filenames.
        """

        states = []
        self.logger.info('Generating states for model: '+model)
        if model in ("geos_marine"):
            states = self.marine_states(background_frequency, window_length, window_begin_iso,
                                        marine_models)

        return states

    # --------------------------------------------------------------------------------------------------

    def marine_states(self,
                      background_frequency: str,
                      window_length: str,
                      window_begin_iso: str,
                      marine_models: list
                      ) -> list:
        """
        Generates states specifically for the geos_marine model component.

        Args:
            background_frequency (str): ISO 8601 duration between background states.
            window_length (str): ISO 8601 duration of the DA window.
            window_begin_iso (str): ISO 8601 datetime string for the start of the window.
            marine_models (list): List of active marine model components.

        Returns:
            list: List of dictionaries containing JEDI state information for marine models.
        """

        static_part = {"basename": "./", "read_from_file": 1}

        # Calculate the number of states using background frequency and window length
        number_of_states = int(isodate.parse_duration(window_length)
                               / isodate.parse_duration(background_frequency)) + 1
        self.logger.info('Number of states: ' + str(number_of_states-1))

        # Generate the list of states dictionary with date and marine filename entries.
        # The date is calculated by adding the background frequency to the window begin date.
        # The ocn_filename is calculated by adding the background frequency to the window begin date
        states = []

        # For FGAT and 4D-Var, the first state is the background state, hence we need to
        # skip the first state in the loop by adding "-1" to the range function.
        for i in range(1, number_of_states):
            hours = int((isodate.parse_duration(background_frequency) * i).total_seconds() / 3600)
            state_dto = isodate.parse_datetime(window_begin_iso) \
                + isodate.parse_duration(background_frequency) * i
            state = {
                "date": state_dto.strftime(datetime_formats['iso_format']),
                "ocn_filename": "ocn.fc." + window_begin_iso + "." + f"PT{hours}H" + ".nc"
            }
            if 'cice6' in marine_models:
                state.update({"ice_filename": "ice.fc." + window_begin_iso + "." + f"PT{hours}H" +
                              ".nc"})
            state.update(static_part)
            states.append(state)

        return states

    # --------------------------------------------------------------------------------------------------

    def write_mom6_input(self, mom6_config: dict, output_path: str) -> None:
        """
        Writes a MOM6 configuration dictionary to a file in MOM6 input format.

        Args:
            mom6_config (dict): Dictionary of MOM6 parameters.
            output_path (str): Path where the MOM6 input file will be written.
        """

        self.logger.info(f"Writing MOM6 configuration to: {output_path}")

        try:
            with open(output_path, 'w') as file:
                file.write("! === module MOM_oda_incupd ===\n")
                for key, value in mom6_config.items():
                    # Format bool values as True/False
                    if isinstance(value, bool):
                        value = "True" if value else "False"
                    # Write the key-value pair to the file
                    file.write(f"{key} = {value}\n")
        except Exception as e:
            self.logger.abort(f"Failed to write MOM6 configuration to {output_path}: {e}")

# --------------------------------------------------------------------------------------------------
