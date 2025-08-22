# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self
from collections.abc import Mapping
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
    class BuildGeos(Task):
        pass

    @dataclass
    class BuildGeosByLinking(Task):
        pass

    @dataclass
    class BuildJediByLinking(Task):
        pass

    @dataclass
    class BuildJedi(Task):
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class CleanCycle(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class CloneGeos(Task):
        pass

    @dataclass
    class CloneJedi(Task):
        pass

    @dataclass
    class CloneGeosMksi(Task):
        is_model: bool = True

    @dataclass
    class CompareJediCTestOutput(Task):
        pass

    @dataclass
    class EvaJediLog(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class EvaComparisonIncrement(Task):
        is_cycling: bool = True
        is_model: bool = True
    
    @dataclass
    class EvaComparisonJediLog(Task):
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
    class JediOopsLogParser(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetBackground(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetBackgroundGeosExperiment(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetEnsembleGeosExperiment(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetGeosRestart(Task):
        is_cycling: bool = True

    @dataclass
    class GetGeovals(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetGsiBc(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GsiBcToIoda(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetGsiNcdiag(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GsiNcdiagToIoda(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class GetGeosAdasBackground(Task):
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
    class GenerateObservingSystemRecords(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class LinkGeosOutput(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class MoveDaRestart(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class MoveForecastRestart(Task):
        is_cycling: bool = True

    @dataclass
    class PrepGeosRunDir(Task):
        is_cycling: bool = True

    @dataclass
    class PrepareAnalysis(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class RunJediFgatExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class RunJediHofxExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class RunJediLocalEnsembleDaExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class RunJediVariationalExecutable(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({'nodes': 3})

    @dataclass
    class RemoveForecastDir(Task):
        is_cycling: bool = True

    @dataclass
    class RunGeosExecutable(Task):
        is_cycling: bool = True

    @dataclass
    class RunJediUfoExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({})
        time_limit: bool = True

    @dataclass
    class RunJediUfoTestsExecutable(Task):
        time_limit: bool = True
        is_cycling: bool = True
        is_model: bool = True
        slurm: dict = mutable_field({'ntasks-per-node': 1})

    @dataclass
    class RunJediConvertStateSoca2ciceExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({'nodes': 1})

    @dataclass
    class RunJediFgatExecutable(Task):
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @dataclass
    class SaveObsDiags(Task):
        is_cycling: bool = True
        is_model: bool = True

    @dataclass
    class SaveRestart(Task):
        is_cycling: bool = True
        is_model: bool = True

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
    class sync_point(Task):
        script: str = "true"

    @dataclass
    class ThinObs(Task):
        script: str = ("swell task RunJediObsfiltersExecutable $config"
                       " -d $datetime -m geos_atmosphere")
        is_cycling: bool = True
        is_model: bool = True
        time_limit: bool = True
        slurm: dict = mutable_field({})

    @classmethod
    def get(cls, name: str) -> Task:
        return getattr(cls, name)

# --------------------------------------------------------------------------------------------------
