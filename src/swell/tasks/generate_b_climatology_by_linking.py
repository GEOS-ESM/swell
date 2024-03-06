# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import link_all_files_from_first_in_hierarchy_of_sources


# --------------------------------------------------------------------------------------------------


class GenerateBClimatologyByLinking(taskBase):

    def execute(self):
        """Acquires B Matrix files for background error model(s):

            - EXPLICIT_DIFFUSION:

            For geos_marine, horizontal corr. scales solely depend on the tripolar grid
            hence they are located in the swell_static_files directory. Meanwhile,
            vertical corr. scales are MLD dependent. Hence, this task will check
            for the vertical diffusion files corresponding to the current cycle.
            If it fails, it will move onto generate these files via the
            GenerateBClimatology task.

            - BUMP:

            This one is currently not supported. However, it will likely become
            an option again once higher resolution grid tests are executed.

        Parameters
        ----------
            All inputs are extracted from the JEDI experiment file configuration.
            See the taskBase constructor for more information.
        """

        # Get the flavor of static background error model
        # -----------------------------------------------
        background_error_model = self.config.background_error_model()

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        self.jedi_rendering.add_key('background_error_model', self.config.background_error_model())

        # Extract general parts of the config
        # -----------------------------------
        swell_static_files_main = self.config.swell_static_files()
        swell_static_files_user = self.config.swell_static_files_user(None)

        # Set the destination directory
        # ------------------------------
        target_path = os.path.join(self.cycle_dir(), 'background_error_model')
        os.makedirs(target_path, mode=0o777, exist_ok=True)

        # Source path base the part that looks like /path/to/static_background_error/
        # -------------------------------------------------------------------------
        source_path_base = os.path.join('jedi', 'interfaces', self.get_model(), 'model',
                                        'static_background_error', background_error_model)

        # Compute data assimilation window parameters to obtain the local background time
        # -------------------------------------------------------------------------------
        window_offset = self.config.window_offset()
        window_type = self.config.window_type()
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)

        # Background
        # ----------
        self.jedi_rendering.add_key('local_background_time', local_background_time)

        # Model specific part of the path, i.e. anything that goes between the base path above,
        # and the actual files that need to be linked into the directory.
        # The name of the correlation file is also defined, which could be useful in the
        # long run.
        # ------------------------------------------------------------------------------
        if background_error_model == 'explicit_diffusion':
            horizontal_resolution = self.config.horizontal_resolution()
            vertical_resolution = self.config.vertical_resolution()
            res_path = horizontal_resolution + 'x' + vertical_resolution

            correlation_files = 'vt.' + local_background_time + '.nc'
        else:
            self.logger.abort("Only explicit diffusion is supported")

        # List of source paths to search for some existing files. A limitation of this code is that
        # it does not know the name of the files that should be linked. It will link all files that
        # it finds in the first directory that some are found in. The first place to look is a user
        # provided path containing swell static files. The user would be responsible for filling
        # those directories in a way that is compliant with the above. Secondly, it searches the
        # centrally controlled swell static files directory.

        source_paths = []
        # First, append with any user provided path
        # ------------------------------------------
        if swell_static_files_user is not None:
            source_paths.append(os.path.join(swell_static_files_user, source_path_base,
                                             res_path, correlation_files))
        # Second, append with centrally controlled path
        # ----------------------------------------------
        source_paths.append(os.path.join(swell_static_files_main, source_path_base,
                                         res_path, correlation_files))

        # First check the users swell static files path
        # ----------------------------------------------
        link_all_files_from_first_in_hierarchy_of_sources(self.logger, source_paths, target_path)

# --------------------------------------------------------------------------------------------------
