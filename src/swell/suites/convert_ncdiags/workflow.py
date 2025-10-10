# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for executing geos_atmosphere ObsFilters tests

# --------------------------------------------------------------------------------------------------

[scheduler]
    UTC mode = True
    allow implicit tasks = False

# --------------------------------------------------------------------------------------------------

[scheduling]

    initial cycle point = {{start_cycle_point}}
    final cycle point = {{final_cycle_point}}
    runahead limit = {{runahead_limit}}

    [[graph]]
        R1 = """
            # Triggers for non cycle time dependent tasks
            # -------------------------------------------
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """

            # Convert bias correction to ioda
            GetGsiBc
            GetGsiBc => GsiBcToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiBcToIoda

            # Convert ncdiags to ioda
            GetGsiNcdiag
            GetGsiNcdiag => GsiNcdiagToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiNcdiagToIoda

            # Clean up
            GsiNcdiagToIoda => CleanCycle
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------
'''

# --------------------------------------------------------------------------------------------------


class Workflow_convert_ncdiags(CylcWorkflow):

    def define_initial_workflow(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        return workflow_str

# --------------------------------------------------------------------------------------------------
