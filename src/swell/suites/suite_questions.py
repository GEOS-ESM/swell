# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from enum import Enum
from dataclasses import asdict

from swell.utilities.swell_questions import QuestionList, QuestionContainer
from swell.suites.suite_question_defaults import SuiteQuestionDefaults as sq


# --------------------------------------------------------------------------------------------------

class SuiteQuestions(QuestionContainer, Enum):
    
    # --------------------------------------------------------------------------------------------------
    
    all_suites = QuestionList(
        list_name = "all_suites",
        questions = [
            sq.experiment_id(),
            sq.experiment_root()
        ]
    )
    
    # --------------------------------------------------------------------------------------------------
    
    common = QuestionList(
        list_name = "common",
        questions = [
            all_suites,
            sq.cycle_times(),
            sq.start_cycle_point(),
            sq.final_cycle_point(),
            sq.model_components(),
            sq.runahead_limit()
        ]
    )
    
    # --------------------------------------------------------------------------------------------------

    marine = QuestionList(
        list_name = "marine",
        questions = [
            common,
            sq.marine_models()
        ]
    )    

    # --------------------------------------------------------------------------------------------------

    _3dfgat_atmos = QuestionList(
        list_name="3dfgat_atmos",
        questions = [
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dfgat_cycle = QuestionList(
        list_name="3dfgat_cycle",
        questions = [
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar = QuestionList(
        list_name="3dvar",
        questions = [
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_atmos = QuestionList(
        list_name="3dvar_atmos",
        questions = [
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cycle = QuestionList(
        list_name="3dvar_cycle",
        questions = [
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    convert_ncdiags = QuestionList(
        list_name="convert_ncdiags",
        questions = [
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    forecast_geos = QuestionList(
        list_name="forecast_geos",
        questions=[
            sq.cycle_times(),
            sq.final_cycle_point(),
            sq.start_cycle_point()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    hofx = QuestionList(
        list_name="hofx",
        questions=[
            marine,
            sq.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    localensembleda = QuestionList(
        list_name="localensembleda",
        questions=[
            marine,
            sq.ensemble_hofx_packets(),
            sq.ensemble_hofx_strategy(),
            sq.skip_ensemble_hofx(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    ufo_testing = QuestionList(
        list_name="ufo_testing",
        questions = [
            common,
        ]
    )


# --------------------------------------------------------------------------------------------------
