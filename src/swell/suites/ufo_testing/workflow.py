# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.tasks.task_runtimes import TaskRuntimes as tr

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

            # Clone geos ana for generating observing system records
            CloneGeosMksi
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """

            # Generate satellite channel records
            CloneGeosMksi[^] => GenerateObservingSystemRecords

            # Convert bias correction to ioda
            GetGsiBc
            GetGsiBc => GsiBcToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiBcToIoda

            # Convert ncdiags to ioda
            GetGsiNcdiag
            GetGsiNcdiag => GsiNcdiagToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiNcdiagToIoda

            GetGeovals

            # Run Jedi hofx executable
            GenerateObservingSystemRecords => RunJediUfoTestsExecutable
            GsiNcdiagToIoda => RunJediUfoTestsExecutable
            GsiBcToIoda => RunJediUfoTestsExecutable
            GetGeovals => RunJediUfoTestsExecutable

            # EvaObservations
            RunJediUfoTestsExecutable => EvaObservations

            # Clean up large files
            EvaObservations => CleanCycle

        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------
'''

# --------------------------------------------------------------------------------------------------


class Workflow_ufo_testing(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)
        
        for task in self.tasks():
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        return workflow_str
    
    def tasks(self) -> list:
        tasks = []
        tasks.append(tr.root())
        tasks.append(tr.CloneJedi())
        tasks.append(tr.BuildJedi())
        tasks.append(tr.BuildJediByLinking())

        for model in self.experiment_dict['model_components']:
            tasks.append(tr.CloneGeosMksi(model=model))
            tasks.append(tr.GenerateObservingSystemRecords(model=model))
            tasks.append(tr.GetGsiBc(model=model))
            tasks.append(tr.GsiBcToIoda(model=model))
            tasks.append(tr.GetGsiNcdiag(model=model))
            tasks.append(tr.GsiNcdiagToIoda(model=model))
            tasks.append(tr.RunJediUfoTestsExecutable(model=model))
            tasks.append(tr.GetGeovals(model=model))
            tasks.append(tr.EvaObservations(model=model))
            tasks.append(tr.CleanCycle(model=model))
        
        return tasks

# --------------------------------------------------------------------------------------------------
