# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os

from solo.ioda import Ioda

from swell.tasks.base.task_base import taskBase
from swell.utilities.observations import find_instrument_from_string


# --------------------------------------------------------------------------------------------------


class MergeIodaFiles(taskBase):

    """
    Task to combine IODA output files written by each processor of a JEDI run.
    """

    def execute(self):

        # Dictionary with observation config
        ob_configs = self.config.get('OBSERVATIONS')

        # Loop over observations
        for ob_config in ob_configs:

            # Split the full path into path and filename
            cycle_dir, obs_file_path = os.path.split(ob_config['obs space']['obsdataout']['obsfile'])

            # Get instrument name
            obs_file = os.path.split(obs_file_path)
            obs_file_base = os.path.splitext(obs_file)[0]
            obs_file_extn = os.path.splitext(obs_file)[1]

            filenames = glob.glob(os.path.join(cycle_dir, obs_file_base + '_*.nc4'))

            print()

            print(obs_file)

            print(os.path.split(obs_file))

            exit()

            instrument = find_instrument_from_string(obs_file, self.logger)

            # Log the instrument being processed
            self.logger.info('Combining IODA output files for '+instrument+'.')

            # Get a list of files for this instrument
            filenames = glob.glob(os.path.join(cycle_dir, '*'+instrument+'*.*Z_*.nc4'))

            # Output files that are being concatenated
            self.logger.info('Files: ')
            filenames.sort()
            for filename in filenames:
                self.logger.info(' '+filename)

            # Concatenate each obs file into one file, based on current obs window
            if (len(filenames)) > 0:
                ioda = Ioda(instrument)
                ioda.concat_files(filenames, os.path.join(cycle_dir, obs_file))
