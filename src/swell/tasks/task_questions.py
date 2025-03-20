# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from enum import Enum

from swell.utilities.swell_questions import QuestionList, QuestionContainer
from swell.utilities.question_defaults import QuestionDefaults as qd


# --------------------------------------------------------------------------------------------------

class TaskQuestions(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    window_questions = QuestionList(
        list_name="window_questions",
        questions=[
            qd.window_length(),
            qd.window_offset(),
            qd.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    np_proc_resolution = QuestionList(
        list_name="np_resolution",
        questions=[
            qd.npx_proc(),
            qd.npy_proc(),
            qd.horizontal_resolution(),
            qd.vertical_resolution()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    swell_static_file_questions = QuestionList(
        list_name="swell_static_file_questions",
        questions=[
            qd.swell_static_files(),
            qd.swell_static_files_user()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    background_crtm_obs = QuestionList(
        list_name="background_crtm_obs",
        questions=[
            qd.background_time_offset(),
            qd.crtm_coeff_dir(),
            qd.observations()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    run_jedi_executable = QuestionList(
        list_name="run_jedi_executable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            qd.analysis_variables(),
            qd.background_frequency(),
            qd.generate_yaml_and_exit(),
            qd.gradient_norm_reduction(),
            qd.gsibec_configuration(),
            qd.jedi_forecast_model(),
            qd.minimizer(),
            qd.number_of_iterations(),
            qd.observing_system_records_path(),
            qd.total_processors(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetBackground = QuestionList(
        list_name="GetBackground",
        questions=[
            window_questions,
            qd.analysis_forecast_window_offset(),
            qd.background_experiment(),
            qd.background_frequency(),
            qd.horizontal_resolution(),
            qd.r2d2_local_path(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    MoveDaRestart = QuestionList(
        list_name="MoveDaRestart",
        questions=[
            qd.analysis_forecast_window_offset(),
            qd.mom6_iau(),
            qd.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    PrepareAnalysis = QuestionList(
        list_name="PrepareAnalysis",
        questions=[
            qd.analysis_forecast_window_offset(),
            qd.analysis_variables(),
            qd.mom6_iau(),
            qd.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    StoreBackground = QuestionList(
        list_name="StoreBackground",
        questions=[
            window_questions,
            qd.analysis_forecast_window_offset(),
            qd.background_experiment(),
            qd.background_frequency(),
            qd.horizontal_resolution(),
            qd.r2d2_local_path(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GenerateBClimatology = QuestionList(
        list_name="GenerateBClimatology",
        questions=[
            np_proc_resolution,
            swell_static_file_questions,
            qd.analysis_variables(),
            qd.background_error_model(),
            qd.generate_yaml_and_exit(),
            qd.marine_models(),
            qd.total_processors(),
            qd.window_offset(),
            qd.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediConvertStateSoca2ciceExecutable = QuestionList(
        list_name="RunJediConvertStateSoca2ciceExecutable",
        questions=[
            qd.analysis_variables(),
            qd.generate_yaml_and_exit(),
            qd.jedi_forecast_model(),
            qd.marine_models(),
            qd.observations(),
            qd.total_processors(),
            qd.window_offset(),
            qd.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediEnsembleMeanVariance = QuestionList(
        list_name="RunJediEnsembleMeanVariance",
        questions=[
            np_proc_resolution,
            window_questions,
            qd.analysis_variables(),
            qd.ensemble_num_members(),
            qd.generate_yaml_and_exit(),
            qd.jedi_forecast_model(),
            qd.observations(),
            qd.observing_system_records_path(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediFgatExecutable = QuestionList(
        list_name="RunJediFgatExecutable",
        questions=[
            run_jedi_executable,
            qd.marine_models()
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
            qd.background_error_model(),
            qd.horizontal_resolution(),
            qd.vertical_resolution(),
            qd.window_offset(),
            qd.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetBackgroundGeosExperiment = QuestionList(
        list_name="GetBackgroundGeosExperiment",
        questions=[
            qd.horizontal_resolution(),
            qd.background_experiment(),
            qd.background_time_offset(),
            qd.geos_x_background_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    LinkGeosOutput = QuestionList(
        list_name="LinkGeosOutput",
        questions=[
            window_questions,
            qd.background_frequency(),
            qd.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediHofxEnsembleExecutable = QuestionList(
        list_name="RunJediHofxEnsembleExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            qd.background_frequency(),
            qd.ensemble_hofx_packets(),
            qd.ensemble_hofx_strategy(),
            qd.ensemble_num_members(),
            qd.generate_yaml_and_exit(),
            qd.jedi_forecast_model(),
            qd.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediHofxExecutable = QuestionList(
        list_name="RunJediHofxExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            qd.background_frequency(),
            qd.generate_yaml_and_exit(),
            qd.jedi_forecast_model(),
            qd.observing_system_records_path(),
            qd.save_geovals(),
            qd.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediObsfiltersExecutable = QuestionList(
        list_name="RunJediObsfiltersExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            qd.background_frequency(),
            qd.generate_yaml_and_exit(),
            qd.jedi_forecast_model(),
            qd.observing_system_records_path(),
            qd.total_processors()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaObservations = QuestionList(
        list_name="EvaObservations",
        questions=[
            background_crtm_obs,
            qd.marine_models(),
            qd.observing_system_records_path(),
            qd.window_offset(),
            qd.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGeovals = QuestionList(
        list_name="GetGeovals",
        questions=[
            background_crtm_obs,
            qd.geovals_experiment(),
            qd.geovals_provider(),
            qd.r2d2_local_path(),
            qd.window_length(),
            qd.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetObservations = QuestionList(
        list_name="GetObservations",
        questions=[
            background_crtm_obs,
            qd.cycling_varbc(),
            qd.obs_experiment(),
            qd.obs_provider(),
            qd.observing_system_records_path(),
            qd.r2d2_local_path(),
            qd.window_length(),
            qd.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GsiBcToIoda = QuestionList(
        list_name="GsiBcToIoda",
        questions=[
            background_crtm_obs,
            qd.observing_system_records_path(),
            qd.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediLocalEnsembleDaExecutable = QuestionList(
        list_name="RunJediLocalEnsembleDaExecutable",
        questions=[
            np_proc_resolution,
            window_questions,
            background_crtm_obs,
            qd.ensemble_hofx_packets(),
            qd.ensemble_hofx_strategy(),
            qd.ensemble_num_members(),
            qd.ensmean_only(),
            qd.ensmeanvariance_only(),
            qd.generate_yaml_and_exit(),
            qd.horizontal_localization_lengthscale(),
            qd.horizontal_localization_max_nobs(),
            qd.horizontal_localization_method(),
            qd.jedi_forecast_model(),
            qd.local_ensemble_inflation_mult(),
            qd.local_ensemble_inflation_rtpp(),
            qd.local_ensemble_inflation_rtps(),
            qd.local_ensemble_save_posterior_ensemble(),
            qd.local_ensemble_save_posterior_ensemble_increments(),
            qd.local_ensemble_save_posterior_mean(),
            qd.local_ensemble_save_posterior_mean_increment(),
            qd.local_ensemble_solver(),
            qd.local_ensemble_use_linear_observer(),
            qd.observing_system_records_path(),
            qd.skip_ensemble_hofx(),
            qd.total_processors(),
            qd.vertical_localization_apply_log_transform(),
            qd.vertical_localization_function(),
            qd.vertical_localization_ioda_vertical_coord(),
            qd.vertical_localization_ioda_vertical_coord_group(),
            qd.vertical_localization_lengthscale(),
            qd.vertical_localization_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediUfoTestsExecutable = QuestionList(
        list_name="RunJediUfoTestsExecutable",
        questions=[
            background_crtm_obs,
            qd.generate_yaml_and_exit(),
            qd.observing_system_records_path(),
            qd.single_observations(),
            qd.window_length(),
            qd.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    SaveObsDiags = QuestionList(
        list_name="SaveObsDiags",
        questions=[
            background_crtm_obs,
            qd.observing_system_records_path(),
            qd.r2d2_local_path(),
            qd.window_offset(),
            qd.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildJedi = QuestionList(
        list_name="BuildJedi",
        questions=[
            qd.bundles(),
            qd.jedi_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CloneJedi = QuestionList(
        list_name="CloneJedi",
        questions=[
            qd.bundles(),
            qd.existing_jedi_source_directory(),
            qd.existing_jedi_source_directory_pinned(),
            qd.jedi_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CleanCycle = QuestionList(
        list_name="CleanCycle",
        questions=[
            qd.clean_patterns()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildGeosByLinking = QuestionList(
        list_name="BuildGeosByLinking",
        questions=[
            qd.existing_geos_gcm_build_path(),
            qd.geos_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    PrepGeosRunDir = QuestionList(
        list_name="PrepGeosRunDir",
        questions=[
            swell_static_file_questions,
            qd.existing_geos_gcm_build_path(),
            qd.forecast_duration(),
            qd.geos_experiment_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CloneGeos = QuestionList(
        list_name="CloneGeos",
        questions=[
            qd.existing_geos_gcm_source_path(),
            qd.geos_build_method(),
            qd.geos_gcm_tag()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildJediByLinking = QuestionList(
        list_name="BuildJediByLinking",
        questions=[
            qd.existing_jedi_build_directory(),
            qd.existing_jedi_build_directory_pinned(),
            qd.jedi_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    MoveForecastRestart = QuestionList(
        list_name="MoveForecastRestart",
        questions=[
            qd.forecast_duration()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    BuildGeos = QuestionList(
        list_name="BuildGeos",
        questions=[
            qd.geos_build_method()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGeosRestart = QuestionList(
        list_name="GetGeosRestart",
        questions=[
            swell_static_file_questions,
            qd.geos_restarts_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    StageJedi = QuestionList(
        list_name="StageJedi",
        questions=[
            swell_static_file_questions,
            qd.gsibec_configuration(),
            qd.horizontal_resolution(),
            qd.vertical_resolution()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaIncrement = QuestionList(
        list_name="EvaIncrement",
        questions=[
            qd.marine_models(),
            qd.window_offset(),
            qd.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GenerateObservingSystemRecords = QuestionList(
        list_name="GenerateObservingSystemRecords",
        questions=[
            qd.observations(),
            qd.observing_system_records_mksi_path(),
            qd.observing_system_records_path()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GsiNcdiagToIoda = QuestionList(
        list_name="GsiNcdiagToIoda",
        questions=[
            qd.observations(),
            qd.produce_geovals(),
            qd.single_observations(),
            qd.window_offset()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CloneGeosMksi = QuestionList(
        list_name="CloneGeosMksi",
        questions=[
            qd.observing_system_records_mksi_path(),
            qd.observing_system_records_mksi_path_tag()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetEnsemble = QuestionList(
        list_name="GetEnsemble",
        questions=[
            qd.path_to_ensemble()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGeosAdasBackground = QuestionList(
        list_name="GetGeosAdasBackground",
        questions=[
            qd.path_to_geos_adas_background()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGsiBc = QuestionList(
        list_name="GetGsiBc",
        questions=[
            qd.path_to_gsi_bc_coefficients(),
            qd.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGsiNcdiag = QuestionList(
        list_name="GetGsiNcdiag",
        questions=[
            qd.path_to_gsi_nc_diags()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    SaveRestart = QuestionList(
        list_name="SaveRestart",
        questions=[
            window_questions,
            qd.background_time_offset(),
            qd.forecast_duration(),
            qd.horizontal_resolution(),
            qd.marine_models(),
            qd.r2d2_local_path()
        ]
    )

    # --------------------------------------------------------------------------------------------------
