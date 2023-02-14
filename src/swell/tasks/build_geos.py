# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.build import build_and_source_dirs


# --------------------------------------------------------------------------------------------------


class BuildGeos(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        geos_build_method = self.config_get('geos_build_method')

        # Get the experiment/geos directory
        # ---------------------------------
        swell_exp_path = self.get_swell_exp_path()
        geos_gcm_path = os.path.join(swell_exp_path, 'GEOSgcm')

        # Get paths to build and source
        # -----------------------------
        geos_gcm_build_path, geos_gcm_source_path = build_and_source_dirs(geos_gcm_path)

        # Check that the choice is to create build
        # ----------------------------------------
        if not geos_build_method == 'create':
            self.logger.abort(f'Found \'{jedi_build_method}\' for jedi_build_method in the '
                                          f'experiment dictionary. Must be \'create\'.')

        # Run parallel build script
        # -------------------------


# --------------------------------------------------------------------------------------------------
