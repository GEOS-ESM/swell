# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from dataclasses import dataclass

from swell.utilities.swell_questions import SuiteQuestion, TaskQuestion
from swell.utilities.swell_questions import WidgetType as WType
from swell.utilities.dataclass_utils import mutable_field


# --------------------------------------------------------------------------------------------------

class QuestionDefaults():

    # --------------------------------------------------------------------------------------------------
    # Suite question defaults go here
    # --------------------------------------------------------------------------------------------------

    @dataclass
    class comparison_experiment_paths(SuiteQuestion):
        default_value: list = mutable_field([])
        question_name: str = "comparison_experiment_paths"
        ask_question: bool = True
        prompt: str = "Provide paths to two experiments to run comparison tests on."
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class cycle_times(SuiteQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "cycle_times"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Enter the cycle times for this model."
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class cycling_varbc(SuiteQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "cycling_varbc"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Do you want to use cycling VarBC option?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_packets(SuiteQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "ensemble_hofx_packets"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Enter the number of ensemble packets."
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_strategy(SuiteQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "ensemble_hofx_strategy"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Enter the ensemble hofx strategy."
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class experiment_id(SuiteQuestion):
        default_value: str = "defer_to_code"
        question_name: str = "experiment_id"
        ask_question: bool = True
        prompt: str = "What is the experiment id?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class experiment_root(SuiteQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "experiment_root"
        ask_question: bool = True
        prompt: str = ("What is the experiment root (the directory where the "
                       "experiment will be stored)?")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class final_cycle_point(SuiteQuestion):
        default_value: str = "2023-10-10T06:00:00Z"
        question_name: str = "final_cycle_point"
        ask_question: bool = True
        prompt: str = "What is the time of the final cycle (middle of the window)?"
        widget_type: WType = WType.ISO_DATETIME

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class marine_models(SuiteQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "marine_models"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_marine"
        ])
        prompt: str = "Select the active SOCA models for this model."
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class model_components(SuiteQuestion):
        default_value: str = "defer_to_code"
        question_name: str = "model_components"
        ask_question: bool = True
        options: str = "defer_to_code"
        prompt: str = "Enter the model components for this model."
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class parser_options(SuiteQuestion):
        default_value: list = mutable_field(['fgrep_residual_norm'])
        question_name: str = "parser_options"
        ask_question: bool = True
        options: list = mutable_field(['fgrep_residual_norm'])
        prompt: str = "list the test types to run on the JEDI oops log."
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class r2d2_experiment_id(SuiteQuestion):
        default_value: str = "defer_to_code"
        question_name: str = "r2d2_experiment_id"
        prompt: str = "What experiment_id should r2d2 reference for experiment?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class runahead_limit(SuiteQuestion):
        default_value: str = "P4"
        question_name: str = "runahead_limit"
        ask_question: bool = True
        prompt: str = ("Set the Cylc runahead limit: the maximum number of cycles "
                       "that may be active ahead of the current cycle "
                       "(e.g. P1: up to 1 cycle ahead, P3: up to 3 cycles ahead, default P4).")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class skip_ensemble_hofx(SuiteQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "skip_ensemble_hofx"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Enter if skip ensemble hofx."
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class skip_r2d2(SuiteQuestion):
        default_value: bool = False
        question_name: str = "skip_r2d2"
        prompt: str = "Skip registering and storing results of this experiment in R2D2?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class start_cycle_point(SuiteQuestion):
        default_value: str = "2023-10-10T00:00:00Z"
        question_name: str = "start_cycle_point"
        ask_question: bool = True
        prompt: str = "What is the time of the first cycle (middle of the window)?"
        widget_type: WType = WType.ISO_DATETIME

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class window_type(SuiteQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "window_type"
        options: list[str] = mutable_field([
            "3D",
            "4D"
        ])
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Enter the window type for this model."
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------
    # Task question defaults go here
    # --------------------------------------------------------------------------------------------------

    @dataclass
    class analysis_variables(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "analysis_variables"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What are the analysis variables?"
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_error_model(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "background_error_model"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Which background error model do you want to use?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_experiment(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "background_experiment"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What is the name of the name of the experiment providing the backgrounds?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_frequency(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "background_frequency"
        models: list[str] = mutable_field([
            "all_models"
        ])
        depends: dict = mutable_field({
            "window_type": "4D"
        })
        prompt: str = "What is the frequency of the background files?"
        widget_type: WType = WType.ISO_DURATION

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class background_time_offset(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "background_time_offset"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = ("How long before the middle of the analysis window did"
                       " the background providing forecast begin?")
        widget_type: WType = WType.ISO_DURATION

    # --------------------------------------------------------------------------------------------------
    @dataclass
    class bufr_obs_classes(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "bufr_obs_classes"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What BUFR observation classes will be used?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class bundles(TaskQuestion):
        default_value: list[str] = mutable_field([
            "fv3-jedi",
            "soca",
            "iodaconv",
            "ufo"
        ])
        question_name: str = "bundles"
        ask_question: bool = True
        options: list[str] = mutable_field([
            "fv3-jedi",
            "soca",
            "iodaconv",
            "ufo",
            "ioda",
            "oops",
            "saber"
        ])
        depends: dict = mutable_field({
            "jedi_build_method": "create"
        })
        prompt: str = "Which JEDI bundles do you wish to build?"
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class check_for_obs(TaskQuestion):
        default_value: bool = True
        question_name: str = "check_for_obs"
        options: list[bool] = mutable_field([True, False])
        models: list[str] = mutable_field([
            'all_models'
        ])
        prompt: str = "Perform check for observations? Set to false for debugging purposes."
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class clean_patterns(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "clean_patterns"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Provide a list of patterns that you wish to remove from the cycle directory."
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class comparison_log_type(TaskQuestion):
        default_value: str = "variational"
        question_name: str = "comparison_log_type"
        options: list[str] = mutable_field([
            'variational',
            'fgat',
        ])
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Provide the log naming convention (e.g. 'variational', 'fgat')."
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class crtm_coeff_dir(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "crtm_coeff_dir"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to the CRTM coefficient files?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_packets(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "ensemble_hofx_packets"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Enter number of packets in which ensemble observers should be computed."
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_hofx_strategy(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "ensemble_hofx_strategy"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Enter hofx strategy."
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensemble_num_members(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "ensemble_num_members"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "How many members comprise the ensemble?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensmean_only(TaskQuestion):
        default_value: bool = False
        question_name: str = "ensmean_only"
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Calculate ensemble mean only?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ensmeanvariance_only(TaskQuestion):
        default_value: bool = False
        question_name: str = "ensmeanvariance_only"
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Calculate ensemble mean and variance only?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_geos_gcm_build_path(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "existing_geos_gcm_build_path"
        ask_question: bool = True
        depends: dict = mutable_field({
            "geos_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing GEOS build directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_geos_gcm_source_path(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "existing_geos_gcm_source_path"
        ask_question: bool = True
        depends: dict = mutable_field({
            "geos_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing GEOS source code directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_build_directory(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "existing_jedi_build_directory"
        ask_question: bool = True
        depends: dict = mutable_field({
            "jedi_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing JEDI build directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_build_directory_pinned(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "existing_jedi_build_directory_pinned"
        ask_question: bool = True
        depends: dict = mutable_field({
            "jedi_build_method": "use_pinned_existing"
        })
        prompt: str = "What is the path to the existing pinned JEDI build directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_source_directory(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "existing_jedi_source_directory"
        ask_question: bool = True
        depends: dict = mutable_field({
            "jedi_build_method": "use_existing"
        })
        prompt: str = "What is the path to the existing JEDI source code directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_jedi_source_directory_pinned(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "existing_jedi_source_directory_pinned"
        ask_question: bool = True
        depends: dict = mutable_field({
            "jedi_build_method": "use_pinned_existing"
        })
        prompt: str = "What is the path to the existing pinned JEDI source code directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class existing_perllib_path(TaskQuestion):
        default_value: str = 'defer_to_platform'
        question_name: str = 'existing_perllib_path'
        prompt: str = "Provide a path to an existing location for GMAO_perllib."
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class gmao_perllib_tag(TaskQuestion):
        default_value: str = 'g1.0.1'
        question_name: str = 'gmao_perllib_tag'
        prompt: str = "Specify the tag at which GMAO_perllib should be cloned."
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class forecast_duration(TaskQuestion):
        default_value: str = "PT12H"
        question_name: str = "forecast_duration"
        ask_question: bool = True
        prompt: str = "GEOS forecast duration"
        widget_type: WType = WType.ISO_DURATION

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class generate_yaml_and_exit(TaskQuestion):
        default_value: bool = False
        question_name: str = "generate_yaml_and_exit"
        prompt: str = "Generate JEDI executable YAML and exit?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_build_method(TaskQuestion):
        default_value: str = "create"
        question_name: str = "geos_build_method"
        ask_question: bool = True
        options: list[str] = mutable_field([
            "use_existing",
            "create"
        ])
        prompt: str = "Do you want to use an existing GEOS build or create a new build?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_homdir(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "geos_homdir"
        ask_question: bool = True
        prompt: str = ("What is the location for the HOME Directory (HOMDIR in gcm_run and "
                       "gcm_setup) that contains model settings and RC files?")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_expdir_different(TaskQuestion):
        default_value: str = False
        question_name: str = "geos_expdir_different"
        ask_question: bool = True
        options: list[bool] = mutable_field([
            True,
            False
        ])
        prompt: str = ("Is your GEOS EXPERIMENT Directory, where restarts and scratch is located, "
                       "different than your GEOS HOME Directory?")
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_expdir(TaskQuestion):
        default_value: str = "/dev/null/"
        question_name: str = "geos_expdir"
        depends: dict = mutable_field({
            "geos_expdir_different": True
        })
        prompt: str = ("What is the location for the EXPERIMENT Directory (to contain model "
                       "output and restart files), if it is different than your GEOS HOME "
                       "Directory?")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_gcm_tag(TaskQuestion):
        default_value: str = "v11.6.0"
        question_name: str = "geos_gcm_tag"
        depends: dict = mutable_field({
            "geos_build_method": "create"
        })
        prompt: str = "Which GEOS tag do you wish to clone?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_x_background_directory(TaskQuestion):
        default_value: str = "/dev/null/"
        question_name: str = "geos_x_background_directory"
        ask_question: bool = True
        options: list[str] = mutable_field([
            "/dev/null/",
            "/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x"
        ])
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What is the path to the GEOS X-backgrounds directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geos_x_ensemble_directory(TaskQuestion):
        default_value: str = "/dev/null/"
        question_name: str = "geos_x_ensemble_directory"
        ask_question: bool = True
        options: list[str] = mutable_field([
            "/dev/null/",
            "/gpfsm/dnb05/projects/p139/rtodling/archive/"
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to the GEOS X-backgrounds directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geovals_experiment(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "geovals_experiment"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the name of the R2D2 experiment providing the GeoVaLs?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class geovals_provider(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "geovals_provider"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the name of the R2D2 database providing the GeoVaLs?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class gradient_norm_reduction(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "gradient_norm_reduction"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What value of gradient norm reduction for convergence?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class gsibec_configuration(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "gsibec_configuration"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Which GSIBEC climatological or hybrid?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class gsibec_nlats(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "gsibec_nlats"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "How many number of latutides in GSIBEC grid?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class gsibec_nlons(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "gsibec_nlons"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "How many number of longitudes in GSIBEC grid?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_localization_lengthscale(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "horizontal_localization_lengthscale"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the length scale for horizontal covariance localization?"
        widget_type: WType = WType.FLOAT

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_localization_max_nobs(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "horizontal_localization_max_nobs"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = ("What is the maximum number of observations to consider"
                       " for horizontal covariance localization?")
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_localization_method(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "horizontal_localization_method"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Which localization scheme should be applied in the horizontal?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class horizontal_resolution(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "horizontal_resolution"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What is the horizontal resolution for the forecast model and backgrounds?"
        widget_type: WType = WType.STRING_DROP_LIST

    # ------------------------------------------------------------------------------------------------

    @dataclass
    class dry_run(TaskQuestion):
        default_value: bool = True
        question_name: str = "dry_run"
        ask_question: bool = False
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Dry-run mode: preview what would be ingested before storing to R2D2"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class obs_to_ingest(TaskQuestion):
        default_value: list = mutable_field([])
        question_name: str = "obs_to_ingest"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Which observations do you want to ingest to R2D2?"
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------
    @dataclass
    class initial_restarts_method(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "initial_restarts_method"
        ask_question: bool = True
        options: list[str] = mutable_field([
            "geos_expdir",
            "r2d2",
            "hotstart",
        ])
        prompt: str = "How should initial GEOS restarts be obtained?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ioda_locations_not_in_r2d2(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "ioda_locations_not_in_r2d2"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = (
            "Provide a path that contains observation files not in r2d2.")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class jedi_build_method(TaskQuestion):
        default_value: str = "create"
        question_name: str = "jedi_build_method"
        ask_question: bool = True
        options: list[str] = mutable_field([
            "use_existing",
            "use_pinned_existing",
            "create",
            "pinned_create"
        ])
        prompt: str = "Do you want to use an existing JEDI build or create a new build?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class jedi_forecast_model(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "jedi_forecast_model"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        depends: dict = mutable_field({
            "window_type": "4D"
        })
        prompt: str = "What forecast model should be used within JEDI for 4D window propagation?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_inflation_mult(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "local_ensemble_inflation_mult"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Specify the multiplicative prior inflation coefficient (0 inf]."
        widget_type: WType = WType.FLOAT

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_inflation_rtpp(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "local_ensemble_inflation_rtpp"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Specify the Relaxation To Prior Perturbation (RTPP) coefficient (0 1]."
        widget_type: WType = WType.FLOAT

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_inflation_rtps(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "local_ensemble_inflation_rtps"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Specify the Relaxation To Prior Spread (RTPS) coefficient (0 1]."
        widget_type: WType = WType.FLOAT

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_ensemble(TaskQuestion):
        default_value: bool = False
        question_name: str = "local_ensemble_save_posterior_ensemble"
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble members?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_ensemble_increments(TaskQuestion):
        default_value: bool = False
        question_name: str = "local_ensemble_save_posterior_ensemble_increments"
        ask_question: bool = True
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble member increments?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_mean(TaskQuestion):
        default_value: bool = False
        question_name: str = "local_ensemble_save_posterior_mean"
        ask_question: bool = True
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble mean?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_save_posterior_mean_increment(TaskQuestion):
        default_value: bool = True
        question_name: str = "local_ensemble_save_posterior_mean_increment"
        ask_question: bool = True
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Save the posterior ensemble mean increment?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_solver(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "local_ensemble_solver"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Which local ensemble solver type should be implemented?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class local_ensemble_use_linear_observer(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "local_ensemble_use_linear_observer"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Which local ensemble solver type should be implemented?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class minimizer(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "minimizer"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Which data assimilation minimizer do you wish to use?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class mom6_iau(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "mom6_iau"
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_marine",
        ])
        prompt: str = "Do you wish to use IAU for MOM6?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class mom6_iau_nhours(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "mom6_iau_nhours"
        options: list[str] = mutable_field([
            'PT3H',
            'PT12H'
        ])
        depends: dict = mutable_field({'mom6_iau': True})
        models: list[str] = mutable_field([
            "geos_marine",
        ])
        prompt: str = "What is the IAU length (ODA_INCUPD_NHOURS) for MOM6?"
        widget_type: WType = WType.ISO_DURATION

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class ncdiag_experiments(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "ncdiag_experiments"
        options: list[str] = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Which previously run experiments do you wish to use for the NCdiag?"
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class npx_proc(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "npx_proc"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere",
            "geos_cf"
        ])
        prompt: str = "What number of processors do you wish to use in the x-direction?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class npy_proc(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "npy_proc"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere",
            "geos_cf"
        ])
        prompt: str = "What number of processors do you wish to use in the y-direction?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class npx(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "npx"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_cf"
        ])
        prompt: str = "What is the number of grid points in the x-direction on each cube face?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class npy(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "npy"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_cf"
        ])
        prompt: str = "What is the number of grid points in the y-direction on each cube face?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class number_of_iterations(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "number_of_iterations"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = (
            "What number of iterations do you wish to use for each outer loop?"
            " Provide a list of integers the same length as the number of outer loops.")
        widget_type: WType = WType.INTEGER_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class obs_experiment(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "obs_experiment"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What is the database providing the observations?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class obs_thinning_rej_fraction(TaskQuestion):
        default_value: float = 0.75
        question_name: str = "obs_thinning_rej_fraction"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the rejection fraction for obs thinning?"
        widget_type: WType = WType.FLOAT

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observations(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "observations"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Which observations do you want to include?"
        widget_type: WType = WType.STRING_CHECK_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observing_system_records_mksi_path(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "observing_system_records_mksi_path"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to the GSI formatted observing system records?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observing_system_records_mksi_path_tag(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "observing_system_records_mksi_path_tag"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the GSI formatted observing system records tag?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class observing_system_records_path(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "observing_system_records_path"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to the Swell formatted observing system records?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_ensemble(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "path_to_ensemble"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere",
            "geos_marine"
        ])
        prompt: str = "What is the path to where ensemble members are stored?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_geos_adas_background(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "path_to_geos_adas_background"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = (
            "What is the path for the GEOSadas cubed sphere backgrounds?")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_gsi_bc_coefficients(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "path_to_gsi_bc_coefficients"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the location where GSI bias correction files can be found?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class path_to_gsi_nc_diags(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "path_to_gsi_nc_diags"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the path to where the GSI ncdiags are stored?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class perhost(TaskQuestion):
        default_value: str = None
        question_name: str = "perhost"
        ask_question: bool = True
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the number of processors per host?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class produce_geovals(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "produce_geovals"
        ask_question: bool = True
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = ("When running the ncdiag to ioda converted do you "
                       "want to produce GeoVaLs files?")
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class save_geovals(TaskQuestion):
        default_value: bool = False
        question_name: str = "save_geovals"
        options: list[bool] = mutable_field([
            True,
            False
        ])
        prompt: str = "When running hofx do you want to output the GeoVaLs?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class single_observations(TaskQuestion):
        default_value: bool = False
        question_name: str = "single_observations"
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Is it a single-observation test?"
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class swell_static_files(TaskQuestion):
        default_value: str = "defer_to_platform"
        question_name: str = "swell_static_files"
        prompt: str = "What is the path to the Swell Static files directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class swell_static_files_user(TaskQuestion):
        default_value: str = "None"
        question_name: str = "swell_static_files_user"
        prompt: str = "What is the path to the user provided Swell Static Files directory?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class total_processors(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "total_processors"
        ask_question: bool = True
        models: list[str] = mutable_field([
            "geos_marine",
        ])
        prompt: str = "What is the number of processors for JEDI?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_apply_log_transform(TaskQuestion):
        default_value: bool = True
        question_name: str = "vertical_localization_apply_log_transform"
        options: list[bool] = mutable_field([
            True,
            False
        ])
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = ("Should a log (base 10) transformation be applied "
                       "to vertical coordinate when "
                       "constructing vertical localization?")
        widget_type: WType = WType.BOOLEAN

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_function(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "vertical_localization_function"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Which localization scheme should be applied in the vertical?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_ioda_vertical_coord(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "vertical_localization_ioda_vertical_coord"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "Which coordinate should be used in constructing vertical localization?"
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_ioda_vertical_coord_group(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "vertical_localization_ioda_vertical_coord_group"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = ("Which vertical coordinate group should be used "
                       "in constructing vertical localization?")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_lengthscale(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "vertical_localization_lengthscale"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = "What is the length scale for vertical covariance localization?"
        widget_type: WType = WType.INTEGER

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_localization_method(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "vertical_localization_method"
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "geos_atmosphere"
        ])
        prompt: str = ("What localization scheme should be applied in "
                       "constructing a vertical localization?")
        widget_type: WType = WType.STRING

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class vertical_resolution(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "vertical_resolution"
        ask_question: bool = True
        options: str = "defer_to_model"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What is the vertical resolution for the forecast model and background?"
        widget_type: WType = WType.STRING_DROP_LIST

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class window_length(TaskQuestion):
        default_value: str = "defer_to_model"
        question_name: str = "window_length"
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "What is the duration for the data assimilation window?"
        widget_type: WType = WType.ISO_DURATION

    # --------------------------------------------------------------------------------------------------

    @dataclass
    class window_type(TaskQuestion):
        question_name: str = "window_type"
        default_value: str = "defer_to_model"
        ask_question: bool = True
        options: list[str] = mutable_field([
            "3D",
            "4D"
        ])
        models: list[str] = mutable_field([
            "all_models"
        ])
        prompt: str = "Do you want to use a 3D or 4D (including FGAT) window?"
        widget_type: WType = WType.STRING_DROP_LIST

# --------------------------------------------------------------------------------------------------
