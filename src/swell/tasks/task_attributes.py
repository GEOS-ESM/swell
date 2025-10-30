# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self
from collections.abc import Mapping

from swell.utilities.task_spec import Task
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
        qd.horizontal_resolution(),
        qd.vertical_resolution()
    ]
)

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

    class root(Task):

        def set_attributes(self):
            self.script = False
            self.pre_script = "source $CYLC_SUITE_DEF_PATH/modules"
            self.addional_sections = [self.create_new_section('environment', {'datetime': '$CYLC_TASK_CYCLE_POINT',
                                                                              'config': '$CYLC_SUITE_DEF_PATH/experiment.yaml'})]

    # --------------------------------------------------------------------------------------------------            

    class BuildGeos(Task):
        def set_attributes(self):
            self.question_list = QuestionList([
                qd.geos_build_method()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class BuildGeosByLinking(Task):
        def set_attributes(self):
            self.mail_events = ['submit-failed']
            self.question_list = QuestionList([
                qd.existing_geos_gcm_build_path(),
                qd.geos_build_method()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class BuildJediByLinking(Task):
        def set_attributes(self):
            self.mail_events = ['submit-failed']
            self.question_list = QuestionList([
                qd.existing_jedi_build_directory(),
                qd.existing_jedi_build_directory_pinned(),
                qd.jedi_build_method()
            ])

    # --------------------------------------------------------------------------------------------------

    class BuildJedi(Task):
        def set_attributes(self):
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
                qd.bundles(),
                qd.jedi_build_method()
            ])

    # --------------------------------------------------------------------------------------------------

    class CleanCycle(Task):
        def set_attributes(self):

            self.is_cycling = True
            self.is_model = True

            self.question_list = QuestionList([
                qd.clean_patterns()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class CloneGeos(Task):
        def set_attributes(self):
            self.question_list = QuestionList([
                qd.existing_geos_gcm_source_path(),
                qd.geos_build_method(),
                qd.geos_gcm_tag()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class CloneJedi(Task):
        def set_attributes(self):
            self.self.question_list = QuestionList([
                qd.bundles(),
                qd.existing_jedi_source_directory(),
                qd.existing_jedi_source_directory_pinned(),
                qd.jedi_build_method()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class CloneGeosMksi(Task):
        def set_attributes(self):
            self.is_model = True
            self.question_list = QuestionList([
                qd.observing_system_records_mksi_path(),
                qd.observing_system_records_mksi_path_tag()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class CloneGmaoPerllib(Task):
        def set_attributes(self):
            self.question_list = QuestionList([
                qd.existing_perllib_path(),
                qd.gmao_perllib_tag()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class EvaJediLog(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True

    # --------------------------------------------------------------------------------------------------
    
    class EvaComparisonIncrement(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.marine_models(),
                qd.window_offset(),
                qd.window_type()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class EvaComparisonJediLog(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True

    # --------------------------------------------------------------------------------------------------
    
    class EvaIncrement(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.marine_models(),
                qd.window_offset(),
                qd.window_type()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class EvaObservations(Task):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {}
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.marine_models(),
                qd.observing_system_records_path(),
                qd.window_offset(),
                qd.marine_models(),
            ])
    
    # --------------------------------------------------------------------------------------------------

    class EvaTimeseries(Task):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {}
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.window_length(),
                qd.window_offset(),
                qd.ncdiag_experiments(),
                qd.marine_models(),
            ])
    
    # --------------------------------------------------------------------------------------------------

    class JediOopsLogParser(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.parser_options(),
            ])

    # --------------------------------------------------------------------------------------------------
    
    class GetBackground(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                window_questions,
                qd.analysis_forecast_window_offset(),
                qd.background_experiment(),
                qd.background_frequency(),
                qd.horizontal_resolution(),
                qd.marine_models(),
                qd.r2d2_local_path(),
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GetBackgroundGeosExperiment(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.mail_events = ['submit-failed']
            self.question_list = QuestionList([
                qd.horizontal_resolution(),
                qd.background_experiment(),
                qd.background_time_offset(),
                qd.geos_x_background_directory()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GetBufr(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.bufr_obs_classes()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class BufrToIoda(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True

    # --------------------------------------------------------------------------------------------------
    
    class GetEnsembleGeosExperiment(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.background_experiment(),
                qd.background_time_offset(),
                qd.geos_x_ensemble_directory()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class GetGeosRestart(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.question_list = QuestionList([
                swell_static_file_questions,
                qd.geos_restarts_directory()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GetGeovals(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.geovals_experiment(),
                qd.geovals_provider(),
                qd.r2d2_local_path(),
                qd.window_length(),
                qd.window_offset()
            ])

    # --------------------------------------------------------------------------------------------------

    class GetGsiBc(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.path_to_gsi_bc_coefficients(),
                qd.window_length()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GsiBcToIoda(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.observing_system_records_path(),
                qd.window_offset()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GetGsiNcdiag(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.path_to_gsi_nc_diags()
            ])

    # --------------------------------------------------------------------------------------------------
    
    class GsiNcdiagToIoda(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.observations(),
                qd.produce_geovals(),
                qd.single_observations(),
                qd.window_offset()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GetNcdiags(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.ncdiag_experiments(),
                qd.marine_models(),
                qd.r2d2_local_path(),
                qd.window_length(),
                qd.window_offset(),
            ])

    # --------------------------------------------------------------------------------------------------
    
    class GetGeosAdasBackground(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.path_to_geos_adas_background()
            ])

    # --------------------------------------------------------------------------------------------------

    class GetObservations(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.cycling_varbc(),
                qd.obs_experiment(),
                qd.obs_provider(),
                qd.observing_system_records_path(),
                qd.r2d2_local_path(),
                qd.window_length(),
                qd.window_offset(),
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GetObsNotInR2d2(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.mail_events = ['submit-failed']
            self.question_list = QuestionList([
                qd.ioda_locations_not_in_r2d2(),
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GenerateBClimatology(Task):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {}
            self.question_list = QuestionList([
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
                qd.window_offset(),
                qd.window_type()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GenerateBClimatologyByLinking(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                swell_static_file_questions,
                qd.background_error_model(),
                qd.horizontal_resolution(),
                qd.vertical_resolution(),
                qd.window_offset(),
                qd.window_type()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class GenerateObservingSystemRecords(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.observations(),
                qd.observing_system_records_mksi_path(),
                qd.observing_system_records_path()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class LinkGeosOutput(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                window_questions,
                qd.background_frequency(),
                qd.marine_models()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class MoveDaRestart(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.analysis_forecast_window_offset(),
                qd.mom6_iau(),
                qd.window_length()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class MoveForecastRestart(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.question_list = QuestionList([
                qd.forecast_duration()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class PrepGeosRunDir(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.question_list = QuestionList([
                swell_static_file_questions,
                qd.existing_geos_gcm_build_path(),
                qd.forecast_duration(),
                qd.geos_experiment_directory(),
                qd.mom6_iau_nhours()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class PrepareAnalysis(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                qd.analysis_forecast_window_offset(),
                qd.analysis_variables(),
                qd.mom6_iau(),
                qd.total_processors()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediFgatExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
                run_jedi_executable,
                qd.marine_models()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediEnsembleMeanVariance(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
                np_proc_resolution,
                window_questions,
                qd.analysis_variables(),
                qd.ensemble_num_members(),
                qd.generate_yaml_and_exit(),
                qd.jedi_forecast_model(),
                qd.observations(),
                qd.observing_system_records_path(),
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediHofxEnsembleExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
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
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediHofxExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
                np_proc_resolution,
                window_questions,
                background_crtm_obs,
                qd.background_frequency(),
                qd.generate_yaml_and_exit(),
                qd.jedi_forecast_model(),
                qd.save_geovals(),
                qd.total_processors()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediLocalEnsembleDaExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
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
                qd.perhost()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediVariationalExecutable(Task):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {'nodes': 3}
            self.question_list = QuestionList([
                run_jedi_executable,
                qd.perhost()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RemoveForecastDir(Task):
        def set_attributes(self):
            self.is_cycling = True

    # --------------------------------------------------------------------------------------------------
    
    class RunGeosExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
    
    # --------------------------------------------------------------------------------------------------

    class RunJediUfoExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.slurm = {}
            self.time_limit = True

    # --------------------------------------------------------------------------------------------------
    
    class RunJediUfoTestsExecutable(Task):
        def set_attributes(self):
            self.time_limit = True
            self.is_cycling = True
            self.is_model = True
            self.slurm = {'ntasks-per-node': 1}
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.generate_yaml_and_exit(),
                qd.single_observations(),
                qd.window_length(),
                qd.window_offset()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediConvertStateSoca2ciceExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {'nodes': 1}
            self.question_list = QuestionList([
                qd.analysis_variables(),
                qd.generate_yaml_and_exit(),
                qd.jedi_forecast_model(),
                qd.marine_models(),
                qd.observations(),
                qd.total_processors(),
                qd.window_offset(),
                qd.window_type()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediFgatExecutable(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
                run_jedi_executable,
                qd.marine_models()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class SaveObsDiags(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                background_crtm_obs,
                qd.r2d2_local_path(),
                qd.window_offset(),
                qd.marine_models()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class SaveRestart(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.question_list = QuestionList([
                window_questions,
                qd.background_time_offset(),
                qd.forecast_duration(),
                qd.horizontal_resolution(),
                qd.marine_models(),
                qd.r2d2_local_path()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class StageJedi(Task):
        def set_attributes(self):
            self.is_model = True
            self.question_list = QuestionList([
                swell_static_file_questions,
                qd.gsibec_configuration(),
                qd.gsibec_nlats(),
                qd.gsibec_nlons(),
                qd.horizontal_resolution(),
                qd.vertical_resolution()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class StageJediCycle(Task):
        def set_attributes(self):
            self.is_cycling = True
            self.is_model = True
            self.base_name = "StageJedi"
            self.scheduling_name = "StageJediCycle-{self.model}"
            self.question_list = QuestionList([
                swell_static_file_questions,
                qd.gsibec_configuration(),
                qd.gsibec_nlats(),
                qd.gsibec_nlons(),
                qd.horizontal_resolution(),
                qd.vertical_resolution()
            ])
    
    # --------------------------------------------------------------------------------------------------

    class sync_point(Task):
        def set_attributes(self):
            self.script = "true"

    # --------------------------------------------------------------------------------------------------
    
    class JediLogComparison(Task):
        def set_attributes(self):
            self.is_model = True
            self.question_list = QuestionList([
                qd.number_of_iterations(),
                qd.comparison_log_type(),
            ])
    
    # --------------------------------------------------------------------------------------------------

    class RunJediObsfiltersExecutable(Task):
        def set_attributes(self):
            self.script = ("swell task RunJediObsfiltersExecutable $config"
                        " -d $datetime -m geos_atmosphere")
            self.is_cycling = True
            self.is_model = True
            self.time_limit = True
            self.slurm = {}
            self.question_list = QuestionList([
                np_proc_resolution,
                window_questions,
                background_crtm_obs,
                qd.background_frequency(),
                qd.generate_yaml_and_exit(),
                qd.jedi_forecast_model(),
                qd.observing_system_records_path(),
                qd.total_processors(),
                qd.obs_thinning_rej_fraction()
            ])

    # --------------------------------------------------------------------------------------------------

    @classmethod
    def get(cls, name: str) -> Task:
        return getattr(cls, name)

# --------------------------------------------------------------------------------------------------
