# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import re
import datetime as pydatetime

# --------------------------------------------------------------------------------------------------
#  @package datetime
#
#  Class containing the datetime
#
# --------------------------------------------------------------------------------------------------


class Datetime:

    def __init__(self, datetime_input):

        # Convert input string to standard format yyyymmddHHMMSS
        datetime_str = re.sub('[^0-9]', '', datetime_input+'000000')[0:14]

        # Convert string to datetime object
        self.datetime = pydatetime.datetime.strptime(datetime_str, '%Y%m%d%H%M%S')


# --------------------------------------------------------------------------------------------------
