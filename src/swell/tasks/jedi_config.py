# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase

import os
import re
import yaml


# --------------------------------------------------------------------------------------------------


class JediConfig(taskBase):

    def execute(self):

        """Generates the yaml configuration needed to run the JEDI executable.

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.

        """

        # Set full path to the templated config file
        # ------------------------------------------
        jedi_conf_path = os.path.join(self.config.get("suite_dir"), "jedi_config.yaml")

        # Open the template file to dictionary
        # ------------------------------------
        with open(jedi_conf_path, 'r') as ymlfile:
            jedi_conf = yaml.safe_load(ymlfile)

        # Loop over the dictionary and replace elements
        # ---------------------------------------------
        for key in jedi_conf:

            # Strip special characters from element
            element = jedi_conf[key]
            element = element.replace("$", "")
            element = element.replace("{", "")
            element = element.replace("}", "")

            # Replace with element from filled config
            jedi_conf[key] = self.config.get(element)

        # Remove some keys that do not pass yaml validation
        # -------------------------------------------------
        del jedi_conf['initial condition']['filename']

        # Filename for output yaml
        # ------------------------
        cycle_dir = self.config.get("cycle_dir")
        if not os.path.exists(cycle_dir):
            os.makedirs(cycle_dir, 0o755, exist_ok=True)

        jedi_conf_output = os.path.join(cycle_dir, "jedi_config.yaml")

        # Write out the final yaml file
        # -----------------------------
        with open(jedi_conf_output, 'w') as outfile:
            yaml.dump(jedi_conf, outfile, default_flow_style=False)
