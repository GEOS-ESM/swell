# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import textwrap
import logging
from typing import Optional

from swell.utilities.exceptions import ExceptionTypes

# --------------------------------------------------------------------------------------------------
#  @package logger
#
#  Class containing a logger for tasks.
#
# --------------------------------------------------------------------------------------------------


SwellError = ExceptionTypes.get_type('SwellError')

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

    def format_message(self, msg: str, wrap: bool, level: Optional[str] = None) -> str:
        # Wrap the message if needed
        if wrap:
            message_items = textwrap.wrap(msg, self.__maxlen__, break_long_words=True)
            for i in range(0, len(message_items)-1):
                message_items[i] = message_items[i] + ' ...\n'
        else:
            message_items = []
            message_items.append(msg)

        # Include level in the message
        level_show = ''
        if level != 'BLANK':
            level_show = level_show+' '+self.name+': '

        if level == 'ABORT':
            task_name = under + self.name + end
            level_show = red + 'ABORT IN ' + end + task_name + ': '

        color = end
        if level == 'ABORT':
            color = red

        msg = ''
        if level == 'ABORT':
            msg = '\n' + msg
        first_line = True
        for message_item in message_items:
            if not first_line:
                message_item = ' ' + color + message_item + end
            msg = msg + level_show + message_item
            first_line = False

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
        msg = self.format_message(msg, wrap, 'BLANK')
        super().info(msg, *args, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def debug(self, msg: str, wrap: bool = True, *args, **kwargs) -> None:
        msg = self.format_message(msg, wrap)
        super().debug(msg, *args, **kwargs)

    # ----------------------------------------------------------------------------------------------

    def abort(self, msg: str, wrap: bool = True, exception: Exception = SwellError, *args, **kwargs) -> None:
        formatted_msg = red + msg + end
        formatted_msg = self.format_message(formatted_msg, wrap, 'ABORT')
        super().critical(formatted_msg)

        raise exception(msg)

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
        logger.setLevel(log_level)

    return logger

# ----------------------------------------------------------------------------------------------
