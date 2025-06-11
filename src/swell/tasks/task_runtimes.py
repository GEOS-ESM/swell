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
from swell.utilities.cylc_runtime import Task

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
    class CompareJediCTestOutput(Task):
        pass

    @dataclass
    class BuildJediByLinking(Task):
        pass

    @dataclass
    class BuildJedi(Task):
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class StageJedi(Task):
        is_model: bool = True

    @dataclass
    class StageJediCycle(Task):
        is_cycling: bool = True
        is_model: bool = True
        base_name: str = "StageJedi"
        scheduling_name: str = "StageJediCycle-{model}"

    @dataclass
    class GetBackground(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetObservations(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GenerateBClimatology(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class GenerateBClimatologyByLinking(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class RunJediVariationalExecutable(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class EvaJediLog(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class EvaIncrement(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class EvaObservations(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class SaveObsDiags(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class CleanCycle(Task):
        is_cycling: bool = True
        is_model: bool = True

    @classmethod
    def get(cls, name: str) -> Task:
        return getattr(cls, name)

# --------------------------------------------------------------------------------------------------
