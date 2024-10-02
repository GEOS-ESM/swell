# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from jedi_bundle.bin.jedi_bundle import execute_tasks, get_bundles

from swell.utilities.build import link_path
from swell.tasks.base.task_base import taskBase
from swell.utilities.pinned_versions.check_hashes import check_hashes
from swell.utilities.build import set_jedi_bundle_config, build_and_source_dirs


# --------------------------------------------------------------------------------------------------


class CloneJedi(taskBase):

    def execute(self) -> None:

        # Get the experiment/jedi_bundle directory
        # ----------------------------------------
        swell_exp_path = self.experiment_path()
        jedi_bundle_path = os.path.join(swell_exp_path, 'jedi_bundle')

        # Get paths to build and source
        # -----------------------------
        jedi_bundle_build_path, jedi_bundle_source_path = build_and_source_dirs(jedi_bundle_path)

        # Choice to link to existing build or build JEDI using jedi_bundle
        # ----------------------------------------------------------------
        if self.config.jedi_build_method() == 'use_existing':

            # Link the source code directory
            link_path(self.config.existing_jedi_source_directory(), jedi_bundle_source_path)

        elif self.config.jedi_build_method() == 'use_pinned_existing':

            # Check hashes before proceeding
            check_hashes(self.config.existing_jedi_source_directory_pinned(), self.logger)

            # Link the pinned source code directory
            link_path(self.config.existing_jedi_source_directory_pinned(), jedi_bundle_source_path)

        elif self.config.jedi_build_method() in ('create', 'pinned_create'):

            # Determine which bundles need to be build
            model_components = self.get_model_components()
            if model_components is not None:
                bundles = []
                for model_component in model_components:
                    # Open the metadata config for interface
                    self.jedi_rendering.add_key('npx_proc', '1')
                    self.jedi_rendering.add_key('npy_proc', '1')
                    self.jedi_rendering.add_key('total_processors', '1')
                    meta = self.jedi_rendering.render_interface_meta(model_component)
                    bundles.append(meta['jedi_interface'])
            else:
                bundles = get_bundles()

            # Determine whether to use pinned versions or not
            use_pinned = False
            if self.config.jedi_build_method() == 'pinned_create':
                use_pinned = True

            # Generate the build dictionary
            jedi_bundle_dict = set_jedi_bundle_config(self.config.bundles(bundles),
                                                      jedi_bundle_source_path,
                                                      jedi_bundle_build_path,
                                                      self.platform(),
                                                      use_pinned)

            # Perform the clone of JEDI repos
            try:
                execute_tasks(['clone'], jedi_bundle_dict)
            except Exception:
                self.logger.abort(f'A failure occurred in jedi_bundle.execute_tasks')

        else:

            self.logger.abort(f'Found \'{self.config.jedi_build_method()}\' for ' +
                              f'jedi_build_method in the experiment dictionary. Must be ' +
                              f'\'use_existing\', \'use_pinned_existing\', ' +
                              f'\'create\' or \'pinned_create\'.')


# --------------------------------------------------------------------------------------------------
