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
    # Helper question lists used by multiple tasks (in order of use)
    # --------------------------------------------------------------------------------------------------

    background_crtm_obs = QuestionList(
        list_name="background_crtm_obs",
        questions=[
            qd.background_time_offset(),
            qd.crtm_coeff_dir(),
            qd.observations(),
            qd.observing_system_records_path()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    np_proc_resolution = QuestionList(
        list_name="np_resolution",
        questions=[
            qd.npx_proc(),
            qd.npy_proc(),
            qd.npx(),
            qd.npy(),
            qd.horizontal_resolution(),
            qd.vertical_resolution()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    window_questions = QuestionList(
        list_name="window_questions",
        questions=[
            qd.window_length(),
            qd.window_type()
        ]
    )
    # --------------------------------------------------------------------------------------------------

    geos_gcm_questions = QuestionList(
        list_name="geos_gcm_questions",
        questions=[
            qd.geos_homdir(),
            qd.geos_expdir_different(),
            qd.geos_expdir(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    run_jedi_executable = QuestionList(
        list_name="run_jedi_executable",
        questions=[
            background_crtm_obs,
            np_proc_resolution,
            window_questions,
            qd.analysis_variables(),
            qd.background_frequency(),
            qd.generate_yaml_and_exit(),
            qd.gradient_norm_reduction(),
            qd.gsibec_configuration(),
            qd.jedi_forecast_model(),
            qd.minimizer(),
            qd.gsibec_nlats(),
            qd.gsibec_nlons(),
            qd.number_of_iterations(),
            qd.total_processors(),
            qd.saber_central_block(),
            qd.saber_outer_block(),
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
    # Task-specific question lists (in alphabetical order)
    # --------------------------------------------------------------------------------------------------

    BuildGeos = QuestionList(
        list_name="BuildGeos",
        questions=[
            qd.geos_build_method()
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

    BuildJedi = QuestionList(
        list_name="BuildJedi",
        questions=[
            qd.bundles(),
            qd.jedi_build_method()
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

    CleanCycle = QuestionList(
        list_name="CleanCycle",
        questions=[
            qd.clean_patterns()
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

    CloneGeosMksi = QuestionList(
        list_name="CloneGeosMksi",
        questions=[
            qd.observing_system_records_mksi_path(),
            qd.observing_system_records_mksi_path_tag()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    CloneGmaoPerllib = QuestionList(
        list_name="CloneGmaoPerllib",
        questions=[
            qd.existing_perllib_path(),
            qd.gmao_perllib_tag()
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

    ConvertObsToIoda = QuestionList(
        list_name="ConvertObsToIoda",
        questions=[
            qd.converter_path(),
            qd.dry_run(),
            qd.obs_to_download(),
            qd.window_length(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    DownloadObs = QuestionList(
        list_name="DownloadObs",
        questions=[
            qd.dry_run(),
            qd.obs_to_download(),
            qd.window_length(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaComparisonJediLog = QuestionList(
        list_name="EvaJediLog",
        questions=[
            qd.comparison_log_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaComparisonObservations = QuestionList(
        list_name="EvaComparisonObservations",
        questions=[
            qd.comparison_log_type(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaIncrement = QuestionList(
        list_name="EvaIncrement",
        questions=[
            qd.marine_models(),
            qd.window_length(),
            qd.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaObservations = QuestionList(
        list_name="EvaObservations",
        questions=[
            background_crtm_obs,
            qd.marine_models(),
            qd.observing_system_records_path(),
            qd.window_length(),
            qd.marine_models(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    EvaTimeseries = QuestionList(
        list_name="EvaTimeseries",
        questions=[
            background_crtm_obs,
            qd.window_length(),
            qd.ncdiag_experiments(),
            qd.marine_models(),
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
            qd.gradient_norm_reduction(),
            qd.gsibec_configuration(),
            qd.gsibec_nlats(),
            qd.gsibec_nlons(),
            qd.jedi_forecast_model(),
            qd.marine_models(),
            qd.minimizer(),
            qd.number_of_iterations(),
            qd.observing_system_records_path(),
            qd.total_processors(),
            qd.window_length(),
            qd.window_type()
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

    GetBackground = QuestionList(
        list_name="GetBackground",
        questions=[
            window_questions,
            qd.background_experiment(),
            qd.background_frequency(),
            qd.horizontal_resolution(),
            qd.marine_models(),
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

    GetBufr = QuestionList(
        list_name="GetBufr",
        questions=[
            qd.bufr_obs_classes()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetCoupledGeosRestart = QuestionList(
        list_name="GetCoupledGeosRestart",
        questions=[
            geos_gcm_questions,
            qd.initial_restarts_method(),
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

    GetEnsembleGeosExperiment = QuestionList(
        list_name="GetEnsembleGeosExperiment",
        questions=[
            qd.background_experiment(),
            qd.background_time_offset(),
            qd.geos_x_ensemble_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetGeovals = QuestionList(
        list_name="GetGeovals",
        questions=[
            background_crtm_obs,
            qd.geovals_experiment(),
            qd.geovals_provider(),
            qd.window_length(),
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

    GetNcdiags = QuestionList(
        list_name="GetNcdiags",
        questions=[
            background_crtm_obs,
            qd.ncdiag_experiments(),
            qd.marine_models(),
            qd.window_length(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetObservations = QuestionList(
        list_name="GetObservations",
        questions=[
            background_crtm_obs,
            qd.cache_fetch(),
            qd.cycling_varbc(),
            qd.obs_experiment(),
            qd.observing_system_records_path(),
            qd.window_length(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GetObsNotInR2d2 = QuestionList(
        list_name="GetExistingObservations",
        questions=[
            qd.ioda_locations_not_in_r2d2(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GsiBcToIoda = QuestionList(
        list_name="GsiBcToIoda",
        questions=[
            background_crtm_obs,
            qd.observing_system_records_path(),
            qd.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    GsiNcdiagToIoda = QuestionList(
        list_name="GsiNcdiagToIoda",
        questions=[
            qd.observations(),
            qd.produce_geovals(),
            qd.single_observations(),
            qd.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    IngestObs = QuestionList(
        list_name="IngestObs",
        questions=[
            qd.dry_run(),
            qd.obs_to_ingest(),
            qd.window_length(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    JediLogComparison = QuestionList(
        list_name="JediComparisonLog",
        questions=[
            qd.comparison_log_type(),
            qd.number_of_iterations()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    JediOopsLogParser = QuestionList(
        list_name="JediOopsLogParser",
        questions=[
            qd.comparison_log_type(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    LinkCoupledGeosOutput = QuestionList(
        list_name="LinkCoupledGeosOutput",
        questions=[
            window_questions,
            qd.background_frequency(),
            qd.marine_models()
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

    MoveEraseDaRestart = QuestionList(
        list_name="MoveEraseDaRestart",
        questions=[
            qd.mom6_iau(),
            qd.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    MoveDaRestart = QuestionList(
        list_name="MoveDaRestart",
        questions=[
            qd.mom6_iau(),
            qd.window_length()
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

    PublishComparisons = QuestionList(
        list_name="PublishComparisons",
        questions=[
            qd.model_components(),
            qd.publish_directory()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    PrepareAnalysis = QuestionList(
        list_name="PrepareAnalysis",
        questions=[
            qd.analysis_variables(),
            qd.mom6_iau(),
            qd.total_processors(),
            qd.window_length()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    PrepCoupledGeosRunDir = QuestionList(
        list_name="PrepCoupledGeosRunDir",
        questions=[
            swell_static_file_questions,
            geos_gcm_questions,
            qd.existing_geos_gcm_build_path(),
            qd.forecast_duration(),
            qd.mom6_iau_nhours()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RenderJediObservations = QuestionList(
        list_name="RenderJediObservations",
        questions=[
            qd.check_for_obs(),
            qd.crtm_coeff_dir(),
            qd.background_time_offset(),
            qd.observing_system_records_path(),
            qd.observations(),
            qd.window_length()
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
            qd.window_length(),
            qd.window_type(),
            qd.comparison_log_type('convert_state_soca2cice'),
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
            qd.comparison_log_type('ensmeanvariance'),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediFgatExecutable = QuestionList(
        list_name="RunJediFgatExecutable",
        questions=[
            run_jedi_executable,
            qd.marine_models(),
            qd.comparison_log_type('fgat')
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
            qd.total_processors(),
            qd.comparison_log_type('hofx')
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
            qd.save_geovals(),
            qd.total_processors(),
            qd.comparison_log_type('ensemblehofx'),
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
            qd.skip_ensemble_hofx(),
            qd.total_processors(),
            qd.vertical_localization_apply_log_transform(),
            qd.vertical_localization_function(),
            qd.vertical_localization_ioda_vertical_coord(),
            qd.vertical_localization_ioda_vertical_coord_group(),
            qd.vertical_localization_lengthscale(),
            qd.vertical_localization_method(),
            qd.perhost(),
            qd.comparison_log_type('localensembleda'),
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
            qd.total_processors(),
            qd.obs_thinning_rej_fraction(),
            qd.comparison_log_type('obsfilters')
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediUfoTestsExecutable = QuestionList(
        list_name="RunJediUfoTestsExecutable",
        questions=[
            background_crtm_obs,
            qd.generate_yaml_and_exit(),
            qd.single_observations(),
            qd.window_length(),
            qd.comparison_log_type('ufo_tests'),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    RunJediVariationalExecutable = QuestionList(
        list_name="RunJediVariationalExecutable",
        questions=[
            run_jedi_executable,
            qd.perhost(),
            qd.comparison_log_type('variational'),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    SaveObsDiags = QuestionList(
        list_name="SaveObsDiags",
        questions=[
            background_crtm_obs,
            qd.window_length(),
            qd.marine_models()
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
        ]
    )

    # --------------------------------------------------------------------------------------------------

    StageJedi = QuestionList(
        list_name="StageJedi",
        questions=[
            swell_static_file_questions,
            qd.npx_proc(),
            qd.npy_proc(),
            qd.gsibec_configuration(),
            qd.gsibec_nlats(),
            qd.gsibec_nlons(),
            qd.horizontal_resolution(),
            qd.saber_central_block(),
            qd.vertical_resolution()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    StoreBackground = QuestionList(
        list_name="StoreBackground",
        questions=[
            window_questions,
            qd.background_experiment(),
            qd.background_frequency(),
            qd.horizontal_resolution(),
        ]
    )

    # --------------------------------------------------------------------------------------------------
