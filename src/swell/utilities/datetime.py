# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import re
import datetime as pydatetime


# --------------------------------------------------------------------------------------------------

datetime_formats = {
    'directory_format': '%Y%m%dT%H%M%SZ',   # yyyymmddThhMMssZ for directory formats
    'iso_format': '%Y-%m-%dT%H:%M:%SZ',     # yyyy-mm-ddThh:MM:ssZ ISO format
    'gsi_nc_diag_format': '%Y%m%d_%Hz',     # yyyymmdd_hhz Format for GSI netcdf diagnostic files
}

# --------------------------------------------------------------------------------------------------


class Datetime:

    def __init__(self, datetime_input):

        # Convert input string to standard format yyyymmddHHMMSS
        datetime_str = re.sub('[^0-9]', '', datetime_input+'000000')[0:14]

        # Convert string to datetime object
        self.__datetime__ = pydatetime.datetime.strptime(datetime_str, '%Y%m%d%H%M%S')

    # ----------------------------------------------------------------------------------------------

    def dto(self):

        return self.__datetime__

    # ----------------------------------------------------------------------------------------------

    def string_iso(self):

        return self.__datetime__.strftime(datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def string_directory(self):

        return self.__datetime__.strftime(datetime_formats['directory_format'])

    # ----------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
