# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import netCDF4 as nc
from typing import Optional

from swell.utilities.shell_commands import run_track_log_subprocess
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


def check_obs(
    path_to_observing_sys_yamls: Optional[str],
    observation: str,
    obs_dict: dict,
    cycle_time: Optional[str],
    input_and_output: Optional[bool] = False
) -> bool:

    use_observation = False

    # Check if observations in input file exists
    # ------------------------------------------
    filename = obs_dict['obs space']['obsdatain']['engine']['obsfile']

    if os.path.exists(filename):

        # Open file and check if number of location dimension is nonzero
        # --------------------------------------------------------------
        with nc.Dataset(filename, 'r') as dataset:
            for dim_name, dim in dataset.dimensions.items():
                if dim_name == 'Location' and dim.size > 0:
                    use_observation = True

    if input_and_output:

        # Check if observations in output file exists
        # ------------------------------------------
        filename = obs_dict['obs space']['obsdataout']['engine']['obsfile']
        if os.path.exists(filename):

            # Open file and check if number of location dimension is nonzero
            # --------------------------------------------------------------
            with nc.Dataset(filename, 'r') as dataset:

                for dim_name, dim in dataset.dimensions.items():
                    if dim_name == 'Location' and dim.size < 1:
                        print(f'IODA {observation} output has {dim.size} location dimension(s)')
                        use_observation = False

    return use_observation

# ----------------------------------------------------------------------------------------------


def run_executable(
    logger: Logger,
    cycle_dir: str,
    np: int,
    jedi_executable_path: str,
    jedi_config_file: str,
    output_log: str,
    perhost: Optional[int] = None
) -> None:

    # Run the JEDI executable
    # -----------------------
    persistent_job_id = os.environ.get('SWELL_PERSISTENT_JOB_ID')

    if perhost is None:
        logger.info(f"Running {jedi_executable_path} with {str(np)} processors.")
        if persistent_job_id:
            ntasks_per_node = os.environ.get('SWELL_SRUN_NTASKS_PER_NODE')
            nodes = os.environ.get('SWELL_SRUN_NODES')
            command = ['srun', '--jobid', persistent_job_id, '--exclusive', '-n', str(np)]
            if ntasks_per_node:
                command += ['--ntasks-per-node', ntasks_per_node]
            if nodes:
                command += ['--nodes', nodes]
            command += [jedi_executable_path, jedi_config_file]
        else:
            command = ['mpirun', '-np', str(np), jedi_executable_path, jedi_config_file]
    else:
        logger.info(
            f"Running {jedi_executable_path} with {str(np)} processors & perhost {str(perhost)}"
        )
        if persistent_job_id:
            nodes = os.environ.get('SWELL_SRUN_NODES') or (
                str(np // perhost) if np % perhost == 0 else None
            )
            command = ['srun', '--jobid', persistent_job_id, '--exclusive', '-n', str(np),
                       '--ntasks-per-node', str(perhost)]
            if nodes:
                command += ['--nodes', nodes]
            command += [jedi_executable_path, jedi_config_file]
        else:
            command = [
                'mpirun', '-np', str(np), '-perhost', str(perhost),
                jedi_executable_path, jedi_config_file
            ]
        s = ('mpi_command='+" ".join(command)+' '+output_log)
        logger.debug(s)

    # Run command
    # -----------
    run_track_log_subprocess(logger, command, output_log=output_log, cwd=cycle_dir)

# --------------------------------------------------------------------------------------------------
