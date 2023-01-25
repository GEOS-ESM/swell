# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from jedi_bundle.bin.jedi_bundle import execute_tasks

from swell.tasks.base.task_base import taskBase
from swell.utilities.git_utils import git_got
from swell.utilities.jedi_bundle import set_jedi_bundle_config, get_bundles, build_and_source_dirs
from swell.utilities.jedi_bundle import link_path


# --------------------------------------------------------------------------------------------------


class CloneJedi(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        jedi_build_method = self.config_get('jedi_build_method')

        # Get the experiment/jedi_bundle directory
        # ----------------------------------------
        swell_exp_path = self.get_swell_exp_path()
        jedi_bundle_path = os.path.join(swell_exp_path, 'jedi_bundle')

        # Get paths to build and source
        # -----------------------------
        jedi_bundle_build_path, jedi_bundle_source_path = build_and_source_dirs(jedi_bundle_path)

        # Choice to link to existing build or build JEDI using jedi_bundle
        # ----------------------------------------------------------------
        if jedi_build_method == 'use_existing':

            # Get the existing bundle directory to get the source code
            existing_source_directory = self.config_get('existing_source_directory')

            # Link the source code directory
            link_path(existing_source_directory, jedi_bundle_source_path)

        elif jedi_build_method == 'create':

            # Determine which bundles need to be build
            bundles = get_bundles()
            model_components = self.config_get('model_components', None)
            if model_components is not None:
                bundles = []
                for model_component in model_components:
                    # Open the metadata config for interface
                    meta = self.open_jedi_interface_meta_config_file(model_component)
                    bundles.append(meta['jedi_interface'])

            # Generate the build dictionary
            jedi_bundle_dict = set_jedi_bundle_config(bundles, jedi_bundle_source_path,
                                                      jedi_bundle_build_path)

            # Perform the clone of JEDI repos
            try:
                execute_tasks(['clone'], jedi_bundle_dict)
            except:
                self.logger.abort(f'A failure occurred in jedi_bundle.execute_tasks')

        else:

            self.logger.abort(f'Found \'{jedi_build_method}\' for jedi_build_method in the '
                              f'experiment dictionary. Must be \'use_existing\' or \'create\'.')


# --------------------------------------------------------------------------------------------------
