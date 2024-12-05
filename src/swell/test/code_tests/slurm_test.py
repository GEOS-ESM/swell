# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import logging
import unittest

from swell.utilities.slurm import prepare_scheduling_dict
from unittest.mock import patch, Mock

# --------------------------------------------------------------------------------------------------


class SLURMConfigTest(unittest.TestCase):

    # Mock the `slurm_global_directives` function to ignore "real"
    # configuration and platform-specific settings
    @patch("swell.utilities.slurm.slurm_global_defaults")
    @patch("platform.platform")
    def test_slurm_config(self, platform_mocked: Mock, mock_global_defaults: Mock) -> None:

        logger = logging.getLogger()

        # Fake user-specified global values (for consistent unit tests)
        mock_global_defaults.return_value = {"qos": "dastest"}

        # Nested example
        experiment_dict = {
            "model_components": ["geos_atmosphere", "geos_ocean"],
            "slurm_directives_global": {
                "account": "x1234",
            },
            "slurm_directives_tasks": {
                "EvaObservations": {
                    "all": {
                        "account": "x5678",
                        "nodes": 2,
                        "ntasks-per-node": 4
                    },
                    "geos_atmosphere": {
                        "nodes": 4
                    }
                }
            }
        }

        platform_mocked.return_value = "Linux-4.12.14"
        # Platform-specific definitions and tests
        sd_discover = prepare_scheduling_dict(logger, experiment_dict,
                                              platform="nccs_discover")
        self.assertEqual(sd_discover["RunJediVariationalExecutable"]["directives"]["all"]
                         ["constraint"], "cas|sky")

        platform_mocked.return_value = "Linux-5.14.21"
        sd_discover_sles15 = prepare_scheduling_dict(logger, experiment_dict,
                                                     platform="nccs_discover_sles15")
        self.assertEqual(sd_discover_sles15["RunJediVariationalExecutable"]["directives"]
                         ["all"]["constraint"], "mil")
        self.assertEqual(sd_discover_sles15["RunJediVariationalExecutable"]["directives"]
                         ["all"]["qos"], "dastest")

        with self.assertRaises(AssertionError):
            prepare_scheduling_dict(logger, experiment_dict,
                                    platform="nccs_discover")

        # Platform generic tests
        for sd in [sd_discover, sd_discover_sles15]:
            for mc in ["all", "geos_atmosphere", "geos_ocean"]:
                # Hard-coded task-specific defaults
                self.assertEqual(sd["RunJediVariationalExecutable"]["directives"][mc]["nodes"], 3)
                self.assertEqual(sd["RunJediUfoTestsExecutable"]["directives"][mc]
                                 ["ntasks-per-node"], 1)
                # Global defaults from experiment dict
                self.assertEqual(sd["BuildJedi"]["directives"][mc]["account"], "x1234")
                self.assertEqual(sd["RunJediUfoTestsExecutable"]["directives"][mc]["account"],
                                 "x1234")
                # Task-specific, model-generic config
                self.assertEqual(sd["EvaObservations"]["directives"][mc]["account"], "x5678")
                self.assertEqual(sd["EvaObservations"]["directives"][mc]["ntasks-per-node"], 4)

            # Task-specific, model-specific configs
            self.assertEqual(sd["EvaObservations"]["directives"]["geos_ocean"]["nodes"], 2)
            self.assertEqual(sd["EvaObservations"]["directives"]["geos_atmosphere"]["nodes"], 4)

# --------------------------------------------------------------------------------------------------
