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
    'directory_format': '%Y%m%dT%H%M%SZ',  # yyyymmddThhMMssZ for directory formats
    'iso_format': '%Y-%m-%dT%H:%M:%SZ'     # yyyy-mm-ddThh:MM:ssZ ISO format
}

# --------------------------------------------------------------------------------------------------

class Datetime:

    def __init__(self, datetime_input):

        # Convert input string to standard format yyyymmddHHMMSS
        datetime_str = re.sub('[^0-9]', '', datetime_input+'000000')[0:14]

        # Convert string to datetime object
        self.datetime = pydatetime.datetime.strptime(datetime_str, '%Y%m%d%H%M%S')

        # Datetime formats
        self.directory_format = datetime_formats['directory_format']
        self.iso_format = datetime_formats['iso_format']

    # ----------------------------------------------------------------------------------------------

    def string_iso(self):

        return self.datetime.strftime(self.iso_format)

    # ----------------------------------------------------------------------------------------------

    def string_directory(self):

        return self.datetime.strftime(self.directory_format)

    # ----------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
