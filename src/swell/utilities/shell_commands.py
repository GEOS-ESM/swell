# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import stat
import subprocess


# --------------------------------------------------------------------------------------------------


def run_track_log_subprocess(logger, command, output_log=None):

    # Prepare output file
    # -------------------
    if output_log is not None:
        if os.path.exists(output_log):
            os.remove(output_log)
        output_log_h = open(output_log, 'w')
        logger.info(f'Output log (from run_and_track_subprocess) being written to: '
                         f'{output_log}')

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


def run_subprocess_dev_null(logger, command):

    run_subprocess(logger, command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------------------------------


def run_subprocess(logger, command, stdout=None, stderr=None):

    # Run subprocess
    try:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr)
    except subprocess.CalledProcessError as e:
        logger.abort('Subprocess with command {command} failed, throwing error \n{e}')


# --------------------------------------------------------------------------------------------------


def create_executable_file(logger, file_name, file_contents):

    # Write contents to file
    with open(os.path.join(file_name), "w") as file_name_open:
        file_name_open.write(file_contents)

    # Make file executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)


# --------------------------------------------------------------------------------------------------
