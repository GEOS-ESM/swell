# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self
from collections.abc import Mapping
from enum import Enum, member

from swell.utilities.cylc_runtime import Task, Model, Cycling, Slurm

# --------------------------------------------------------------------------------------------------

class TaskRuntimes(Enum):

    @member
    class CloneJedi(Task):
        pass

    @member
    class BuildJediByLinking(Task):
        pass

    @member
    class BuildJedi(Slurm):
        time_limit: bool = True

    @member
    class StageJedi(Model):
        pass

    @member
    class StageJediCycle(Cycling, Model):
        pass

    @member
    class GetBackground(Cycling, Model):
        pass

    @member
    class GetObservations(Cycling, Model):
        pass

    @member
    class GenerateBClimatology(Cycling, Model, Slurm):
        time_limit: bool = True

    @member
    class GenerateBClimatologyByLinking(Cycling, Model):
        pass

    @member
    class RunJediVariationalExecutable(Cycling, Model, Slurm):
        time_limit: bool = True

    @member
    class EvaJediLog(Cycling, Model):
        pass

    @member
    class EvaIncrement(Cycling, Model):
        pass

    @member
    class EvaObservations(Cycling, Model, Slurm):
        time_limit: bool = True

    @member
    class SaveObsDiags(Cycling, Model):
        pass

    @member
    class CleanCycle(Cycling, Model):
        pass


# --------------------------------------------------------------------------------------------------