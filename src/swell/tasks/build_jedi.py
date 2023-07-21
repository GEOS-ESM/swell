# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from jedi_bundle.bin.jedi_bundle import execute_tasks

from swell.tasks.base.task_base import taskBase
from swell.utilities.build import set_jedi_bundle_config, get_bundles, build_and_source_dirs

# --------------------------------------------------------------------------------------------------


class BuildJedi(taskBase):

    def execute(self):

        # Get the experiment/jedi_bundle directory
        # ----------------------------------------
        swell_exp_path = self.experiment_path()
        jedi_bundle_path = os.path.join(swell_exp_path, 'jedi_bundle')

        # Get paths to build and source
        # -----------------------------
        jedi_bundle_build_path, jedi_bundle_source_path = build_and_source_dirs(jedi_bundle_path)

        # Choice to link to existing build or build JEDI using jedi_bundle
        # ----------------------------------------------------------------
        if self.config.jedi_build_method() == 'create':

            # Determine which bundles need to be build
            model_components = self.get_model_components()
            if model_components is not None:
                bundles = []
                for model_component in model_components:
                    # Open the metadata config for interface
                    meta = self.jedi_rendering.render_interface_meta()
                    bundles.append(meta['jedi_interface'])
            else:
                bundles_default = get_bundles()

            # Generate the build dictionary
            jedi_bundle_dict = set_jedi_bundle_config(self.config.bundles(bundles_default),
                                                      jedi_bundle_source_path,
                                                      jedi_bundle_build_path, 24)

            # Perform the clone of JEDI repos
            try:
                execute_tasks(['configure', 'make'], jedi_bundle_dict)
            except Exception:
                self.logger.abort(f'A failure occurred in jedi_bundle.execute_tasks')

        else:

            self.logger.abort(f'Found \'{self.config.jedi_build_method()}\' for ' +
                              f'jedi_build_method in the  experiment dictionary. Must be ' +
                              f'\'create\'.')


# --------------------------------------------------------------------------------------------------
