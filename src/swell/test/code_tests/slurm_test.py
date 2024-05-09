# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import unittest
import logging

from swell.utilities.slurm import prepare_scheduling_dict

# --------------------------------------------------------------------------------------------------

class SLURMConfigTest(unittest.TestCase):

    def test_slurm_config(self):

        logger = logging.getLogger()

        # Nested example
        experiment_dict = {
            "model_components": ["geos_atmosphere", "geos_ocean"],
            "slurm_directives_globals": {
                "account": "x1234",
                "nodes": 1
            },
            "slurm_directives_tasks": {
                "EvaObservations": {
                    "all": {
                        "account": "x5678",
                        "nodes": 2,
                        "ntasks_per_node": 4
                    },
                    "geos_atmosphere": {
                        "nodes": 4
                    }
                }
            }
        }

        sd = prepare_scheduling_dict(logger, experiment_dict)

        for mc in ["all", "geos_atmosphere", "geos_ocean"]:
            # Hard-coded global defaults
            assert sd["BuildJedi"]["directives"][mc]["account"] == "g0613"
            assert sd["EvaObservations"]["directives"][mc]["qos"] == "allnccs"
            assert sd["EvaObservations"]["directives"][mc]["constraint"] == "cas|sky"
            # Hard-coded task-specific defaults
            assert sd["RunJediVariationalExecutable"]["directives"][mc]["nodes"] == 3
            assert sd["RunJediVariationalExecutable"]["directives"][mc]["ntasks_per_node"] == 36
            assert sd["RunJediUfoTestsExecutable"]["directives"][mc]["ntasks_per_node"] == 1
            # Global defaults from experiment dict
            assert sd["BuildJedi"]["directives"][mc]["account"] == "x1234"
            assert sd["RunJediUfoTestsExecutable"]["directives"][mc]["account"] == "x1234"
            # Task-specific, model-generic config
            assert sd["EvaObservations"]["directives"][mc]["account"] == "x5678"
            assert sd["EvaObservations"]["directives"][mc]["ntasks_per_node"] == 4

        # Task-specific, model-specific configs
        assert sd["EvaObservations"]["directives"]["geos_ocean"]["nodes"] == 2
        assert sd["EvaObservations"]["directives"]["geos_atmosphere"]["nodes"] == 4

# --------------------------------------------------------------------------------------------------
