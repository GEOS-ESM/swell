# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import TaskAttributes as ta

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

            # Clone GMAO_perllib
            CloneGmaoPerllib

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi

            {% for model_component in model_components %}
            # Clone location for generating observing system records
            CloneGeosMksi-{{model_component}}
            {% endfor %}
        """

        {% for cycle_time in cycle_times %}
        {% for model_component in model_components %}
        {{cycle_time.cycle_time}} = """
        {% if cycle_time[model_component] %}

            # Make sure GMAO_perllib, Mksi and JEDI are cloned and/or linked
            CloneGmaoPerllib[^] => GetBufr-{{model_component}}
            CloneGeosMksi-{{model_component}}[^] => GetBufr-{{model_component}}
            BuildJediByLinking[^]? | BuildJedi[^]  => BufrToIoda-{{model_component}}

            # Convert BUFR to ioda
            GetBufr-{{model_component}} => BufrToIoda-{{model_component}}
            BuildJediByLinking[^]? | BuildJedi[^]  => BufrToIoda-{{model_component}}

            # Clean up
            BufrToIoda-{{model_component}} => CleanCycle-{{model_component}}
        {% endif %}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''  # noqa

# --------------------------------------------------------------------------------------------------


class Workflow_convert_bufr(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        for task in self.tasks:
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        return workflow_str

    def set_tasks(self) -> list:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.BuildJedi())
        self.tasks.append(ta.CloneGmaoPerllib())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.CloneGeosMksi(model=model))
            self.tasks.append(ta.GetBufr(model=model))
            self.tasks.append(ta.BufrToIoda(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
