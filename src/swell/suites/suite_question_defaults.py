# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from dataclasses import dataclass, field
from typing import List

from swell.utilities.swell_questions import SuiteQuestion, QDtype


# --------------------------------------------------------------------------------------------------

class SuiteQuestionDefaults():

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class cycle_times(SuiteQuestion):
        question_name: str = "cycle_times"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Enter the cycle times for this model."
        dtype: str = QDtype.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_packets(SuiteQuestion):
        question_name: str = "ensemble_hofx_packets"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Enter the number of ensemble packets."
        dtype: str = QDtype.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_strategy(SuiteQuestion):
        question_name: str = "ensemble_hofx_strategy"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Enter the ensemble hofx strategy."
        dtype: str = QDtype.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class experiment_id(SuiteQuestion):
        question_name: str = "experiment_id"
        default_value: str = "defer_to_code"
        ask_question: bool = True
        prompt: str = "What is the experiment id?"
        dtype: str = QDtype.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class experiment_root(SuiteQuestion):
        question_name: str = "experiment_root"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        prompt: str = ("What is the experiment root (the directory where the "
                       "experiment will be stored)?")
        dtype: str = QDtype.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class final_cycle_point(SuiteQuestion):
        question_name: str = "final_cycle_point"
        default_value: str = "2023-10-10T06:00:00Z"
        ask_question: bool = True
        prompt: str = "What is the time of the final cycle (middle of the window)?"
        dtype: str = QDtype.ISO_DATETIME

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class marine_models(SuiteQuestion):
        question_name: str = "marine_models"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_marine"
        ])
        prompt: str = "Select the active SOCA models for this model."
        dtype: str = QDtype.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class model_components(SuiteQuestion):
        question_name: str = "model_components"
        default_value: str = "defer_to_code"
        ask_question: bool = True
        options: str = "defer_to_code"
        prompt: str = "Enter the model components for this model."
        dtype: str = QDtype.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class runahead_limit(SuiteQuestion):
        question_name: str = "runahead_limit"
        default_value: str = "P4"
        ask_question: bool = True
        prompt: str = ("Since this suite is non-cycling choose how "
                       "many hours the workflow can run ahead?")
        dtype: str = QDtype.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class skip_ensemble_hofx(SuiteQuestion):
        question_name: str = "skip_ensemble_hofx"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Enter if skip ensemble hofx."
        dtype: str = QDtype.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class start_cycle_point(SuiteQuestion):
        question_name: str = "start_cycle_point"
        default_value: str = "2023-10-10T00:00:00Z"
        ask_question: bool = True
        prompt: str = "What is the time of the first cycle (middle of the window)?"
        dtype: str = QDtype.ISO_DATETIME

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class window_type(SuiteQuestion):
        question_name: str = "window_type"
        default_value: str = "defer_to_model"
        options: List[str] = field(default_factory=lambda: [
            "3D",
            "4D"
        ])
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Enter the window type for this model."
        dtype: str = QDtype.STRING_DROP_LIST

# --------------------------------------------------------------------------------------------------
