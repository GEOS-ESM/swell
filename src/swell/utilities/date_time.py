# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import isodate


# --------------------------------------------------------------------------------------------------


# Swell datetime format (yyyymmddThhMMssZ)

datetime_formats = {
    'dir_format': "%Y%m%dT%H%M%SZ"        # yyyymmddThhMMssZ for directory formats
    'iso_format': "%Y-%m-%dT%H:%M:%SZ"    # yyyy-mm-ddThh:MM:ssZ ISO format
}

# --------------------------------------------------------------------------------------------------


class DataAssimilationWindowParams():

    def __init__(self, cycle_time, window_offset):

        """
        Defines cycle dependent parameters for the data assimilation window and adds to config
        """

        # Current cycle datetime object
        self.__current_cycle_dto__ = datetime.datetime.strptime(cycle_time,
                                                                datetime_formats['dir_format'])

        # Save the window offset
        self.__window_offset__ = window_offset

    # ----------------------------------------------------------------------------------------------

    def __get_window_begin_dto__(self):

        window_offset_dur = isodate.parse_duration(self.__window_offset__)
        return self.__current_cycle_dto__ - window_offset_dur

    # ----------------------------------------------------------------------------------------------

    def __get_local_background_time__(self, window_type):

        # Background time for the window
        if window_type == '4D':
            local_background_time = self.__get_window_begin_dto__(self.__window_offset__)
        elif window_type == '3D':
            local_background_time = self.__current_cycle_dto__

        return local_background_time

    # ----------------------------------------------------------------------------------------------

    def window_begin(self):

        window_begin_dto = self.__get_window_begin_dto__()
        return window_begin_dto.strftime(datetime_formats['dir_format'])

    # ----------------------------------------------------------------------------------------------

    def window_begin_iso(self):

        window_begin_dto = self.__get_window_begin_dto__()
        return window_begin_dto.strftime(datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def background_time(self, background_time_offset):

        background_time_offset_dur = isodate.parse_duration(background_time_offset)
        background_time_dto = self.__current_cycle_dto__ - background_time_offset_dur
        return background_time_dto.strftime(datetime_formats['dir_format'])

    # ----------------------------------------------------------------------------------------------

    def local_background_time_iso(self, window_type):

        local_background_time = self.__get_local_background_time__(window_type)
        return local_background_time.strftime(datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def local_background_time(self, window_type):

        local_background_time = self.__get_local_background_time__(window_type)
        return local_background_time.strftime(datetime_formats['dir_format'])

    # ----------------------------------------------------------------------------------------------
