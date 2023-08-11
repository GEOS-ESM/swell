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

class Logger:

    def __init__(self, task_name):

        self.task_name = task_name

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

    def send_message(self, level, message, wrap):

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
            level_show = level_show+' '+self.task_name+': '

        if level == 'ABORT':
            task_name = under + self.task_name + end
            level_show = red + 'ABORT IN ' + end +task_name+': '

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

    def info(self, message, wrap=True):

        self.send_message('INFO', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def test(self, message, wrap=True):

        self.send_message('TEST', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def trace(self, message, wrap=True):

        self.send_message('TRACE', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def debug(self, message, wrap=True):

        self.send_message('DEBUG', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def blank(self, message, wrap=True):

        self.send_message('BLANK', message, wrap)

    # ----------------------------------------------------------------------------------------------

    def abort(self, message, wrap=True):

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

    def assert_abort(self, condition, message, wrap=True):

        if condition:
            return
        else:
            self.abort(message, wrap)

    # ----------------------------------------------------------------------------------------------

    def input(self, message):

        input(' '+self.task_name+': '+message + ". Press any key to continue...")

    # ----------------------------------------------------------------------------------------------
