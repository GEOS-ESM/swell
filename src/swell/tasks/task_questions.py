# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from enum import Enum

from swell.utilities.swell_questions import QuestionList, QuestionContainer
from swell.tasks.task_question_defaults import TaskQuestionDefaults as tq


# --------------------------------------------------------------------------------------------------

class TaskQuestions(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    window_questions = QuestionList(
        list_name="window_questions",
        questions=[
            tq.window_length(),
            tq.window_offset(),
            tq.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    np_proc_resolution = QuestionList(
        list_name="np_resolution",
        questions=[
            tq.npx_proc(),
            tq.npy_proc(),
            tq.horizontal_resolution(),
            tq.vertical_resolution()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    swell_static_file_questions = QuestionList(
        list_name="swell_static_file_questions",
        questions=[
            tq.swell_static_files(),
            tq.swell_static_files_user()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    background_crtm_obs = QuestionList(
        list_name="background_crtm_obs",
        questions=[
            tq.background_time_offset(),
            tq.crtm_coeff_dir(),
            tq.observations()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    run_jedi_executable = QuestionList(
        list_name="run_jedi_executable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            tq.analysis_variables(),
            tq.background_frequency(),
            tq.generate_yaml_and_exit(),
            tq.gradient_norm_reduction(),
            tq.gsibec_configuration(),
            tq.jedi_forecast_model(),
            tq.minimizer(),
            tq.number_of_iterations(),
            tq.observing_system_records_path(),
            tq.total_processors(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetBackground = QuestionList(
        list_name="GetBackground",
        questions=[
            window_questions,
            tq.analysis_forecast_window_offset(),
            tq.background_experiment(),
            tq.background_frequency(),
            tq.horizontal_resolution(),
            tq.r2d2_local_path(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    MoveDaRestart = QuestionList(
        list_name="MoveDaRestart",
        questions=[
            tq.analysis_forecast_window_offset(),
            tq.mom6_iau(),
            tq.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    PrepareAnalysis = QuestionList(
        list_name="PrepareAnalysis",
        questions=[
            tq.analysis_forecast_window_offset(),
            tq.analysis_variables(),
            tq.mom6_iau(),
            tq.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    StoreBackground = QuestionList(
        list_name="StoreBackground",
        questions=[
            window_questions,
            tq.analysis_forecast_window_offset(),
            tq.background_experiment(),
            tq.background_frequency(),
            tq.horizontal_resolution(),
            tq.r2d2_local_path(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GenerateBClimatology = QuestionList(
        list_name="GenerateBClimatology",
        questions=[
            np_proc_resolution,
            swell_static_file_questions,
            tq.analysis_variables(),
            tq.background_error_model(),
            tq.generate_yaml_and_exit(),
            tq.marine_models(),
            tq.total_processors(),
            tq.window_offset(),
            tq.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediConvertStateSoca2ciceExecutable = QuestionList(
        list_name="RunJediConvertStateSoca2ciceExecutable",
        questions=[
            tq.analysis_variables(),
            tq.cice6_domains(),
            tq.generate_yaml_and_exit(),
            tq.jedi_forecast_model(),
            tq.marine_models(),
            tq.observations(),
            tq.total_processors(),
            tq.window_offset(),
            tq.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediEnsembleMeanVariance = QuestionList(
        list_name="RunJediEnsembleMeanVariance",
        questions=[
            np_proc_resolution,
            window_questions,
            tq.analysis_variables(),
            tq.ensemble_num_members(),
            tq.generate_yaml_and_exit(),
            tq.jedi_forecast_model(),
            tq.observations(),
            tq.observing_system_records_path(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediFgatExecutable = QuestionList(
        list_name="RunJediFgatExecutable",
        questions=[
            run_jedi_executable,
            tq.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediVariationalExecutable = QuestionList(
        list_name="RunJediVariationalExecutable",
        questions=[
            run_jedi_executable
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GenerateBClimatologyByLinking = QuestionList(
        list_name="GenerateBClimatologyByLinking",
        questions=[
            swell_static_file_questions,
            tq.background_error_model(),
            tq.horizontal_resolution(),
            tq.vertical_resolution(),
            tq.window_offset(),
            tq.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetBackgroundGeosExperiment = QuestionList(
        list_name="GetBackgroundGeosExperiment",
        questions=[
            tq.horizontal_resolution(),
            tq.background_experiment(),
            tq.background_time_offset(),
            tq.geos_x_background_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    LinkGeosOutput = QuestionList(
        list_name="LinkGeosOutput",
        questions=[
            window_questions,
            tq.background_frequency(),
            tq.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediHofxEnsembleExecutable = QuestionList(
        list_name="RunJediHofxEnsembleExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            tq.background_frequency(),
            tq.ensemble_hofx_packets(),
            tq.ensemble_hofx_strategy(),
            tq.ensemble_num_members(),
            tq.generate_yaml_and_exit(),
            tq.jedi_forecast_model(),
            tq.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediHofxExecutable = QuestionList(
        list_name="RunJediHofxExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            tq.background_frequency(),
            tq.generate_yaml_and_exit(),
            tq.jedi_forecast_model(),
            tq.observing_system_records_path(),
            tq.save_geovals(),
            tq.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediObsfiltersExecutable = QuestionList(
        list_name="RunJediObsfiltersExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            tq.background_frequency(),
            tq.generate_yaml_and_exit(),
            tq.jedi_forecast_model(),
            tq.observing_system_records_path(),
            tq.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaObservations = QuestionList(
        list_name="EvaObservations",
        questions=[
            background_crtm_obs,
            tq.observing_system_records_path(),
            tq.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGeovals = QuestionList(
        list_name="GetGeovals",
        questions=[
            background_crtm_obs,
            tq.geovals_experiment(),
            tq.geovals_provider(),
            tq.r2d2_local_path(),
            tq.window_length(),
            tq.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetObservations = QuestionList(
        list_name="GetObservations",
        questions=[
            background_crtm_obs,
            tq.cycling_varbc(),
            tq.obs_experiment(),
            tq.obs_provider(),
            tq.observing_system_records_path(),
            tq.r2d2_local_path(),
            tq.window_length(),
            tq.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GsiBcToIoda = QuestionList(
        list_name="GsiBcToIoda",
        questions=[
            background_crtm_obs,
            tq.observing_system_records_path(),
            tq.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediLocalEnsembleDaExecutable = QuestionList(
        list_name="RunJediLocalEnsembleDaExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            tq.ensemble_hofx_packets(),
            tq.ensemble_hofx_strategy(),
            tq.ensemble_num_members(),
            tq.ensmean_only(),
            tq.ensmeanvariance_only(),
            tq.generate_yaml_and_exit(),
            tq.horizontal_localization_lengthscale(),
            tq.horizontal_localization_max_nobs(),
            tq.horizontal_localization_method(),
            tq.jedi_forecast_model(),
            tq.local_ensemble_inflation_mult(),
            tq.local_ensemble_inflation_rtpp(),
            tq.local_ensemble_inflation_rtps(),
            tq.local_ensemble_save_posterior_ensemble(),
            tq.local_ensemble_save_posterior_ensemble_increments(),
            tq.local_ensemble_save_posterior_mean(),
            tq.local_ensemble_save_posterior_mean_increment(),
            tq.local_ensemble_solver(),
            tq.local_ensemble_use_linear_observer(),
            tq.observing_system_records_path(),
            tq.skip_ensemble_hofx(),
            tq.total_processors(),
            tq.vertical_localization_apply_log_transform(),
            tq.vertical_localization_function(),
            tq.vertical_localization_ioda_vertical_coord(),
            tq.vertical_localization_ioda_vertical_coord_group(),
            tq.vertical_localization_lengthscale(),
            tq.vertical_localization_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediUfoTestsExecutable = QuestionList(
        list_name="RunJediUfoTestsExecutable",
        questions=[
            background_crtm_obs,
            tq.generate_yaml_and_exit(),
            tq.observing_system_records_path(),
            tq.single_observations(),
            tq.window_length(),
            tq.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    SaveObsDiags = QuestionList(
        list_name="SaveObsDiags",
        questions=[
            background_crtm_obs,
            tq.observing_system_records_path(),
            tq.r2d2_local_path(),
            tq.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildJedi = QuestionList(
        list_name="BuildJedi",
        questions=[
            tq.bundles(),
            tq.jedi_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CloneJedi = QuestionList(
        list_name="CloneJedi",
        questions=[
            tq.bundles(),
            tq.existing_jedi_source_directory(),
            tq.existing_jedi_source_directory_pinned(),
            tq.jedi_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CleanCycle = QuestionList(
        list_name="CleanCycle",
        questions=[
            tq.clean_patterns()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildGeosByLinking = QuestionList(
        list_name="BuildGeosByLinking",
        questions=[
            tq.existing_geos_gcm_build_path(),
            tq.geos_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    PrepGeosRunDir = QuestionList(
        list_name="PrepGeosRunDir",
        questions=[
            swell_static_file_questions,
            tq.existing_geos_gcm_build_path(),
            tq.forecast_duration(),
            tq.geos_experiment_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CloneGeos = QuestionList(
        list_name="CloneGeos",
        questions=[
            tq.existing_geos_gcm_source_path(),
            tq.geos_build_method(),
            tq.geos_gcm_tag()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildJediByLinking = QuestionList(
        list_name="BuildJediByLinking",
        questions=[
            tq.existing_jedi_build_directory(),
            tq.existing_jedi_build_directory_pinned(),
            tq.jedi_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    MoveForecastRestart = QuestionList(
        list_name="MoveForecastRestart",
        questions=[
            tq.forecast_duration()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildGeos = QuestionList(
        list_name="BuildGeos",
        questions=[
            tq.geos_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGeosRestart = QuestionList(
        list_name="GetGeosRestart",
        questions=[
            swell_static_file_questions,
            tq.geos_restarts_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    StageJedi = QuestionList(
        list_name="StageJedi",
        questions=[
            swell_static_file_questions,
            tq.gsibec_configuration(),
            tq.horizontal_resolution(),
            tq.vertical_resolution()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaIncrement = QuestionList(
        list_name="EvaIncrement",
        questions=[
            tq.marine_models(),
            tq.window_offset(),
            tq.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GenerateObservingSystemRecords = QuestionList(
        list_name="GenerateObservingSystemRecords",
        questions=[
            tq.observations(),
            tq.observing_system_records_mksi_path(),
            tq.observing_system_records_path()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GsiNcdiagToIoda = QuestionList(
        list_name="GsiNcdiagToIoda",
        questions=[
            tq.observations(),
            tq.produce_geovals(),
            tq.single_observations(),
            tq.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CloneGeosMksi = QuestionList(
        list_name="CloneGeosMksi",
        questions=[
            tq.observing_system_records_mksi_path(),
            tq.observing_system_records_mksi_path_tag()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetEnsemble = QuestionList(
        list_name="GetEnsemble",
        questions=[
            tq.path_to_ensemble()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGeosAdasBackground = QuestionList(
        list_name="GetGeosAdasBackground",
        questions=[
            tq.path_to_geos_adas_background()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGsiBc = QuestionList(
        list_name="GetGsiBc",
        questions=[
            tq.path_to_gsi_bc_coefficients(),
            tq.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGsiNcdiag = QuestionList(
        list_name="GetGsiNcdiag",
        questions=[
            tq.path_to_gsi_nc_diags()
        ]
    )

# --------------------------------------------------------------------------------------------------
