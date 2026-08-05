# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import re
import datetime as pydatetime
from isodate import parse_duration, parse_datetime, ISO8601Error

# --------------------------------------------------------------------------------------------------

datetime_formats = {
    'directory_format': '%Y%m%dT%H%M%SZ',   # yyyymmddThhMMssZ for directory formats
    'ensemble_format': '%Y%m%d_%H%M%Sz',    # yyyymmdd_hhMMssz for JEDI ensemble files
    'geos_format': '%Y%m%d_%H00z',          # yyyymmdd_hh00z for GEOS files
    'gsi_nc_diag_format': '%Y%m%d_%Hz',     # yyyymmdd_hhz Format for GSI netcdf diagnostic files
    'iso_format': '%Y-%m-%dT%H:%M:%SZ',     # yyyy-mm-ddThh:MM:ssZ ISO format
    'short_date': '%Y%m%d%H',               # yyyymmddhh Short format
    'ymd_format': '%Y%m%d',                 # yyyymmdd for acquire_obsys bymd
    'hms_format': '%H%M%S',                 # HHmmss for acquire_obsys bhms
}

# --------------------------------------------------------------------------------------------------


class Datetime:

    def __init__(self, datetime_input) -> None:

        # Convert input string to standard format yyyymmddHHMMSS
        datetime_str = re.sub('[^0-9]', '', datetime_input+'000000')[0:14]

        # Convert string to datetime object
        self.__datetime__ = pydatetime.datetime.strptime(datetime_str, '%Y%m%d%H%M%S')

    # ----------------------------------------------------------------------------------------------

    def dto(self):

        return self.__datetime__

    # ----------------------------------------------------------------------------------------------

    def string_iso(self) -> str:

        return self.__datetime__.strftime(datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def string_directory(self) -> str:

        return self.__datetime__.strftime(datetime_formats['directory_format'])

# ----------------------------------------------------------------------------------------------


def is_duration(dt_str: str) -> bool:
    try:
        parse_duration(dt_str)
    except ISO8601Error:
        return False

    return True

# --------------------------------------------------------------------------------------------------


def is_datetime(dt_str: str) -> bool:
    try:
        parse_datetime(dt_str)
    except ISO8601Error:
        return False

    return True

# --------------------------------------------------------------------------------------------------

def previous_bias_file(cycle_time_dto: Datetime,
                       target_file: str,
                       window_length: str,
                       background_time_offset) -> str:
    
    # This requires two modifications, one in the directory and one in the filename.
    # Start with the changing the bias filename
    # -----------------------------------------------------------------
    bias_file = os.path.basename(target_file)

    # Get the date bit from the target file
    bias_path = os.path.dirname(target_file)
    dt_str = bias_path.split('/')[-2]

    # Get the previous cycle datetime string and replace it in the bias path
    previous_cycle_dto = cycle_time_dto - parse_duration(window_length)
    previous_cycle_dt_str = previous_cycle_dto.strftime(datetime_formats['directory_format'])

    bias_path = bias_path.replace(dt_str, previous_cycle_dt_str)

    # Get the previous cycle's offset time
    previous_cycle_offset = previous_cycle_dto - parse_duration(background_time_offset)
    previous_cycle_offset_str = previous_cycle_offset.strftime(datetime_formats['directory_format'])

    # Get the current cycle's offset time, so it can be replaced
    current_cycle_offset = cycle_time_dto - parse_duration(background_time_offset)
    current_cycle_offset_str = current_cycle_offset.strftime(datetime_formats['directory_format'])

    bias_file = bias_file.replace(current_cycle_offset_str, previous_cycle_offset_str)

    # Combine the new bias path and the file name
    # ---------------------------------------------
    new_target_file = os.path.join(bias_path, bias_file)

    return new_target_file

# --------------------------------------------------------------------------------------------------
