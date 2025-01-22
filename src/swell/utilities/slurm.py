# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import importlib
import os
import platform as pltfrm
import re
import yaml
from typing import Union

from importlib import resources
from logging import Logger as pyLogger

from swell.utilities.logger import Logger


def prepare_scheduling_dict(
    logger: Union[Logger, pyLogger],
    experiment_dict: dict,
    platform: str,
) -> dict:

    # Obtain platform-specific SLURM directives and set them as global defaults
    # Start by constructing the full platforms path
    # -------------------------------------------
    platform_path = f"swell.deployment.platforms.{platform}"

    # Import the path dynamically
    # ------------------------------
    try:
        path_import = importlib.import_module(platform_path)
    except ModuleNotFoundError:
        raise Exception(f"Platform '{platform}' has not been configured in SWELL")
    except Exception as err:
        raise err

    logger.info(f'Loading SLURM user configuration for the "{platform}" platform')
    with resources.open_text(path_import, 'slurm.yaml') as yaml_file:
        global_defaults = yaml.safe_load(yaml_file)

    # Hard-coded SLURM defaults for certain tasks
    # -------------------------------------------
    task_defaults = {
        "RunJediVariationalExecutable": {"all": {"nodes": 3}},
        "RunJediUfoTestsExecutable": {"all": {"ntasks-per-node": 1}},
        "RunJediConvertStateSoca2ciceExecutable": {"all": {"nodes": 1}}
    }

    # Global SLURM settings stored in $HOME/.swell/swell-slurm.yaml
    # ----------------------------------------------
    # NOTE: Separate function to allow it to be mocked in unit tests.
    # See https://github.com/GEOS-ESM/swell/issues/351
    user_globals = slurm_global_defaults(logger)

    # Check if platform contains Linux-5.14.21, which indicates platform is SLES15
    if 'Linux-4.12.14' in pltfrm.platform():
        assert platform == "nccs_discover", (
            "'Linux-4.12.14' detected, which implies platform 'nccs_discover. " +
            f"That is inconsistent with user-specified platform '{platform}'."
        )

    # Global SLURM settings from experiment dict (questionary / overrides YAML)
    # ----------------------------------------------
    experiment_globals = {}
    if "slurm_directives_global" in experiment_dict:
        logger.info(f"Loading additional SLURM globals from experiment dict")
        experiment_globals = experiment_dict["slurm_directives_global"]

    # Task-specific SLURM settings from experiment dict (questionary / overrides YAML)
    # ----------------------------------------------
    experiment_task_directives = {}
    if "slurm_directives_tasks" in experiment_dict:
        logger.info(f"Loading experiment-specific SLURM configs from experiment dict")
        experiment_task_directives = experiment_dict["slurm_directives_tasks"]

    # List of tasks using slurm
    # -------------------------
    slurm_tasks = {
        'BuildJedi',
        'BuildGeos',
        'EvaObservations',
        'GenerateBClimatology',
        'RunJediEnsembleMeanVariance',
        'RunJediConvertStateSoca2ciceExecutable',
        'RunJediFgatExecutable',
        'RunJediHofxEnsembleExecutable',
        'RunJediHofxExecutable',
        'RunJediLocalEnsembleDaExecutable',
        'RunJediObsfiltersExecutable',
        'RunJediUfoTestsExecutable',
        'RunJediVariationalExecutable',
        'RunGeosExecutable'
        }

    # Throw an error if a user tries to set SLURM directives for a task that
    # doesn't use SLURM.
    experiment_slurm_tasks = set(experiment_task_directives.keys())
    non_slurm_tasks = experiment_slurm_tasks.difference(slurm_tasks)
    assert len(non_slurm_tasks) == 0, \
        f"The following tasks cannot use SLURM: {non_slurm_tasks}"

    model_components = experiment_dict["model_components"] \
        if "model_components" in experiment_dict \
        else []

    scheduling_dict = {}
    for slurm_task in slurm_tasks:
        # Priority order (first = highest priority)
        # 1. Task-specific directives from experiment
        #    (experiment_task_directives[slurm_task]["all"])
        # 2. Global directives from experiment (experiment_globals)
        # 3. Directives from user config (user_globals)
        # 4. Hard-coded task-specific defaults (task_defaults)
        # 5. Hard-coded global defaults (global_defaults)
        # NOTE: Hard-code "job-name" to SWELL task here but it can be
        # overwritten in task-specific directives.
        directives = {
            "job-name": slurm_task,
            **global_defaults,
            **user_globals,
            **experiment_globals
        }
        if slurm_task in task_defaults:
            if "all" in task_defaults[slurm_task]:
                directives = {
                    **directives,
                    **task_defaults[slurm_task]["all"]
                }
        if slurm_task in experiment_task_directives:
            if "all" in experiment_task_directives[slurm_task]:
                directives = {
                    **directives,
                    **experiment_task_directives[slurm_task]["all"]
                }
        # Set model_agnostic directives
        validate_directives(directives)
        scheduling_dict[slurm_task] = {"directives": {"all": directives}}

        # Now, add model component-specific logic. The inheritance here is more
        # complicated:
        # - Experiment global defaults (`experiment_globals`)
        # - User global defaults (`user_globals`)
        # - Task- and model-specific hard-coded defaults
        # - Task-specific, model-generic hard-coded defaults
        # - Global hard-coded defaults
        # Now, for every model component, set the model-generic directives
        # (`directives`) but overwrite with model-specific directives if
        # present.
        for model_component in model_components:
            model_directives = {
                "job-name": f"{slurm_task}-{model_component}",
                **global_defaults
            }
            if slurm_task in task_defaults:
                model_directives = add_directives(
                    model_directives,
                    task_defaults[slurm_task],
                    "all"
                )
                model_directives = add_directives(
                    model_directives,
                    task_defaults[slurm_task],
                    model_component
                )
            model_directives = {
                **model_directives,
                **user_globals,
                **experiment_globals
            }
            if slurm_task in experiment_task_directives:
                model_directives = add_directives(
                    model_directives,
                    experiment_task_directives[slurm_task],
                    "all"
                )
                model_directives = add_directives(
                    model_directives,
                    experiment_task_directives[slurm_task],
                    model_component
                )
            validate_directives(model_directives)
            scheduling_dict[slurm_task]["directives"][model_component] = model_directives

    return scheduling_dict


def add_directives(target_dict: dict, input_dict: dict, key: str) -> dict:
    if key in input_dict:
        return {
            **target_dict,
            **input_dict[key]
        }
    else:
        return target_dict


def validate_directives(directive_dict: dict) -> None:
    directive_pattern = r'(?<=--)[a-zA-Z-]+'
    # Parse sbatch docs and extract all directives (e.g., `--account`)
    directive_list = {
        re.search(directive_pattern, s).group(0)
        for s in man_sbatch.split("\n")
        if re.search(directive_pattern, s)
    }
    # Make sure that everything in `directive_dict` is in `directive_list`;
    # i.e., that all entries are valid slurm directives.
    invalid_directives = set(directive_dict.keys()).difference(directive_list)
    assert \
        len(invalid_directives) == 0, \
        f"The following are invalid SLURM directives: {invalid_directives}"


def slurm_global_defaults(
    logger: Union[Logger, pyLogger],
    yaml_path: str = "~/.swell/swell-slurm.yaml"
) -> dict:
    yaml_path = os.path.expanduser(yaml_path)
    user_globals = {}
    if os.path.exists(yaml_path):
        logger.info(f"Loading SLURM user configuration from {yaml_path}")
        with open(yaml_path, "r") as yaml_file:
            user_globals = yaml.safe_load(yaml_file)
    return user_globals


man_sbatch = """
Parallel run options:
  -a, --array=indexes         job array index values
  -A, --account=name          charge job to specified account
      --bb=<spec>             burst buffer specifications
      --bbf=<file_name>       burst buffer specification file
  -b, --begin=time            defer job until HH:MM MM/DD/YY
      --comment=name          arbitrary comment
      --cpu-freq=min[-max[:gov]] requested cpu frequency (and governor)
  -c, --cpus-per-task=ncpus   number of cpus required per task
  -d, --dependency=type:jobid[:time] defer job until condition on jobid is satisfied
      --deadline=time         remove the job if no ending possible before
                              this deadline (start > (deadline - time[-min]))
      --delay-boot=mins       delay boot for desired node features
  -D, --chdir=directory       set working directory for batch script
  -e, --error=err             file for batch script's standard error
      --export[=names]        specify environment variables to export
      --export-file=file|fd   specify environment variables file or file
                              descriptor to export
      --get-user-env          load environment from local cluster
      --gid=group_id          group ID to run job as (user root only)
      --gres=list             required generic resources
      --gres-flags=opts       flags related to GRES management
  -H, --hold                  submit job in held state
      --ignore-pbs            Ignore #PBS and #BSUB options in the batch script
  -i, --input=in              file for batch script's standard input
  -J, --job-name=jobname      name of job
  -k, --no-kill               do not kill job on node failure
  -L, --licenses=names        required license, comma separated
  -M, --clusters=names        Comma separated list of clusters to issue
                              commands to.  Default is current cluster.
                              Name of 'all' will submit to run on all clusters.
                              NOTE: SlurmDBD must up.
      --container             Path to OCI container bundle
  -m, --distribution=type     distribution method for processes to nodes
                              (type = block|cyclic|arbitrary)
      --mail-type=type        notify on state change: BEGIN, END, FAIL or ALL
      --mail-user=user        who to send email notification for job state
                              changes
      --mcs-label=mcs         mcs label if mcs plugin mcs/group is used
  -n, --ntasks=ntasks         number of tasks to run
      --nice[=value]          decrease scheduling priority by value
      --no-requeue            if set, do not permit the job to be requeued
      --ntasks-per-node=n     number of tasks to invoke on each node
  -N, --nodes=N               number of nodes on which to run (N = min[-max])
  -o, --output=out            file for batch script's standard output
  -O, --overcommit            overcommit resources
  -p, --partition=partition   partition requested
      --parsable              outputs only the jobid and cluster name (if present),
                              separated by semicolon, only on successful submission.
      --power=flags           power management options
      --priority=value        set the priority of the job to value
      --profile=value         enable acct_gather_profile for detailed data
                              value is all or none or any combination of
                              energy, lustre, network or task
      --propagate[=rlimits]   propagate all [or specific list of] rlimits
  -q, --qos=qos               quality of service
  -Q, --quiet                 quiet mode (suppress informational messages)
      --reboot                reboot compute nodes before starting job
      --requeue               if set, permit the job to be requeued
  -s, --oversubscribe         over subscribe resources with other jobs
  -S, --core-spec=cores       count of reserved cores
      --signal=[[R][B]:]num[@time] send signal when time limit within time seconds
      --spread-job            spread job across as many nodes as possible
      --switches=max-switches{@max-time-to-wait}
                              Optimum switches and max time to wait for optimum
      --thread-spec=threads   count of reserved threads
  -t, --time=minutes          time limit
      --time-min=minutes      minimum time limit (if distinct)
      --uid=user_id           user ID to run job as (user root only)
      --use-min-nodes         if a range of node counts is given, prefer the
                              smaller count
  -v, --verbose               verbose mode (multiple -v's increase verbosity)
  -W, --wait                  wait for completion of submitted job
      --wckey=wckey           wckey to run job under
      --wrap[=command string] wrap command string in a sh script and submit

Constraint options:
      --cluster-constraint=[!]list specify a list of cluster constraints
      --contiguous            demand a contiguous range of nodes
  -C, --constraint=list       specify a list of constraints
  -F, --nodefile=filename     request a specific list of hosts
      --mem=MB                minimum amount of real memory
      --mincpus=n             minimum number of logical processors (threads)
                              per node
      --reservation=name      allocate resources from named reservation
      --tmp=MB                minimum amount of temporary disk
  -w, --nodelist=hosts...     request a specific list of hosts
  -x, --exclude=hosts...      exclude a specific list of hosts

Consumable resources related options:
      --exclusive[=user]      allocate nodes in exclusive mode when
                              cpu consumable resource is enabled
      --exclusive[=mcs]       allocate nodes in exclusive mode when
                              cpu consumable resource is enabled
                              and mcs plugin is enabled
      --mem-per-cpu=MB        maximum amount of real memory per allocated
                              cpu required by the job.
                              --mem >= --mem-per-cpu if --mem is specified.

Affinity/Multi-core options: (when the task/affinity plugin is enabled)
                              For the following 4 options, you are
                              specifying the minimum resources available for
                              the node(s) allocated to the job.
      --sockets-per-node=S    number of sockets per node to allocate
      --cores-per-socket=C    number of cores per socket to allocate
      --threads-per-core=T    number of threads per core to allocate
  -B  --extra-node-info=S[:C[:T]]  combine request of sockets per node,
                              cores per socket and threads per core.
                              Specify an asterisk (*) as a placeholder,
                              a minimum value, or a min-max range.

      --ntasks-per-core=n     number of tasks to invoke on each core
      --ntasks-per-socket=n   number of tasks to invoke on each socket
      --hint=                 Bind tasks according to application hints
                              (see "--hint=help" for options)
      --mem-bind=             Bind memory to locality domains (ldom)
                              (see "--mem-bind=help" for options)

GPU scheduling options:
      --cpus-per-gpu=n        number of CPUs required per allocated GPU
  -G, --gpus=n                count of GPUs required for the job
      --gpu-bind=...          task to gpu binding options
      --gpu-freq=...          frequency and voltage of GPUs
      --gpus-per-node=n       number of GPUs required per allocated node
      --gpus-per-socket=n     number of GPUs required per allocated socket
      --gpus-per-task=n       number of GPUs required per spawned task
      --mem-per-gpu=n         real memory required per allocated GPU

Help options:
  -h, --help                  show this help message
      --usage                 display brief usage message

Other options:
  -V, --version               output version information and exit
"""

# --------------------------------------------------------------------------------------------------
