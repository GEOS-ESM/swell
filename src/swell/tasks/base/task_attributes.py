# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.tasks.base.task_setup import TaskSetup
from swell.utilities.swell_questions import QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd

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


class TaskAttributes():

    # --------------------------------------------------------------------------------------------------

    class root(TaskSetup):

        def set_attributes(self):
            self.script = False
            self.pre_script = "source $CYLC_SUITE_DEF_PATH/modules"
            self.additional_sections = [self.create_new_section('environment',
                                             {'datetime': '$CYLC_TASK_CYCLE_POINT',
                                              'config': '$CYLC_SUITE_DEF_PATH/experiment.yaml'})]  # noqa

    # --------------------------------------------------------------------------------------------------

    class BuildGeos(TaskSetup):
        def set_attributes(self):
            self.questions = [
                qd.geos_build_method()
            ]

    # --------------------------------------------------------------------------------------------------

    class BuildGeosByLinking(TaskSetup):
        def set_attributes(self):
            self.mail_events = ['submit-failed']
            self.questions = [
                qd.existing_geos_gcm_build_path(),
                qd.geos_build_method()
            ]

    # --------------------------------------------------------------------------------------------------

    class BuildJediByLinking(TaskSetup):
        def set_attributes(self):
            self.mail_events = ['submit-failed']
            self.questions = [
                qd.existing_jedi_build_directory(),
                qd.existing_jedi_build_directory_pinned(),
                qd.jedi_build_method()
            ]

    # --------------------------------------------------------------------------------------------------

    class BuildJedi(TaskSetup):
        def set_attributes(self):
            self.time_limit = True
            self.slurm = {}
            self.questions = [
                qd.bundles(),
                qd.jedi_build_method()
            ]

    # --------------------------------------------------------------------------------------------------

    class CleanCycle(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.clean_patterns()
            ]

    # --------------------------------------------------------------------------------------------------

    class CloneGeos(TaskSetup):
        def set_attributes(self):
            self.questions = [
                qd.existing_geos_gcm_source_path(),
                qd.geos_build_method(),
                qd.geos_gcm_tag()
            ]

    # --------------------------------------------------------------------------------------------------

    class CloneJedi(TaskSetup):
        def set_attributes(self):
            self.questions = [
                qd.bundles(),
                qd.existing_jedi_source_directory(),
                qd.existing_jedi_source_directory_pinned(),
                qd.jedi_build_method()
            ]

    # --------------------------------------------------------------------------------------------------

    class CloneGeosMksi(TaskSetup):
        def set_attributes(self):
            self.is_model = True
            self.questions = [
                qd.observing_system_records_mksi_path(),
                qd.observing_system_records_mksi_path_tag()
            ]

    # --------------------------------------------------------------------------------------------------

    class CloneGmaoPerllib(TaskSetup):
        def set_attributes(self):
            self.questions = [
                qd.existing_perllib_path(),
                qd.gmao_perllib_tag()
            ]

    # --------------------------------------------------------------------------------------------------

    class EvaJediLog(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True

    # --------------------------------------------------------------------------------------------------

    class EvaComparisonIncrement(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.marine_models(),
                qd.window_length(),
                qd.window_type()
            ]

    # --------------------------------------------------------------------------------------------------

    class EvaComparisonJediLog(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.comparison_log_type()
            ]

    # --------------------------------------------------------------------------------------------------

    class EvaIncrement(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.marine_models(),
                qd.window_length(),
                qd.window_type()
            ]

    # --------------------------------------------------------------------------------------------------

    class EvaObservations(TaskSetup):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {}
            self.questions = [
                background_crtm_obs,
                qd.marine_models(),
                qd.observing_system_records_path(),
                qd.window_length(),
                qd.marine_models(),
            ]

    # --------------------------------------------------------------------------------------------------

    class EvaTimeseries(TaskSetup):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {}
            self.questions = [
                background_crtm_obs,
                qd.window_length(),
                qd.ncdiag_experiments(),
                qd.marine_models(),
            ]

    # --------------------------------------------------------------------------------------------------

    class JediOopsLogParser(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.parser_options(),
                qd.comparison_log_type()
            ]

    # --------------------------------------------------------------------------------------------------

    class GetBackground(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                window_questions,
                qd.window_length(),
                qd.background_experiment(),
                qd.background_frequency(),
                qd.horizontal_resolution(),
                qd.marine_models(),
                qd.r2d2_local_path(),
            ]

    # --------------------------------------------------------------------------------------------------

    class GetBackgroundGeosExperiment(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.mail_events = ['submit-failed']
            self.questions = [
                qd.horizontal_resolution(),
                qd.background_experiment(),
                qd.background_time_offset(),
                qd.geos_x_background_directory()
            ]

    # --------------------------------------------------------------------------------------------------

    class GetBufr(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.bufr_obs_classes()
            ]

    # --------------------------------------------------------------------------------------------------

    class BufrToIoda(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True

    # --------------------------------------------------------------------------------------------------

    class GetEnsembleGeosExperiment(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.background_experiment(),
                qd.background_time_offset(),
                qd.geos_x_ensemble_directory()
            ]

    # --------------------------------------------------------------------------------------------------

    class GetGeosRestart(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.questions = [
                swell_static_file_questions,
                qd.geos_restarts_directory()
            ]

    # --------------------------------------------------------------------------------------------------

    class GetGeovals(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                background_crtm_obs,
                qd.geovals_experiment(),
                qd.geovals_provider(),
                qd.r2d2_local_path(),
                qd.window_length(),
            ]

    # --------------------------------------------------------------------------------------------------

    class GetGsiBc(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.path_to_gsi_bc_coefficients(),
                qd.window_length()
            ]

    # --------------------------------------------------------------------------------------------------

    class GsiBcToIoda(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                background_crtm_obs,
                qd.observing_system_records_path(),
                qd.window_length()
            ]

    # --------------------------------------------------------------------------------------------------

    class GetGsiNcdiag(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.path_to_gsi_nc_diags()
            ]

    # --------------------------------------------------------------------------------------------------

    class GsiNcdiagToIoda(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.observations(),
                qd.produce_geovals(),
                qd.single_observations(),
                qd.window_length()
            ]

    # --------------------------------------------------------------------------------------------------

    class GetNcdiags(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                background_crtm_obs,
                qd.ncdiag_experiments(),
                qd.marine_models(),
                qd.r2d2_local_path(),
                qd.window_length(),
            ]

    # --------------------------------------------------------------------------------------------------

    class GetGeosAdasBackground(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.path_to_geos_adas_background()
            ]

    # --------------------------------------------------------------------------------------------------

    class GetObservations(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                background_crtm_obs,
                qd.cycling_varbc(),
                qd.obs_experiment(),
                qd.observing_system_records_path(),
                qd.r2d2_local_path(),
                qd.window_length(),
            ]

    # --------------------------------------------------------------------------------------------------

    class GetObsNotInR2d2(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.mail_events = ['submit-failed']
            self.questions = [
                qd.ioda_locations_not_in_r2d2(),
            ]

    # --------------------------------------------------------------------------------------------------

    class GenerateBClimatology(TaskSetup):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.retry = '2*PT1M'
            self.slurm = {}
            self.questions = [
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

    # --------------------------------------------------------------------------------------------------

    class GenerateBClimatologyByLinking(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                swell_static_file_questions,
                qd.background_error_model(),
                qd.horizontal_resolution(),
                qd.vertical_resolution(),
                qd.window_length(),
                qd.window_type()
            ]

    # --------------------------------------------------------------------------------------------------

    class GenerateObservingSystemRecords(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.observations(),
                qd.observing_system_records_mksi_path(),
                qd.observing_system_records_path()
            ]

    # --------------------------------------------------------------------------------------------------

    class LinkGeosOutput(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                window_questions,
                qd.background_frequency(),
                qd.marine_models()
            ]

    # --------------------------------------------------------------------------------------------------

    class MoveDaRestart(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.mom6_iau(),
                qd.window_length()
            ]

    # --------------------------------------------------------------------------------------------------

    class MoveForecastRestart(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.questions = [
                qd.forecast_duration()
            ]

    # --------------------------------------------------------------------------------------------------

    class PrepGeosRunDir(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.questions = [
                swell_static_file_questions,
                qd.existing_geos_gcm_build_path(),
                qd.forecast_duration(),
                qd.geos_experiment_directory(),
                qd.mom6_iau_nhours()
            ]

    # --------------------------------------------------------------------------------------------------

    class PrepareAnalysis(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                qd.analysis_variables(),
                qd.mom6_iau(),
                qd.total_processors(),
                qd.window_length(),
            ]

    # --------------------------------------------------------------------------------------------------

    class RunJediFgatExecutable(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.questions = [
                run_jedi_executable,
                qd.marine_models(),
                qd.comparison_log_type('fgat'),
            ]

    # --------------------------------------------------------------------------------------------------

    class RunJediEnsembleMeanVariance(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.questions = [
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

    # --------------------------------------------------------------------------------------------------

    class RunJediHofxEnsembleExecutable(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.questions = [
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
                qd.comparison_log_type('hofx'),
            ]

    # --------------------------------------------------------------------------------------------------

    class RunJediHofxExecutable(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.questions = [
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

    # --------------------------------------------------------------------------------------------------

    class RunJediLocalEnsembleDaExecutable(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.questions = [
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

    # --------------------------------------------------------------------------------------------------

    class RunJediVariationalExecutable(TaskSetup):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {'nodes': 3}
            self.questions = [
                run_jedi_executable,
                qd.perhost(),
                qd.comparison_log_type('variational'),
            ]

    # --------------------------------------------------------------------------------------------------

    class RemoveForecastDir(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True

    # --------------------------------------------------------------------------------------------------

    class RunGeosExecutable(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True

    # --------------------------------------------------------------------------------------------------

    class RunJediUfoTestsExecutable(TaskSetup):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {'ntasks-per-node': 1}
            self.questions = [
                background_crtm_obs,
                qd.generate_yaml_and_exit(),
                qd.single_observations(),
                qd.window_length(),
                qd.comparison_log_type('ufo_tests'),
            ]

    # --------------------------------------------------------------------------------------------------

    class RunJediConvertStateSoca2ciceExecutable(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {'nodes': 1}
            self.questions = [
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

    # --------------------------------------------------------------------------------------------------

    class RunJediFgatExecutable(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.questions = [
                run_jedi_executable,
                qd.marine_models(),
                qd.comparison_log_type('fgat'),
            ]

    # --------------------------------------------------------------------------------------------------

    class SaveObsDiags(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                background_crtm_obs,
                qd.r2d2_local_path(),
                qd.window_length(),
                qd.marine_models()
            ]

    # --------------------------------------------------------------------------------------------------

    class SaveRestart(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.questions = [
                window_questions,
                qd.background_time_offset(),
                qd.forecast_duration(),
                qd.horizontal_resolution(),
                qd.marine_models(),
                qd.r2d2_local_path()
            ]

    # --------------------------------------------------------------------------------------------------

    class StageJedi(TaskSetup):
        def set_attributes(self):
            self.is_model = True
            self.questions = [
                swell_static_file_questions,
                qd.gsibec_configuration(),
                qd.gsibec_nlats(),
                qd.gsibec_nlons(),
                qd.horizontal_resolution(),
                qd.vertical_resolution()
            ]

    # --------------------------------------------------------------------------------------------------

    class StageJediCycle(TaskSetup):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.base_name = "StageJedi"
            self.scheduling_name = "StageJediCycle-{model}"
            self.questions = [
                swell_static_file_questions,
                qd.gsibec_configuration(),
                qd.gsibec_nlats(),
                qd.gsibec_nlons(),
                qd.horizontal_resolution(),
                qd.vertical_resolution()
            ]

    # --------------------------------------------------------------------------------------------------

    class sync_point(TaskSetup):
        def set_attributes(self):
            self.script = "true"

    # --------------------------------------------------------------------------------------------------

    class JediLogComparison(TaskSetup):
        def set_attributes(self):
            self.is_model = True
            self.questions = [
                qd.number_of_iterations(),
                qd.comparison_log_type(),
            ]

    # --------------------------------------------------------------------------------------------------

    class RunJediObsfiltersExecutable(TaskSetup):
        def set_attributes(self):
            self.script = ("swell task RunJediObsfiltersExecutable $config"
                           " -d $datetime -m geos_atmosphere")
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.questions = [
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

    # --------------------------------------------------------------------------------------------------

    @classmethod
    def get(cls, name: str) -> TaskSetup:
        return getattr(cls, name)

# --------------------------------------------------------------------------------------------
