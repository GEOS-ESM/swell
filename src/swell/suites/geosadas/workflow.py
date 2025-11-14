# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.tasks.task_attributes import TaskAttributes as ta

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

[scheduler]
    UTC mode = True
    allow implicit tasks = False

# --------------------------------------------------------------------------------------------------

[scheduling]

    initial cycle point = 2020-12-15T00:00:00Z
    final cycle point = 2020-12-15T00:00:00Z

    [[graph]]
        R1 = """
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            BuildJediByLinking?

            # Stage JEDI static files
            CloneJedi => StageJedi

            # Clone geos ana for generating observing system records
            CloneGeosMksi
        """

        T00 = """
            # Generate satellite channel records
            CloneGeosMksi[^] => GenerateObservingSystemRecords

            # Get and convert bias correction coefficients
            GetGsiBc => GsiBcToIoda

            # Get and convert ncdiags
            GetGsiNcdiag => GsiNcdiagToIoda

            # Get background
            GetGeosAdasBackground

            # Run Jedi variational executable
            GenerateObservingSystemRecords => RunJediVariationalExecutable
            BuildJediByLinking[^]  => RunJediVariationalExecutable
            StageJedi[^] => RunJediVariationalExecutable
            GsiBcToIoda => RunJediVariationalExecutable
            GsiNcdiagToIoda => RunJediVariationalExecutable
            GetGeosAdasBackground => RunJediVariationalExecutable

            # Clean cycle
            RunJediVariationalExecutable => CleanCycle
        """

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''

# --------------------------------------------------------------------------------------------------


class Workflow_geosadas(CylcWorkflow):

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
        self.tasks.append(ta.CloneGeosMksi())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.StageJedi(model=model))
            self.tasks.append(ta.GetGsiBc(model=model))
            self.tasks.append(ta.GsiBcToIoda(model=model))
            self.tasks.append(ta.GetGsiNcdiag(model=model))
            self.tasks.append(ta.GsiNcdiagToIoda(model=model))
            self.tasks.append(ta.GetGeosAdasBackground(model=model))
            self.tasks.append(ta.RunJediVariationalExecutable(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
