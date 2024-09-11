# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import datetime
import isodate

from swell.utilities.datetime_util import datetime_formats


# --------------------------------------------------------------------------------------------------


class DataAssimilationWindowParams():

    def __init__(self, logger: 'Logger', cycle_time: str) -> None:

        """
        Defines cycle dependent parameters for the data assimilation window and adds to config
        """

        # Keep logger
        self.logger = logger

        # Current cycle datetime object
        self.__current_cycle_dto__ = datetime.datetime.strptime(cycle_time,
                                                                datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def __get_window_begin_dto__(self, window_offset: str) -> datetime:

        window_offset_dur = isodate.parse_duration(window_offset)
        return self.__current_cycle_dto__ - window_offset_dur

    # ----------------------------------------------------------------------------------------------

    def __get_local_background_time__(self, window_type: str, window_offset: str) -> datetime:

        # Background time for the window
        if window_type == '4D':
            local_background_time = self.__get_window_begin_dto__(window_offset)
        elif window_type == '3D':
            local_background_time = self.__current_cycle_dto__

        return local_background_time

    # ----------------------------------------------------------------------------------------------

    def window_begin(self, window_offset: str, dto: bool = False) -> str:

        window_begin_dto = self.__get_window_begin_dto__(window_offset)

        # Return datetime object if asked
        if dto:
            return window_begin_dto

        return window_begin_dto.strftime(datetime_formats['directory_format'])

    # ----------------------------------------------------------------------------------------------

    def window_begin_iso(self, window_offset: str, dto: bool = False):

        window_begin_dto = self.__get_window_begin_dto__(window_offset)

        # Return datetime object if asked
        if dto:
            return window_begin_dto

        return window_begin_dto.strftime(datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def window_end_iso(self, window_offset: str, window_length: str, dto: bool = False) -> str:

        # Compute window length duration
        window_length_dur = isodate.parse_duration(window_length)

        # Get window beginning time
        window_begin_dto = self.__get_window_begin_dto__(window_offset)

        # Window end time
        window_end_dto = window_begin_dto + window_length_dur

        # Return datetime object if asked
        if dto:
            return window_end_dto

        return window_end_dto.strftime(datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def background_time(self, window_offset: str, background_time_offset: str) -> str:

        background_time_offset_dur = isodate.parse_duration(background_time_offset)
        background_time_dto = self.__current_cycle_dto__ - background_time_offset_dur
        return background_time_dto.strftime(datetime_formats['directory_format'])

    # ----------------------------------------------------------------------------------------------

    def local_background_time_iso(self, window_offset: str, window_type: str) -> str:

        local_background_time = self.__get_local_background_time__(window_type, window_offset)
        return local_background_time.strftime(datetime_formats['iso_format'])

    # ----------------------------------------------------------------------------------------------

    def local_background_time(self, window_offset: str, window_type: str) -> str:

        local_background_time = self.__get_local_background_time__(window_type, window_offset)
        return local_background_time.strftime(datetime_formats['directory_format'])

    # ----------------------------------------------------------------------------------------------
