#!/usr/bin/env python

# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# -------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
import isodate

# --------------------------------------------------------------------------------------------------
# Prep Background superclass
# --------------------------------------------------------------------------------------------------
class PrepBackground(ABC):

    def __init__(self, config):

        # Delegate config object
        self.config = config

        # Parse a few config elements
        self.background_experiment = config.background_experiment()
        self.background_frequency = config.background_frequency(None)
        self.forecast_offset = config.analysis_forecast_window_offset()
        self.horizontal_resolution = config.horizontal_resolution()
        self.window_length = config.window_length()
        self.window_offset = config.window_offset()

        # Duration parameters
        self.window_length_dur = None
        self.forecast_offset_dur = None
        self.forecast_duration_for_background = None

        # Offset parameters
        self.window_offset_dur = None

        # Forecast start time
        self.forecast_start_time = None

        # Initialize a list of background time steps
        self.bkg_steps = []

    @classmethod
    def fromConfig(cls, config):
        return cls(config)

    def prep(self, cycle_time_dto):

        # Reset bkg_steps to empty list if necessary
        self.bkg_steps = []

        self._parse_dur()
        self._offset()
        self._add_bkg_steps(cycle_time_dto)
        self._set_forecast_start_time(cycle_time_dto)

    def _parse_dur(self):

        # Convert to datetime durations
        self.window_length_dur = isodate.parse_duration(self.window_length)
        self.forecast_offset_dur = isodate.parse_duration(self.forecast_offset)
        self.forecast_duration_for_background = self.window_length_dur - self.forecast_offset_dur

    def _set_forecast_start_time(self, cycle_time_dto):
        self.forecast_start_time = cycle_time_dto - self.window_length_dur + self.forecast_offset_dur

    @abstractmethod
    def _offset(self):
        pass

    @abstractmethod
    def _add_bkg_steps(self, *args):
        pass

# --------------------------------------------------------------------------------------------------
# Prep 3D Background subclass
# --------------------------------------------------------------------------------------------------
class PrepBackground3D(PrepBackground):

    def _offset(self):
        return None

    def _add_bkg_steps(self, *args):

        self.bkg_steps.append(isodate.duration_isoformat(self.forecast_duration_for_background))

        return None

# --------------------------------------------------------------------------------------------------
# Prep 4D Background sublcass
# --------------------------------------------------------------------------------------------------
class PrepBackground4D(PrepBackground):

    # -------------------------------------------------------------------------------
    def _offset(self):

        # If the window type is 4D then remove the window offset as first background
        # occurs at the beginning of the window
        self.window_offset_dur = isodate.parse_duration(self.window_offset)

        self.forecast_duration_for_background =\
            self.forecast_duration_for_background - self.window_offset_dur

        return None

    # -------------------------------------------------------------------------------
    def _add_bkg_steps(self, cycle_time_dto):

        self.bkg_steps.append(isodate.duration_isoformat(self.forecast_duration_for_background))

        # If background is provided though files get all backgrounds
        bkg_freq_dur = isodate.parse_duration(self.background_frequency)

        # Check for a sensible frequency
        if (self.window_length_dur/bkg_freq_dur) % 2:
            # !!!!!!!!!!!!!!!! no logger in self
            # self.logger.abort('Window length not divisible by background frequency')
            raise ValueError("Need to call logger somehow.")

        # Loop over window
        print('cycle_time_dto', cycle_time_dto)
        print('window_offset_dur', self.window_offset_dur)

        start_date = cycle_time_dto - self.window_offset_dur
        final_date = cycle_time_dto + self.window_offset_dur

        loop_date = start_date + bkg_freq_dur

        while loop_date <= final_date:

            duration_in = loop_date - start_date + self.forecast_duration_for_background
            self.bkg_steps.append(isodate.duration_isoformat(duration_in))
            loop_date += bkg_freq_dur

        return None

