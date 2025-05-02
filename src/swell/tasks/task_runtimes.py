# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self
from collections.abc import Mapping
from enum import Enum, member
from dataclasses import dataclass

from swell.utilities.dataclass_utils import mutable_field
from swell.utilities.cylc_runtime import Task, Model, Cycling, Slurm

# --------------------------------------------------------------------------------------------------

class TaskRuntimes():

    @dataclass
    class root(Task):
        script: bool = False
        pre_script: str = "source $CYLC_SUITE_DEF_PATH/modules"
        environment: dict = mutable_field({'datetime': '$CYLC_TASK_CYCLE_POINT',
                             'config': '$CYLC_SUITE_DEF_PATH/experiment.yaml'})


    @dataclass
    class CloneJedi(Task):
        pass

    @dataclass
    class BuildJediByLinking(Task):
        pass

    @dataclass
    class BuildJedi(Slurm):
        time_limit: bool = True

    @dataclass
    class StageJedi(Model):
        pass

    @dataclass
    class StageJediCycle(Cycling, Model):
        pass

    @dataclass
    class GetBackground(Cycling, Model):
        pass

    @dataclass
    class GetObservations(Cycling, Model):
        pass

    @dataclass
    class GenerateBClimatology(Cycling, Model, Slurm):
        time_limit: bool = True

    @dataclass
    class GenerateBClimatologyByLinking(Cycling, Model):
        pass

    @dataclass
    class RunJediVariationalExecutable(Cycling, Model, Slurm):
        time_limit: bool = True

    @dataclass
    class EvaJediLog(Cycling, Model):
        pass

    @dataclass
    class EvaIncrement(Cycling, Model):
        pass

    @dataclass
    class EvaObservations(Cycling, Model, Slurm):
        time_limit: bool = True

    @dataclass
    class SaveObsDiags(Cycling, Model):
        pass

    @dataclass
    class CleanCycle(Cycling, Model):
        pass

    @classmethod
    def get(cls, name: str) -> Task:
        return getattr(cls, name)


# --------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    print(TaskRuntimes.get('RunJediVariationalExecutable')())
    r = TaskRuntimes.get('root')()
    print(r.pre_script)
