# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from swell.utilities.swell_questions import TaskQuestion


# --------------------------------------------------------------------------------------------------

class TaskQuestionDefaults():

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class analysis_forecast_window_offset(TaskQuestion):
        question_name: str = "analysis_forecast_window_offset"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the duration from the middle of the window when forecasts start?"
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class analysis_variables(TaskQuestion):
        question_name: str = "analysis_variables"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What are the analysis variables?"
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_error_model(TaskQuestion):
        question_name: str = "background_error_model"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Which background error model do you want to use?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_experiment(TaskQuestion):
        question_name: str = "background_experiment"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the name of the name of the experiment providing the backgrounds?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_frequency(TaskQuestion):
        question_name: str = "background_frequency"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        depends: Dict = field(default_factory=lambda: {
            "window_type": "4D"
        })
        prompt: str = "What is the frequency of the background files?"
        dtype: str = "iso-duration"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_time_offset(TaskQuestion):
        question_name: str = "background_time_offset"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = ("How long before the middle of the analysis window did"
                      " the background providing forecast begin?")
        dtype: str = "iso-duration"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class bundles(TaskQuestion):
        question_name: str = "bundles"
        default_value: List[str] = field(default_factory=lambda: [
            "fv3-jedi",
            "soca",
            "iodaconv",
            "ufo"
        ])
        ask_question: bool = True
        options: List[str] = field(default_factory=lambda: [
            "fv3-jedi",
            "soca",
            "iodaconv",
            "ufo",
            "ioda",
            "oops",
            "saber"
        ])
        depends: Dict = field(default_factory=lambda: {
            "jedi_build_method": "create"
        })
        prompt: str = "Which JEDI bundles do you wish to build?"
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class cice6_domains(TaskQuestion):
        question_name: str = "cice6_domains"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_marine"
        ])
        prompt: str = "Which CICE6 domains do you wish to run DA for?"
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class clean_patterns(TaskQuestion):
        question_name: str = "clean_patterns"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Provide a list of patterns that you wish to remove from the cycle directory."
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class crtm_coeff_dir(TaskQuestion):
        question_name: str = "crtm_coeff_dir"
        default_value: str = "defer_to_platform"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to the CRTM coefficient files?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class cycling_varbc(TaskQuestion):
        question_name: str = "cycling_varbc"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Do you want to use cycling VarBC option?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_packets(TaskQuestion):
        question_name: str = "ensemble_hofx_packets"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Enter number of packets in which ensemble observers should be computed."
        dtype: str = "integer"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_strategy(TaskQuestion):
        question_name: str = "ensemble_hofx_strategy"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Enter hofx strategy."
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_num_members(TaskQuestion):
        question_name: str = "ensemble_num_members"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "How many members comprise the ensemble?"
        dtype: str = "integer"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensmean_only(TaskQuestion):
        question_name: str = "ensmean_only"
        default_value: str = False
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Calculate ensemble mean only?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensmeanvariance_only(TaskQuestion):
        question_name: str = "ensmeanvariance_only"
        default_value: str = False
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Calculate ensemble mean and variance only?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_geos_gcm_build_path(TaskQuestion):
        question_name: str = "existing_geos_gcm_build_path"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        depends: Dict = field(default_factory=lambda: {
            "geos_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing GEOS build directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_geos_gcm_source_path(TaskQuestion):
        question_name: str = "existing_geos_gcm_source_path"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        depends: Dict = field(default_factory=lambda: {
            "geos_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing GEOS source code directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_build_directory(TaskQuestion):
        question_name: str = "existing_jedi_build_directory"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        depends: Dict = field(default_factory=lambda: {
            "jedi_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing JEDI build directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_build_directory_pinned(TaskQuestion):
        question_name: str = "existing_jedi_build_directory_pinned"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        depends: Dict = field(default_factory=lambda: {
            "jedi_build_method": "use_pinned_existing"
        })
        prompt: str = "What is the path to the existing pinned JEDI build directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_source_directory(TaskQuestion):
        question_name: str = "existing_jedi_source_directory"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        depends: Dict = field(default_factory=lambda: {
            "jedi_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing JEDI source code directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_source_directory_pinned(TaskQuestion):
        question_name: str = "existing_jedi_source_directory_pinned"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        depends: Dict = field(default_factory=lambda: {
            "jedi_build_method": "use_pinned_existing"
        })
        prompt: str = "What is the path to the existing pinned JEDI source code directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class forecast_duration(TaskQuestion):
        question_name: str = "forecast_duration"
        default_value: str = "PT12H"
        ask_question: bool = True
        prompt: str = "GEOS forecast duration"
        dtype: str = "iso-duration"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class generate_yaml_and_exit(TaskQuestion):
        question_name: str = "generate_yaml_and_exit"
        default_value: str = False
        prompt: str = "Generate JEDI executable YAML and exit?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_build_method(TaskQuestion):
        question_name: str = "geos_build_method"
        default_value: str = "create"
        ask_question: bool = True
        options: List[str] = field(default_factory=lambda: [
            "use_existing",
            "create"
        ])
        prompt: str = "Do you want to use an existing GEOS build or create a new build?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_experiment_directory(TaskQuestion):
        question_name: str = "geos_experiment_directory"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        prompt: str = "What is the path to the GEOS restarts directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_gcm_tag(TaskQuestion):
        question_name: str = "geos_gcm_tag"
        default_value: str = "v11.6.0"
        ask_question: bool = True
        prompt: str = "Which GEOS tag do you wish to clone?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_restarts_directory(TaskQuestion):
        question_name: str = "geos_restarts_directory"
        default_value: str = "defer_to_platform"
        ask_question: bool = True
        prompt: str = "What is the path to the GEOS restarts directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_x_background_directory(TaskQuestion):
        question_name: str = "geos_x_background_directory"
        default_value: str = "/dev/null/"
        ask_question: bool = True
        options: List[str] = field(default_factory=lambda: [
            "/dev/null/",
            "/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x"
        ])
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the path to the GEOS X-backgrounds directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geovals_experiment(TaskQuestion):
        question_name: str = "geovals_experiment"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the name of the R2D2 experiment providing the GeoVaLs?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geovals_provider(TaskQuestion):
        question_name: str = "geovals_provider"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the name of the R2D2 database providing the GeoVaLs?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class gradient_norm_reduction(TaskQuestion):
        question_name: str = "gradient_norm_reduction"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What value of gradient norm reduction for convergence?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class gsibec_configuration(TaskQuestion):
        question_name: str = "gsibec_configuration"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Which GSIBEC climatological or hybrid?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_localization_lengthscale(TaskQuestion):
        question_name: str = "horizontal_localization_lengthscale"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the length scale for horizontal covariance localization?"
        dtype: str = "float"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_localization_max_nobs(TaskQuestion):
        question_name: str = "horizontal_localization_max_nobs"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = ("What is the maximum number of observations to consider"
                       " for horizontal covariance localization?")
        dtype: str = "integer"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_localization_method(TaskQuestion):
        question_name: str = "horizontal_localization_method"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Which localization scheme should be applied in the horizontal?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_resolution(TaskQuestion):
        question_name: str = "horizontal_resolution"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the horizontal resolution for the forecast model and backgrounds?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class jedi_build_method(TaskQuestion):
        question_name: str = "jedi_build_method"
        default_value: str = "create"
        ask_question: bool = True
        options: List[str] = field(default_factory=lambda: [
            "use_existing",
            "use_pinned_existing",
            "create",
            "pinned_create"
        ])
        prompt: str = "Do you want to use an existing JEDI build or create a new build?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class jedi_forecast_model(TaskQuestion):
        question_name: str = "jedi_forecast_model"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        depends: Dict = field(default_factory=lambda: {
            "window_type": "4D"
        })
        prompt: str = "What forecast model should be used within JEDI for 4D window propagation?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_inflation_mult(TaskQuestion):
        question_name: str = "local_ensemble_inflation_mult"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Specify the multiplicative prior inflation coefficient (0 inf]."
        dtype: str = "float"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_inflation_rtpp(TaskQuestion):
        question_name: str = "local_ensemble_inflation_rtpp"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Specify the Relaxation To Prior Perturbation (RTPP) coefficient (0 1]."
        dtype: str = "float"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_inflation_rtps(TaskQuestion):
        question_name: str = "local_ensemble_inflation_rtps"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Specify the Relaxation To Prior Spread (RTPS) coefficient (0 1]."
        dtype: str = "float"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_ensemble(TaskQuestion):
        question_name: str = "local_ensemble_save_posterior_ensemble"
        default_value: str = False
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble members?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_ensemble_increments(TaskQuestion):
        question_name: str = "local_ensemble_save_posterior_ensemble_increments"
        default_value: str = False
        ask_question: bool = True
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble member increments?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_mean(TaskQuestion):
        question_name: str = "local_ensemble_save_posterior_mean"
        default_value: str = False
        ask_question: bool = True
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble mean?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_mean_increment(TaskQuestion):
        question_name: str = "local_ensemble_save_posterior_mean_increment"
        default_value: str = True
        ask_question: bool = True
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble mean increment?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_solver(TaskQuestion):
        question_name: str = "local_ensemble_solver"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Which local ensemble solver type should be implemented?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_use_linear_observer(TaskQuestion):
        question_name: str = "local_ensemble_use_linear_observer"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Which local ensemble solver type should be implemented?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class marine_models(TaskQuestion):
        question_name: str = "marine_models"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_marine"
        ])
        prompt: str = "Enter the active SOCA models for this model."
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class minimizer(TaskQuestion):
        question_name: str = "minimizer"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Which data assimilation minimizer do you wish to use?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class mom6_iau(TaskQuestion):
        question_name: str = "mom6_iau"
        default_value: str = "defer_to_model"
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_marine",
            "geos_ocean"
        ])
        prompt: str = "Do you wish to use IAU for MOM6?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class npx_proc(TaskQuestion):
        question_name: str = "npx_proc"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What number of processors do you wish to use in the x-direction?"
        dtype: str = "integer"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class npy_proc(TaskQuestion):
        question_name: str = "npy_proc"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What number of processors do you wish to use in the y-direction?"
        dtype: str = "integer"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class number_of_iterations(TaskQuestion):
        question_name: str = "number_of_iterations"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = ("What number of iterations do you wish to use for each outer loop?"
                       " Provide a list of integers the same length as the number of outer loops.")
        dtype: str = "integer-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class obs_experiment(TaskQuestion):
        question_name: str = "obs_experiment"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the database providing the observations?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class obs_provider(TaskQuestion):
        question_name: str = "obs_provider"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Which group(s) provide the observations?"
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observations(TaskQuestion):
        question_name: str = "observations"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Which observations do you want to include?"
        dtype: str = "string-check-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observing_system_records_mksi_path(TaskQuestion):
        question_name: str = "observing_system_records_mksi_path"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to the GSI formatted observing system records?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observing_system_records_mksi_path_tag(TaskQuestion):
        question_name: str = "observing_system_records_mksi_path_tag"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the GSI formatted observing system records tag?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observing_system_records_path(TaskQuestion):
        question_name: str = "observing_system_records_path"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to the Swell formatted observing system records?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_ensemble(TaskQuestion):
        question_name: str = "path_to_ensemble"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to where ensemble members are stored?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_geos_adas_background(TaskQuestion):
        question_name: str = "path_to_geos_adas_background"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to where the cubed sphere backgrounds are in the GEOSadas run?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_gsi_bc_coefficients(TaskQuestion):
        question_name: str = "path_to_gsi_bc_coefficients"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the location where GSI bias correction files can be found?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_gsi_nc_diags(TaskQuestion):
        question_name: str = "path_to_gsi_nc_diags"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to where the GSI ncdiags are stored?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class produce_geovals(TaskQuestion):
        question_name: str = "produce_geovals"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "When running the ncdiag to ioda converted do you want to produce GeoVaLs files?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class r2d2_local_path(TaskQuestion):
        question_name: str = "r2d2_local_path"
        default_value: str = "defer_to_platform"
        prompt: str = "What is the path to the R2D2 local directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class save_geovals(TaskQuestion):
        question_name: str = "save_geovals"
        default_value: str = False
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        prompt: str = "When running hofx do you want to output the GeoVaLs?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class single_observations(TaskQuestion):
        question_name: str = "single_observations"
        default_value: str = False
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Is it a single-observation test?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class skip_ensemble_hofx(TaskQuestion):
        question_name: str = "skip_ensemble_hofx"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Which local ensemble solver type should be implemented?"
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class swell_static_files(TaskQuestion):
        question_name: str = "swell_static_files"
        default_value: str = "defer_to_platform"
        prompt: str = "What is the path to the Swell Static files directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class swell_static_files_user(TaskQuestion):
        question_name: str = "swell_static_files_user"
        default_value: str = "None"
        prompt: str = "What is the path to the user provided Swell Static Files directory?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class total_processors(TaskQuestion):
        question_name: str = "total_processors"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "geos_marine",
            "geos_ocean"
        ])
        prompt: str = "What is the number of processors for JEDI?"
        dtype: str = "integer"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_apply_log_transform(TaskQuestion):
        question_name: str = "vertical_localization_apply_log_transform"
        default_value: str = True
        options: List[bool] = field(default_factory=lambda: [
            True,
            False
        ])
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = ("Should a log (base 10) transformation be applied to vertical coordinate when"
                       " constructing vertical localization?")
        dtype: str = "boolean"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_function(TaskQuestion):
        question_name: str = "vertical_localization_function"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Which localization scheme should be applied in the vertical?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_ioda_vertical_coord(TaskQuestion):
        question_name: str = "vertical_localization_ioda_vertical_coord"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "Which coordinate should be used in constructing vertical localization?"
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_ioda_vertical_coord_group(TaskQuestion):
        question_name: str = "vertical_localization_ioda_vertical_coord_group"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = ("Which vertical coordinate group should be used"
                " in constructing vertical localization?")
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_lengthscale(TaskQuestion):
        question_name: str = "vertical_localization_lengthscale"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = "What is the length scale for vertical covariance localization?"
        dtype: str = "integer"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_method(TaskQuestion):
        question_name: str = "vertical_localization_method"
        default_value: str = "defer_to_model"
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "geos_atmosphere"
        ])
        prompt: str = ("What localization scheme should be applied in"
                "constructing a vertical localization?")
        dtype: str = "string"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_resolution(TaskQuestion):
        question_name: str = "vertical_resolution"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the vertical resolution for the forecast model and background?"
        dtype: str = "string-drop-list"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class window_length(TaskQuestion):
        question_name: str = "window_length"
        default_value: str = "defer_to_model"
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the duration for the data assimilation window?"
        dtype: str = "iso-duration"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class window_offset(TaskQuestion):
        question_name: str = "window_offset"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "What is the duration between the middle of the window and the beginning?"
        dtype: str = "iso-duration"

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class window_type(TaskQuestion):
        question_name: str = "window_type"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: List[str] = field(default_factory=lambda: [
            "3D",
            "4D"
        ])
        models: List[str] = field(default_factory=lambda: [
            "all_models"
        ])
        prompt: str = "Do you want to use a 3D or 4D (including FGAT) window?"
        dtype: str = "string-drop-list"

# --------------------------------------------------------------------------------------------------
