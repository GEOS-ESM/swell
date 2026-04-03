# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import logging

# --------------------------------------------------------------------------------------------------


class Logger(logging.Logger):

    # --------------------------------------------------------------------------------------------------

    def abort(self, msg: str,
              exception: Exception = Exception, *args, **kwargs) -> None:

        formatted_msg = '  Swell called ABORT: ' + msg

        super().critical(formatted_msg, *args, **kwargs)

        raise exception(msg)

    # ----------------------------------------------------------------------------------------------

    def assert_abort(self, condition: bool, msg: str) -> None:
        if condition:
            return
        else:
            self.abort(msg)

# --------------------------------------------------------------------------------------------------


def get_logger(name: str | None = None) -> Logger:
    '''
    Get a logger with custom message formatting for swell-related tasks.

    Set environment variable LOGLEVEL to specify level of detail,
    per logging:

    CRITICAL = 50
    FATAL =    50
    ERROR =    40
    WARNING =  30
    INFO =     20
    DEBUG =    10
    NOTSET =    0

    Any message with a level below the specified logger level will
    be ignored. By default the logger level is set to INFO.
    LOGLEVEL can be expressed as an integer value or the name
    associated with it.

    e.g. LOGLEVEL=10, or LOGLEVEL=DEBUG will activate debug messages

    Set LOGLEVEL=NOTSET to enable all messages
    '''
    if name is None:
        name = ''

    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    logging.setLoggerClass(Logger)

    logger = logging.Logger.manager.getLogger(name)

    log_level = os.environ.get('LOGLEVEL')
    if log_level is not None:
        logger.setLevel(log_level)

    return logger

# ----------------------------------------------------------------------------------------------
