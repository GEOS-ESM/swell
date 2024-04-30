# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import os
import yaml

def prepare_scheduling_dict(logger, experiment_dict):
    # Hard-coded defaults
    # ----------------------------------------------
    global_defaults = {
        "account": "g0613",
        "qos": "allnccs",
        "partition": None,
        "constraint": "cas|sky"
    }

    task_defaults = {
        "RunJediVariationalExecutable": { "nodes": 3, "ntasks_per_node": 36},
        "RunJediUfoTestsExecutable": {"ntasks_per_node": 1}
    }

    # Global SLURM settings stored in $HOME/.swell/swell-slurm.yaml
    # ----------------------------------------------
    yaml_path = os.path.expanduser("~/.swell/swell-slurm.yaml")
    user_globals = {}
    if os.path.exists(yaml_path):
        logger.info(f"Loading SLURM user configuration from {yaml_path}")
        with open(yaml_path, "r") as yaml_file:
            user_globals = yaml.safe_load(yaml_file)

    # Global SLURM settings from experiment dict (questionary / overrides YAML)
    # ----------------------------------------------
    experiment_globals = {}
    if "slurm_directives_common" in experiment_dict:
        logger.info(f"Loading additional SLURM globals from experiment dict")
        experiment_globals = experiment_dict["slurm_directives_common"]

    # Task-specific SLURM settings from experiment dict (questionary / overrides YAML)
    # ----------------------------------------------
    experiment_task_directives = {}
    if "slurm_directives_tasks" in experiment_dict:
        logger.info(f"Loading experiment-specific SLURM configs from experiment dict")
        experiment_task_directives = experiment_dict["slurm_directives_tasks"]

    # List of tasks using slurm
    # -------------------------
    slurm_tasks = [
        'BuildJedi',
        'BuildGeos',
        'EvaObservations',
        'GenerateBClimatology',
        'RunJediHofxEnsembleExecutable',
        'RunJediHofxExecutable',
        'RunJediLocalEnsembleDaExecutable',
        'RunJediUfoTestsExecutable',
        'RunJediVariationalExecutable',
        'RunGeosExecutable',
        ]

    # Ap
    scheduling_dict = {}
    for slurm_task in slurm_tasks:
        # Priority order (first = highest priority)
            # 1. Task-specific directives from experiment (experiment_task_directives)
            # 2. Global directives from experiment (experiment_globals)
            # 3. Directives from user config (user_globals)
            # 4. Hard-coded task-specific defaults (task_defaults)
            # 5. Hard-coded global defaults (global_defaults)
        # NOTE: Hard-code "job-name" to SWELL task here...
        directives = {"job-name": slurm_task, **global_defaults, **user_globals, **experiment_globals}
        if slurm_task in task_defaults:
            directives = {**directives, **task_defaults[slurm_task]}
        if slurm_task in experiment_task_directives:
            directives = {**directives, **experiment_task_directives[slurm_task]}
        scheduling_dict[slurm_task]["directives"] = directives

    return scheduling_dict

# --------------------------------------------------------------------------------------------------
