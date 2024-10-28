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

    def __init__(self, task_name: str) -> None:
        super().__init__(task_name)

        self.name = task_name

        # Maximum length of lines
        self.__maxlen__ = 100

        # Set default logging levels
        self.loggerdict = {'BLANK': True,
                           'INFO': True,
                           'TEST': True,
                           'TRACE': False,
                           'DEBUG': False, }

        # Loop over logging levels
        for loglevel in self.loggerdict:

            # Check for environment variable e.g. LOG_TRACE=1 will activiate trace logging
            log_env = os.environ.get('LOG_'+loglevel)

            # If found set element to environment variable
            if log_env is not None:
                self.loggerdict[loglevel] = int(log_env) == 1

    # ----------------------------------------------------------------------------------------------

    def send_message(self, level: str, message: str, wrap: bool) -> None:

        # Wrap the message if needed
        if wrap:
            message_items = textwrap.wrap(message, self.__maxlen__, break_long_words=True)
            for i in range(0, len(message_items)-1):
                message_items[i] = message_items[i] + ' ...'
        else:
            message_items = []
            message_items.append(message)

        # Include level in the message
        level_show = ''
        if level != 'BLANK':
            level_show = level_show+' '+self.name+': '

        if level == 'ABORT':
            name = under + self.name + end
            level_show = red + 'ABORT IN ' + end + name+': '

        color = end
        if level == 'ABORT':
            color = red

        if level == 'ABORT' or self.loggerdict[level]:
            if level == 'ABORT':
                print('\n')
            first_line = True
            for message_item in message_items:
                if not first_line:
                    message_item = ' ' + color + message_item + end
                print(level_show+message_item)
                first_line = False

    # ----------------------------------------------------------------------------------------------

    def info(self, message: str, wrap: bool = True) -> None:

        self.send_message('INFO', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def test(self, message: str, wrap: bool = True) -> None:

        self.send_message('TEST', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def trace(self, message: str, wrap: bool = True) -> None:

        self.send_message('TRACE', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def debug(self, message: str, wrap: bool = True) -> None:

        self.send_message('DEBUG', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def blank(self, message: str, wrap: bool = True) -> None:

        self.send_message('BLANK', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def abort(self, message: str, wrap: bool = True) -> None:

        # Make the text red
        message = red + message + end

        self.send_message('ABORT', message, wrap)

        # Get traceback stack (without logger.py lines)
        filtered_stack = [line for line in traceback.format_stack() if 'logger.py' not in line]

        # Remove everything after 'logger.assert_abort' in last element of filtered_stack
        filtered_stack[-1] = filtered_stack[-1].split('logger.assert_abort')[0]

        traceback_str = '\n'.join(filtered_stack)

        # Exit with traceback
        sys.exit('\nHERE IS THE TRACEBACK: \n----------------------\n\n' + traceback_str)

    # ----------------------------------------------------------------------------------------------

    def assert_abort(self, condition: bool, message: str, wrap: bool = True) -> None:

        if condition:
            return
        else:
            self.abort(message, wrap)

    # ----------------------------------------------------------------------------------------------

    def input(self, message: str) -> None:

        input(' '+self.name+': '+message + ". Press any key to continue...")

# ----------------------------------------------------------------------------------------------


class LoggingManager(logging.Manager):
    # Override manager from logging so it uses custom swell Logger class
    def __init__(self, rootnode):
        super().__init__(rootnode)
        self.loggerClass = Logger


# --------------------------------------------------------------------------------------------------

def get_logger(name: Optional[str] = None):
    # Construct logger object in the same way as base logging instance
    WARNING = 30
    root = logging.RootLogger(WARNING)
    manager = LoggingManager(root)

    if name is None:
        name = ''

    if isinstance(name, str) and name == root.name:
        return root
    return manager.getLogger(name)
