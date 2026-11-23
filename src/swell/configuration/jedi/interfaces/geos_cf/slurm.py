# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

# GEOS-CF MPI layouts and SLURM resources as a function of the cube-sphere horizontal_resolution:
# the single source of truth for the forecast (RunForecast) and for the JEDI executions.
# swell.utilities.slurm calls task_scheduling() for every model component that provides this module.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

# Both tables have one entry per resolution, with the same fields:
#   nx, ny           MPI layout in x and y on each of the 6 cube faces, so that the number of MPI
#                    tasks is 6 * nx * ny
#   nodes            number of nodes requested
#   ntasks_per_node  MPI tasks per node; nodes * ntasks_per_node must be at least 6 * nx * ny
#   sbatch_time      wall time limit (HH:MM:SS)
# discover allocates whole nodes (Milan: 108 cores/node), so cores above ntasks_per_node are idle.
#
# Every field can be overridden per experiment, for the GCM and for JEDI, with the SLURM file given
# to 'swell create -s' through the key 'geos_cf_mpi'. The experiment has a single
# horizontal_resolution, so the overrides are keyed by component only and are merged over the table
# entry of that resolution (any subset of the fields can be given):
#   geos_cf_mpi:
#     gcm:  {nx: 36, ny: 24, nodes: 48, ntasks_per_node: 108, sbatch_time: '02:30:00'}
#     jedi: {nx: 8, ny: 8, nodes: 4, ntasks_per_node: 96, sbatch_time: '00:45:00'}

# GCM (AGCM.rc and gcm_run_geoscf.j): AGCM.rc takes the layout over the whole globe, NX x (6 * NY).
# Validated against real 12h (two 6h segment) background runs on discover: 6 * nx * ny always
# divides evenly into whole nodes of 108 tasks, which is the densest clean packing for each
# resolution. sbatch_time includes ~20-25% margin over the observed wall time of that validated run.
GCM_MPI = {
    'c90':  {'nx': 9,  'ny': 6,  'nodes': 3,  'ntasks_per_node': 108, 'sbatch_time': '01:30:00'},
    'c180': {'nx': 18, 'ny': 12, 'nodes': 12, 'ntasks_per_node': 108, 'sbatch_time': '01:40:00'},
    'c360': {'nx': 36, 'ny': 24, 'nodes': 48, 'ntasks_per_node': 108, 'sbatch_time': '02:15:00'},
}

# JEDI executions (variational, hofx): nx x ny is the 'layout' of the fv3-jedi geometry. nx and ny
# must divide the number of cells along a face edge (90/180/360). BUMP_NICAS files are specific to
# the geometry resolution and layout, and are staged from
# nicas/layout_<nx>x<ny>x6_<horizontal_resolution>.
# These are the layouts tested with standalone fv3jedi_var.x runs on discover.
JEDI_MPI = {
    'c90':  {'nx': 3, 'ny': 3, 'nodes': 1, 'ntasks_per_node': 54, 'sbatch_time': '00:30:00'},
    'c180': {'nx': 4, 'ny': 4, 'nodes': 1, 'ntasks_per_node': 96, 'sbatch_time': '00:30:00'},
    'c360': {'nx': 8, 'ny': 8, 'nodes': 4, 'ntasks_per_node': 96, 'sbatch_time': '00:30:00'},
}

# Fields of a table entry
FIELDS = ('nx', 'ny', 'nodes', 'ntasks_per_node', 'sbatch_time')

# Key of the experiment dictionary (from the 'swell create -s' file) holding the overrides
OVERRIDE_KEY = 'geos_cf_mpi'

# Number of cube faces
FACES = 6

# JEDI tasks that run on the layout defined in JEDI_MPI
JEDI_TASKS = ('RunJediVariationalExecutable', 'RunJediHofxExecutable')

# --------------------------------------------------------------------------------------------------


def validate_overrides(overrides: Mapping | None) -> None:
    """Raise ValueError if the geos_cf_mpi overrides have an unknown component or field."""

    for component, entry in (overrides or {}).items():
        if component not in ('gcm', 'jedi'):
            raise ValueError(f"{OVERRIDE_KEY}: unknown component '{component}'; use 'gcm' or "
                             f"'jedi'")
        unknown = set(entry or {}).difference(FIELDS)
        if unknown:
            raise ValueError(f"{OVERRIDE_KEY}: {component}: unknown fields {sorted(unknown)}; "
                             f"use {list(FIELDS)}")


# --------------------------------------------------------------------------------------------------


def mpi_settings(component: str, resolution: str, overrides: Mapping | None = None) -> dict:
    """Entry of GCM_MPI ('gcm') or JEDI_MPI ('jedi') for the resolution, with the experiment
    overrides (geos_cf_mpi) merged over it, and the derived number of MPI tasks ('ntasks')."""

    table = {'gcm': GCM_MPI, 'jedi': JEDI_MPI}[component]
    validate_overrides(overrides)
    override = (overrides or {}).get(component) or {}

    # A resolution that is not in the table is only usable if the override defines all the fields
    entry = {**table.get(resolution, {}), **override}
    missing = [field for field in FIELDS if field not in entry]
    if missing:
        raise ValueError(f'Unsupported horizontal resolution: {resolution}. Choose from: '
                         f'{list(table)}, or define {missing} for {component} in {OVERRIDE_KEY}')

    # nx and ny are per cube face: they must divide the cells along a face edge
    cells = int(resolution.lstrip('c'))
    if cells % entry['nx'] != 0 or cells % entry['ny'] != 0:
        raise ValueError(f'{component} {resolution}: nx={entry["nx"]} and ny={entry["ny"]} must '
                         f'divide {cells}')

    ntasks = FACES * entry['nx'] * entry['ny']
    capacity = entry['nodes'] * entry['ntasks_per_node']
    if ntasks > capacity:
        raise ValueError(f'{component} {resolution}: {ntasks} MPI tasks (6 * nx * ny) do not fit '
                         f'in {entry["nodes"]} nodes with {entry["ntasks_per_node"]} tasks per '
                         f'node ({capacity})')

    return {**entry, 'ntasks': ntasks}


# --------------------------------------------------------------------------------------------------


def task_scheduling(slurm_task: str, experiment_dict: Mapping) -> dict:
    """SLURM directives ('directives') and Cylc execution time limit ('execution_time_limit') that
    geos_cf sets for a task from the horizontal resolution of the experiment. Only the keys that
    apply to the task are returned; an empty dictionary if it is not resolution dependent."""

    resolution = experiment_dict.get('models', {}).get('geos_cf', {}).get('horizontal_resolution')
    if resolution is None or slurm_task not in ('RunForecast',) + JEDI_TASKS:
        return {}

    component = 'jedi' if slurm_task in JEDI_TASKS else 'gcm'
    settings = mpi_settings(component, resolution, experiment_dict.get(OVERRIDE_KEY))
    scheduling = {'directives': {'nodes': settings['nodes'],
                                 'ntasks-per-node': settings['ntasks_per_node']}}

    # The Cylc execution time limit is an ISO 8601 duration (e.g. PT30M); the forecast job sets
    # its own time limit in gcm_run_geoscf.j from sbatch_time.
    if component == 'jedi':
        hours, minutes, seconds = (int(t) for t in settings['sbatch_time'].split(':'))
        duration = ''.join(f'{value}{unit}' for value, unit in
                           ((hours, 'H'), (minutes, 'M'), (seconds, 'S')) if value)
        scheduling['execution_time_limit'] = f'PT{duration or "0S"}'

    return scheduling

# --------------------------------------------------------------------------------------------------
