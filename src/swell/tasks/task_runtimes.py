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
    @member
    class root(Task):
        script: bool = False
        pre_script: str = "source $CYLC_SUITE_DEF_PATH/modules"
        environment: dict = mutable_field({'datetime': '$CYLC_TASK_CYCLE_POINT',
                                           'config': '$CYLC_SUITE_DEF_PATH/experiment.yaml'})

    @dataclass
    @member
    class BuildGeos(Task):
        pass

    @dataclass
    @member
    class BuildGeosByLinking(Task):
        pass

    @dataclass
    @member
    class BuildJediByLinking(Task):
        pass

    @dataclass
    @member
    class BuildJedi(Task):
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    @member
    class CleanCycle(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class CloneGeos(Task):
        pass

    @dataclass
    @member
    class CloneJedi(Task):
        pass

    @dataclass
    @member
    class CloneGeosMksi(Task):
        is_model: bool = True

    @dataclass
    @member
    class CompareJediCTestOutput(Task):
        pass

    @dataclass
    @member
    class EvaJediLog(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class EvaIncrement(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class EvaObservations(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    @member
    class GetBackground(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GetBackgroundGeosExperiment(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GetEnsembleGeosExperiment(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GetGeosRestart(Task):
        is_cycling: bool = True

    @dataclass
    @member
    class GetGeovals(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GetGsiBc(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GsiBcToIoda(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GetGsiNcdiag(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GsiNcdiagToIoda(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GetGeosAdasBackground(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GetObservations(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GenerateBClimatology(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    @member
    class GenerateBClimatologyByLinking(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class GenerateObservingSystemRecords(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class LinkGeosOutput(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class MoveDaRestart(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class MoveForecastRestart(Task):
        is_cycling: bool = True

    @dataclass
    @member
    class PrepGeosRunDir(Task):
        is_cycling: bool = True

    @dataclass
    @member
    class PrepareAnalysis(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class RunJediFgatExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    @member
    class RunJediHofxExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    @member
    class RunJediLocalEnsembleDaExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    @member
    class RunJediVariationalExecutable(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({'nodes': 3})

    @dataclass
    @member
    class RemoveForecastDir(Task):
        is_cycling: bool = True

    @dataclass
    @member
    class RunGeosExecutable(Task):
        is_cycling: bool = True

    @dataclass
    @member
    class RunJediUfoExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({})
        time_limit: bool = True

    @dataclass
    @member
    class RunJediUfoTestsExecutable(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({'ntasks-per-node': 1})

    @dataclass
    @member
    class RunJediConvertStateSoca2ciceExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({'nodes': 1})

    @dataclass
    @member
    class RunJediFgatExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    @member
    class SaveObsDiags(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class SaveRestart(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    @member
    class StageJedi(Task):
        is_model: bool = True

    @dataclass
    @member
    class StageJediCycle(Task):
        is_cycling: bool = True
        is_model: bool = True
        base_name: str = "StageJedi"
        scheduling_name: str = "StageJediCycle-{model}"

    @dataclass
    @member
    class sync_point(Task):
        script = "true"

    @dataclass
    @member
    class ThinObs(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @classmethod
    def get(cls, name: str) -> Task:
        return getattr(cls, name)

# --------------------------------------------------------------------------------------------------
