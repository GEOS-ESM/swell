# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import yaml

from swell.utilities.cylc_workflow import CylcWorkflow
from swell.utilities.cylc_formatting import indent_lines

# --------------------------------------------------------------------------------------------------


class Workflow_build_geos(CylcWorkflow):
    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for building the GEOS model
        """)

        return description

    # --------------------------------------------------------------------------------------------------

    def define_scheduler(self) -> str:
        scheduler_str = 'allow implicit tasks = False\n'

        settings_file = os.path.expanduser(os.path.join('~', '.swell', 'swell-settings.yaml'))
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings_dict = yaml.safe_load(f)
            if 'email_address' in settings_dict.keys():
                email_address = settings_dict['email_address']

                message_str = "{% if environ['SWELL_SEND_MESSAGES'] %}\n"
                message_str += '[[events]]\n'
                message_str += indent_lines('mail events = startup, shutdown\n', 1)
                message_str += '[[mail]]\n'
                message_str += indent_lines(f'to = {email_address}\n', 1)
                message_str += '{% endif %}\n'

                scheduler_str += message_str

        scheduler = self.create_new_section('scheduler', scheduler_str)

        return scheduler.get_section_str()

    # --------------------------------------------------------------------------------------------------

    def define_scheduling_section(self):
        scheduling_section = self.create_new_section('scheduling', '')

        return scheduling_section

    # --------------------------------------------------------------------------------------------------

    def define_graph_section(self):
        # Define the string of the graph section
        graph_str = ''

        # Define the string for the R1 (first non-cycling) section
        r1 = """
            CloneGeos => BuildGeosByLinking?

            BuildGeosByLinking:fail? => BuildGeos
            """

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
