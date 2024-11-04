# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import sys
import textwrap
import traceback
import logging
from typing import Optional


# --------------------------------------------------------------------------------------------------
#  @package logger
#
#  Class containing a logger for tasks.
#
# --------------------------------------------------------------------------------------------------


red = '\033[91m'
blue = '\033[94m'
cyan = '\033[96m'
green = '\033[92m'
end = '\033[0m'

under = '\033[4m'


# --------------------------------------------------------------------------------------------------


class Logger(logging.Logger):

    def __init__(self, name: Optional[str] = None, **kwargs) -> None:
        self.__maxlen__ = 100
        super().__init__(name, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def format_message(self, msg: str, wrap: bool = True, lead_with_name: bool = True) -> str:
        if wrap:
            msg_items = textwrap.wrap(msg, self.__maxlen__, break_long_words=True)
            if len(msg_items) == 0:
                msg_items = [' ']
            for i in range(0, len(msg_items)-1):
                msg_items[i] = msg_items[i] + '...\n'
            if lead_with_name:
                for i in range(0, len(msg_items)):
                    msg_items[i] = self.name + ': ' + msg_items[i]

            msg = ''
            for msg_item in msg_items:
                msg = msg + ' ' + msg_item

        elif lead_with_name:
            msg = ' ' + self.name + ': ' + msg
        return msg

    # ----------------------------------------------------------------------------------------------

    def critical(self, msg: str, wrap: bool = True, *args, **kwargs) -> None:
        msg = self.format_message(msg, wrap)
        super().critical(msg, *args, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def error(self, msg: str, wrap: bool = True, *args, **kwargs) -> None:
        msg = self.format_message(msg, wrap)
        super().error(msg, **args, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def info(self, msg: str, wrap: bool = True, *args, **kwargs) -> None:
        msg = self.format_message(msg, wrap)
        super().info(msg, *args, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def blank(self, msg: str, wrap: bool = True, *args, **kwargs) -> None:
        # blank has severity of INFO, does not output task name
        msg = self.format_message(msg, wrap, False)
        super().info(msg, *args, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def debug(self, msg: str, wrap: bool = True, *args, **kwargs) -> None:
        msg = self.format_message(msg, wrap)
        super().debug(msg, *args, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def abort(self, msg: str, wrap: bool = True, *args, **kwargs) -> None:
        msg = self.format_message(msg, wrap, False)
        msg = red + msg + end
        msg = red + 'ABORT IN ' + end + under + self.name + end + ': ' + msg
        super().critical(msg)

        # Get traceback stack (without logger.py lines)
        filtered_stack = [line for line in traceback.format_stack() if 'logger.py' not in line]

        # Remove everything after 'logger.assert_abort' in last element of filtered_stack
        filtered_stack[-1] = filtered_stack[-1].split('logger.assert_abort')[0]

        traceback_str = '\n'.join(filtered_stack)

        # Log traceback and exit
        super().error('\nHERE IS THE TRACEBACK: \n----------------------\n\n' + traceback_str)
        sys.exit()

    # ----------------------------------------------------------------------------------------------

    def assert_abort(self, condition: bool, msg: str) -> None:
        if condition:
            return
        else:
            self.abort(msg)

# --------------------------------------------------------------------------------------------------


def get_logger(name: Optional[str] = None) -> Logger:
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

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.setLoggerClass(Logger)

    logger = logging.Logger.manager.getLogger(name)

    log_level = os.environ.get('LOGLEVEL')
    if log_level is not None:
        logging.setLevel(log_level)

    return logger

# ----------------------------------------------------------------------------------------------
