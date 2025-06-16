# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import unittest

from swell.utilities.slurm import prepare_slurm_defaults_and_overrides
from swell.utilities.logger import get_logger
from swell.tasks.task_runtimes import TaskRuntimes
from unittest.mock import patch, Mock

# --------------------------------------------------------------------------------------------------


class SLURMConfigTest(unittest.TestCase):

    # Mock the `slurm_global_directives` function to ignore "real"
    # configuration and platform-specific settings
    @patch("swell.utilities.slurm.slurm_global_defaults")
    @patch("platform.platform")
    def test_slurm_config(self, platform_mocked: Mock, mock_global_defaults: Mock) -> None:

        logger = get_logger()

        # Fake user-specified global values (for consistent unit tests)
        mock_global_defaults.return_value = {"qos": "dastest"}

        # Nested example
        experiment_dict = {
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

        platform_mocked.return_value = "Linux-5.14.21"
        sd_discover_sles15 = prepare_slurm_defaults_and_overrides(logger, 'nccs_discover_sles15',
                                                                  experiment_dict)

        run_jedi_var_class = TaskRuntimes.get('RunJediVariationalExecutable')
        run_jedi_var_obj = run_jedi_var_class()
        run_jedi_var_slurm = run_jedi_var_obj.generate_task_slurm_dict(
                sd_discover_sles15, 'nccs_discover_sles15')

        self.assertEqual(run_jedi_var_slurm["constraint"], "mil")
        self.assertEqual(run_jedi_var_slurm["qos"], "dastest")

        eva_obs_class = TaskRuntimes.get('EvaObservations')
        build_jedi_class = TaskRuntimes.get('BuildJedi')
        run_jedi_ufo_class = TaskRuntimes.get('RunJediUfoExecutable')

        # Platform generic tests
        for sd in [sd_discover_sles15]:
            for mc in ["all", "geos_atmosphere", "geos_marine"]:
                run_jedi_var_obj = run_jedi_var_class(model=mc)
                eva_obs_obj = eva_obs_class(model=mc)
                build_jedi_obj = build_jedi_class(model=mc)
                run_jedi_ufo_obj = run_jedi_ufo_class(model=mc)

                run_jedi_var_dict = run_jedi_var_obj.generate_task_slurm_dict(
                        sd, 'nccs_discover_sles15')
                eva_obs_dict = eva_obs_obj.generate_task_slurm_dict(
                        sd, 'nccs_discover_sles15')
                build_jedi_dict = build_jedi_obj.generate_task_slurm_dict(
                        sd, 'nccs_discover_sles15')
                run_jedi_ufo_dict = run_jedi_ufo_obj.generate_task_slurm_dict(
                        sd, 'nccs_discover_sles15')

                # Hard-coded task-specific defaults
                self.assertEqual(run_jedi_var_dict["nodes"], 3)
                self.assertEqual(run_jedi_ufo_dict["ntasks-per-node"], 1)
                # Global defaults from experiment dict
                self.assertEqual(build_jedi_dict["account"], "x1234")
                self.assertEqual(run_jedi_ufo_dict["account"], "x1234")
                # Task-specific, model-generic config
                self.assertEqual(eva_obs_dict["account"], "x5678")
                self.assertEqual(eva_obs_dict["ntasks-per-node"], 4)

            # Task-specific, model-specific configs
            if mc == "geos_marine":
                self.assertEqual(eva_obs_dict["nodes"], 2)
            if mc == "geos_atmosphere":
                self.assertEqual(eva_obs_dict["nodes"], 4)

# --------------------------------------------------------------------------------------------------
