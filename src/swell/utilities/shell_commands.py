# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import stat
import subprocess

from typing import Union


# --------------------------------------------------------------------------------------------------


def run_track_log_subprocess(
    logger: 'Logger',
    command: str,
    output_log: Union[str, None] = None
) -> None:

    # Prepare output file
    # -------------------
    if output_log is not None:
        if os.path.exists(output_log):
            os.remove(output_log)
        output_log_h = open(output_log, 'w')
        logger.info(f'Output log (from run_and_track_subprocess) being written to: {output_log}')

    # Run commands and print output to screen
    # ---------------------------------------
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline().decode()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Write line of output to screen for tailing
            print(output.strip())
            # Write line of output to file
            if output_log is not None:
                output_log_h.write(f'{output.strip()}\n')

    # Close the log file
    # ------------------
    if output_log is not None:
        output_log_h.close()

    # Abort task if the command did not run successfully
    # --------------------------------------------------
    rc = process.poll()
    if rc != 0:
        command_string = ' '.join(command)
        logger.abort(f'In run_and_track_subprocess command ' + command_string +
                     f' failed to execute.', False)


# --------------------------------------------------------------------------------------------------


def run_subprocess_dev_null(
    logger: 'Logger',
    command: str
) -> None:

    run_subprocess(logger, command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------------------------------


def run_subprocess(
    logger: 'Logger',
    command: str,
    stdout: Union[str, None] = None,
    stderr: Union[str, None] = None
) -> None:

    # Run subprocess
    try:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr)
    except subprocess.CalledProcessError as e:
        print(e)
        logger.abort(f'Subprocess with command {command} failed, throwing error {e}')


# --------------------------------------------------------------------------------------------------


def create_executable_file(logger: 'Logger', file_name: str, file_contents: str) -> None:

    # Write contents to file
    with open(os.path.join(file_name), "w") as file_name_open:
        file_name_open.write(file_contents)

    # Make file executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)


# --------------------------------------------------------------------------------------------------
