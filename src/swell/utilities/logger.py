# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os


# --------------------------------------------------------------------------------------------------
#  @package logger
#
#  Class containing a logger for tasks.
#
# --------------------------------------------------------------------------------------------------

class Logger:

    def __init__(self, task_name):

        self.task_name = task_name

        # Set default logging levels
        self.loggerdict = {"INFO": True,
                           "TRACE": False,
                           "DEBUG": False}

        # Loop over logging levels
        for loglevel in self.loggerdict:

            # Check for environment variable e.g. LOG_TRACE=1 will activiate trace logging
            log_env = os.environ.get('LOG_'+loglevel)

            # If found set element to environment variable
            if log_env is not None:
                self.loggerdict[loglevel] = int(log_env) == 1

    # ----------------------------------------------------------------------------------------------

    def send_message(self, level, message):

        if self.loggerdict[level]:
            print(level+" "+self.task_name+": "+message)

    # ----------------------------------------------------------------------------------------------

    def info(self, message):

        self.send_message("INFO", message)

    # ----------------------------------------------------------------------------------------------

    def trace(self, message):

        self.send_message("TRACE", message)

    # ----------------------------------------------------------------------------------------------

    def debug(self, message):

        self.send_message("DEBUG", message)

    # ----------------------------------------------------------------------------------------------

    def abort(self, message):

        self.send_message("ABORT", message)
        sys.exit('ABORT\n')

    # ----------------------------------------------------------------------------------------------
