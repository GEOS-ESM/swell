# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from dataclasses import dataclass, field
from typing import List, Dict, Any

from swell.utilities.swell_questions import SuiteQuestion, TaskQuestion
from swell.utilities.swell_questions import DataType as DType
from swell.utilities.dataclass_utils import mutable_field

# --------------------------------------------------------------------------------------------------
# Suite question defaults go here
# --------------------------------------------------------------------------------------------------

@dataclass
class comparison_experiment_paths(SuiteQuestion):
    default_value: list = mutable_field([])
    prompt: str = "Provide paths to two experiments to run comparison tests on."
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class cycle_times(SuiteQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Enter the cycle times for this model."
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class cycling_varbc(SuiteQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "Do you want to use cycling VarBC option?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class download_convert_pipeline(SuiteQuestion):
    default_value: bool = False
    prompt: str = ("Run the DownloadObs and ConvertObsToIoda tasks?"
                    "(DownloadObs -> ConvertObsToIoda) -> IngestObs to R2D2")
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class ensemble_hofx_packets(SuiteQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Enter the number of ensemble packets."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class ensemble_hofx_strategy(SuiteQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Enter the ensemble hofx strategy."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class experiment_id(SuiteQuestion):
    default_value: str = "defer_to_code"
    prompt: str = "What is the experiment id?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class experiment_root(SuiteQuestion):
    default_value: str = "defer_to_platform"
    prompt: str = ("What is the experiment root (the directory where the "
                    "experiment will be stored)?")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class final_cycle_point(SuiteQuestion):
    default_value: str = "2023-10-10T06:00:00Z"
    prompt: str = "What is the time of the final cycle (middle of the window)?"
    data_type: DType = DType.ISO_DATETIME

# --------------------------------------------------------------------------------------------------

@dataclass
class marine_models(SuiteQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_marine"
    ])
    prompt: str = "Select the active SOCA models for this model."
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class mock_experiment(SuiteQuestion):
    default_value: bool = False
    prompt: str = "Dry-run option for comparing configs."
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class model_components(SuiteQuestion):
    default_value: str = "defer_to_code"
    options: str = "defer_to_code"
    prompt: str = "Enter the model components for this model."
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class ingest_background_pipeline(SuiteQuestion):
    default_value: bool = False
    prompt: str = "Run the SaveBackground task to ingest background files into R2D2?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class parser_options(SuiteQuestion):
    default_value: list = mutable_field(['fgrep_residual_norm'])
    options: list = mutable_field(['fgrep_residual_norm'])
    prompt: str = "List the test types to run on the JEDI oops log."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class r2d2_experiment_id(SuiteQuestion):
    default_value: str = "defer_to_code"
    prompt: str = "What experiment_id should r2d2 reference for experiment?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class r2d2_server(SuiteQuestion):
    default_value: str | None = None
    prompt: str = (
        "Server/profile name in ~/.swell/r2d2_credentials.yaml "
        "(e.g. 'gmao_server'). Leave empty if credentials are at the root level."
    )
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class r2d2_datastore(SuiteQuestion):
    default_value: str | None = None
    prompt: str = (
        "Datastore name passed to R2D2 fetch and store operations "
        "(e.g. a Discover directory store or an S3 bucket store). "
        "Run scripts/discover_r2d2_datastores.py to list available datastores. "
        "Leave empty to let R2D2 pick the highest-priority writable datastore "
        "for your compute host."
    )
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class runahead_limit(SuiteQuestion):
    default_value: str = "P4"
    prompt: str = ("Set the Cylc runahead limit: the maximum number of cycles "
                    "that may be active ahead of the current cycle "
                    "(e.g. P1: up to 1 cycle ahead, P3: up to 3 cycles ahead, default P4).")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class saber_central_block(SuiteQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which saber central block do you want to use?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class saber_outer_block(SuiteQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which saber outer blocks do you want to use?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class skip_ensemble_hofx(SuiteQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Do you want to run localensembleda observer and solver together?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class skip_r2d2(SuiteQuestion):
    default_value: bool = False
    prompt: str = "Skip registering and storing results of this experiment in R2D2?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class start_cycle_point(SuiteQuestion):
    default_value: str = "2023-10-10T00:00:00Z"
    prompt: str = "What is the time of the first cycle (middle of the window)?"
    data_type: DType = DType.ISO_DATETIME

# --------------------------------------------------------------------------------------------------

@dataclass
class window_type(SuiteQuestion):
    default_value: str = "defer_to_model"
    options: List[str] = mutable_field([
        "3D",
        "4D"
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Enter the window type for this model."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------
# Task question defaults go here
# --------------------------------------------------------------------------------------------------

@dataclass
class analysis_variables(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What are the analysis variables?"
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class background_error_model(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which background error model do you want to use?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class background_experiment(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What is the name of the name of the experiment providing the backgrounds?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class background_frequency(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    depends: Dict = mutable_field({
        "window_type": "4D"
    })
    prompt: str = "What is the frequency of the background files?"
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class background_time_offset(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = ("How long before the middle of the analysis window did"
                    " the background providing forecast begin?")
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class ebkg_time_offset(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = ("How long before the middle of the analysis window did"
                    " the ensemble background providing forecast begin?")
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class rst_experiment(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the name of the experiment providing the restart files in R2D2?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class rst_file_types(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What are the restart file types to fetch/store from R2D2?"
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class rst_store_interval(TaskQuestion):
    default_value: str = None
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = ("After how many cycles should restart files be stored as real files "
                    "(not symlinks)? E.g. 28 means every 28th cycle (and multiples) stores "
                    "real files. Leave unset to always store as symlinks.")
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class bufr_obs_classes(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What BUFR observation classes will be used?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class bundles(TaskQuestion):
    default_value: List[str] = mutable_field([
        "fv3-jedi",
        "soca",
        "iodaconv",
        "ufo"
    ])
    options: List[str] = mutable_field([
        "fv3-jedi",
        "soca",
        "iodaconv",
        "ufo",
        "ioda",
        "oops",
        "saber"
    ])
    depends: Dict = mutable_field({
        "jedi_build_method": "create"
    })
    prompt: str = "Which JEDI bundles do you wish to build?"
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class check_for_obs(TaskQuestion):
    default_value: bool = True
    options: List[bool] = mutable_field([True, False])
    models: List[str] = mutable_field([
        'all_models'
    ])
    prompt: str = "Perform check for observations? Set to false for debugging purposes."
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class clean_patterns(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Provide a list of patterns that you wish to remove from the cycle directory."
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class comparison_log_type(TaskQuestion):
    default_value: str = "variational"
    options: List[str] = mutable_field([
        'variational',
        'fgat',
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Provide the log naming convention (e.g. 'variational', 'fgat')."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class crtm_coeff_dir(TaskQuestion):
    default_value: str = "defer_to_platform"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the path to the CRTM coefficient files?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class ensemble_hofx_packets(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Enter number of packets in which ensemble observers should be computed."
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class ensemble_hofx_strategy(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Enter hofx strategy."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class ensemble_num_members(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "How many members comprise the ensemble?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class obs_pert_amplitude(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Enter obs perturbation amplitude for EDA:"
    data_type: DType = DType.FLOAT

# --------------------------------------------------------------------------------------------------

@dataclass
class ensmean_only(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Calculate ensemble mean only?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class ensmeanvariance_only(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Calculate ensemble mean and variance only?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class ensmeanvariance_spec(TaskQuestion):
    default_value: List[Dict[str, str]] = field(default_factory=lambda: [{}])
    models: List[str] = mutable_field([
        "all_models"
    ])
    
    prompt: str = "Configure the ensemble mean and variance specifications:"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class diffstates_spec(TaskQuestion):
    default_value: Dict[str, Any] = field(default_factory=dict)
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Configure the diffstates specifications: [state1, state2]"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class existing_geos_gcm_build_path(TaskQuestion):
    default_value: str = "defer_to_platform"
    depends: Dict = mutable_field({
        "geos_build_method": "use_existing"
    })
    prompt: str = "What is the path to the existing GEOS build directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class existing_geos_gcm_source_path(TaskQuestion):
    default_value: str = "defer_to_platform"
    depends: Dict = mutable_field({
        "geos_build_method": "use_existing"
    })
    prompt: str = "What is the path to the existing GEOS source code directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class existing_jedi_build_directory(TaskQuestion):
    default_value: str = "defer_to_platform"
    depends: Dict = mutable_field({
        "jedi_build_method": "use_existing"
    })
    prompt: str = "What is the path to the existing JEDI build directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class existing_jedi_build_directory_pinned(TaskQuestion):
    default_value: str = "defer_to_platform"
    depends: Dict = mutable_field({
        "jedi_build_method": "use_pinned_existing"
    })
    prompt: str = "What is the path to the existing pinned JEDI build directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class existing_jedi_source_directory(TaskQuestion):
    default_value: str = "defer_to_platform"
    depends: Dict = mutable_field({
        "jedi_build_method": "use_existing"
    })
    prompt: str = "What is the path to the existing JEDI source code directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class existing_jedi_source_directory_pinned(TaskQuestion):
    default_value: str = "defer_to_platform"
    depends: Dict = mutable_field({
        "jedi_build_method": "use_pinned_existing"
    })
    prompt: str = "What is the path to the existing pinned JEDI source code directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class existing_perllib_path(TaskQuestion):
    default_value: str = 'defer_to_platform'
    question_name: str = 'existing_perllib_path'
    prompt: str = "Provide a path to an existing location for GMAO_perllib."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class gmao_perllib_tag(TaskQuestion):
    default_value: str = 'g1.0.1'
    question_name: str = 'gmao_perllib_tag'
    prompt: str = "Specify the tag at which GMAO_perllib should be cloned."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class forecast_duration(TaskQuestion):
    default_value: str = "PT12H"
    prompt: str = "GEOS forecast duration"
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class forecast_length(TaskQuestion):
    default_value: str = "PT12H"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "Duration of the GEOS-CF forecast (ISO 8601 duration, e.g. PT12H)"
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class forecast_output_frequency(TaskQuestion):
    default_value: str = "PT1H"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "Frequency of forecast output files (ISO 8601 duration, e.g. PT1H)"
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class generate_yaml_and_exit(TaskQuestion):
    default_value: bool = False
    prompt: str = "Generate JEDI executable YAML and exit?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_build_method(TaskQuestion):
    default_value: str = "create"
    options: List[str] = mutable_field([
        "use_existing",
        "create"
    ])
    prompt: str = "Do you want to use an existing GEOS build or create a new build?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_homdir(TaskQuestion):
    default_value: str = "defer_to_platform"
    prompt: str = ("What is the location for the HOME Directory (HOMDIR in gcm_run and "
                    "gcm_setup) that contains model settings and RC files?")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_expdir_different(TaskQuestion):
    default_value: str = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    prompt: str = ("Is your GEOS EXPERIMENT Directory, where restarts and scratch is located, "
                    "different than your GEOS HOME Directory?")
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_expdir(TaskQuestion):
    default_value: str = "/dev/null/"
    depends: Dict = mutable_field({
        "geos_expdir_different": True
    })
    prompt: str = ("What is the location for the EXPERIMENT Directory (to contain model "
                    "output and restart files), if it is different than your GEOS HOME "
                    "Directory?")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_cf_install_dir(TaskQuestion):
    default_value: str = "defer_to_platform"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the path to the GEOS-CF install directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_cf_run_dir(TaskQuestion):
    default_value: str = "defer_to_platform"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the path to the GEOS-CF model run directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geosfp_exp(TaskQuestion):
    default_value: str = "f5295_fp"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the GEOS FP experiment ID used for IAU analysis files?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geosfp_path(TaskQuestion):
    default_value: str = "defer_to_platform"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the path to the GEOS FP archive?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_gcm_tag(TaskQuestion):
    default_value: str = "v11.6.0"
    depends: Dict = mutable_field({
        "geos_build_method": "create"
    })
    prompt: str = "Which GEOS tag do you wish to clone?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_x_background_directory(TaskQuestion):
    default_value: str = "/dev/null/"
    options: List[str] = mutable_field([
        "/dev/null/",
        "/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x"
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What is the path to the GEOS X-backgrounds directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geos_x_ensemble_directory(TaskQuestion):
    default_value: str = "/dev/null/"
    options: List[str] = mutable_field([
        "/dev/null/",
        "/gpfsm/dnb05/projects/p139/rtodling/archive/"
    ])
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the path to the GEOS X-backgrounds directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geovals_experiment(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the name of the R2D2 experiment providing the GeoVaLs?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class geovals_provider(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the name of the R2D2 database providing the GeoVaLs?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class gradient_norm_reduction(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What value of gradient norm reduction for convergence?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class gsibec_configuration(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "Which GSIBEC climatological or hybrid?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class gsibec_nlats(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "How many number of latutides in GSIBEC grid?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class gsibec_nlons(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "How many number of longitudes in GSIBEC grid?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class horizontal_resolution(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What is the horizontal resolution for the forecast model and backgrounds?"
    data_type: DType = DType.STRING

# ------------------------------------------------------------------------------------------------

@dataclass
class dry_run(TaskQuestion):
    default_value: bool = True
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Dry-run mode: preview what would be ingested before storing to R2D2"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class store_as_symlink(TaskQuestion):
    default_value: bool = True
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Store background files as symlinks in R2D2 instead of copying them?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class obs_rc_path(TaskQuestion):
    default_value: str = 'GEOS_mksi/ObsClass/obsys-nccs.rc'
    question_name: str = 'obs_rc_path'
    prompt: str = "Filepath to observing system rc file within experiment directory."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class obs_to_ingest(TaskQuestion):
    default_value: list = mutable_field([])
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which observations do you want to ingest to R2D2?"
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class obs_to_download(TaskQuestion):
    default_value: list = mutable_field([])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which observations do you want to download from remote servers?"
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class converter_path(TaskQuestion):
    default_value: str = ""
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = ("Path to directory containing ioda-converter scripts"
                    " (leave blank to use jedi_bin)")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class initial_restarts_method(TaskQuestion):
    default_value: str = "defer_to_platform"
    options: List[str] = mutable_field([
        "geos_expdir",
        "r2d2",
        "hotstart",
    ])
    prompt: str = "How should initial GEOS restarts be obtained?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class ioda_locations_not_in_r2d2(TaskQuestion):
    default_value: str = "defer_to_platform"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = (
        "Provide a path that contains observation files not in r2d2.")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class iau(TaskQuestion):
    default_value: bool = True
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "Use Incremental Analysis Update (IAU) in the GEOS-CF forecast?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class inc_template(TaskQuestion):
    default_value: str = "defer_to_platform"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the path to the GEOS-CF increment template NetCDF file?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class jedi_build_method(TaskQuestion):
    default_value: str = "use_existing"
    options: List[str] = mutable_field([
        "use_existing",
        "use_pinned_existing",
        "create",
        "pinned_create"
    ])
    prompt: str = "Do you want to use an existing JEDI build or create a new build?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class jedi_forecast_model(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    depends: Dict = mutable_field({
        "window_type": "4D"
    })
    prompt: str = "What forecast model should be used within JEDI for 4D window propagation?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_inflation_mult(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Specify the multiplicative prior inflation coefficient (0 inf]."
    data_type: DType = DType.FLOAT

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_inflation_rtpp(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Specify the Relaxation To Prior Perturbation (RTPP) coefficient (0 1]."
    data_type: DType = DType.FLOAT

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_inflation_rtps(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Specify the Relaxation To Prior Spread (RTPS) coefficient (0 1]."
    data_type: DType = DType.FLOAT

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_save_posterior_ensemble(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Save the posterior ensemble members?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_save_posterior_ensemble_increments(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Save the posterior ensemble member increments?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_save_posterior_mean(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Save the posterior ensemble mean?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_save_posterior_mean_increment(TaskQuestion):
    default_value: bool = True
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Save the posterior ensemble mean increment?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_solver(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which local ensemble solver type should be implemented?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class local_ensemble_use_linear_observer(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Use linear observer in local ensemble solver?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class minimizer(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which data assimilation minimizer do you wish to use?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class mom6_iau(TaskQuestion):
    default_value: str = "defer_to_model"
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "geos_marine",
    ])
    prompt: str = "Do you wish to use IAU for MOM6?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class mom6_iau_nhours(TaskQuestion):
    default_value: str = "defer_to_model"
    options: List[str] = mutable_field([
        'PT3H',
        'PT12H'
    ])
    depends: dict = mutable_field({'mom6_iau': True})
    models: List[str] = mutable_field([
        "geos_marine",
    ])
    prompt: str = "What is the IAU length (ODA_INCUPD_NHOURS) for MOM6?"
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class ncdiag_experiments(TaskQuestion):
    default_value: str = "defer_to_model"
    options: List[str] = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which previously run experiments do you wish to use for the NCdiag?"
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class npx_proc(TaskQuestion):
    default_value: str = "defer_to_model"
    
    models: List[str] = mutable_field([
        "geos_atmosphere",
        "geos_cf"
    ])
    prompt: str = "What number of processors do you wish to use in the x-direction?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class npy_proc(TaskQuestion):
    default_value: str = "defer_to_model"
    
    models: List[str] = mutable_field([
        "geos_atmosphere",
        "geos_cf"
    ])
    prompt: str = "What number of processors do you wish to use in the y-direction?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class npx(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the number of grid points in the x-direction on each cube face?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class npy(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_cf"
    ])
    prompt: str = "What is the number of grid points in the y-direction on each cube face?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class number_of_iterations(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = (
        "What number of iterations do you wish to use for each outer loop?"
        " Provide a list of integers the same length as the number of outer loops.")
    data_type: DType = DType.INTEGER_LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class obs_experiment(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What is the database providing the observations?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class observation_providers(TaskQuestion):
    default_value: Dict[str, str] = mutable_field({})
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Map observation names to their R2D2 providers."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class obs_thinning_rej_fraction(TaskQuestion):
    default_value: float = 0.75
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the rejection fraction for obs thinning?"
    data_type: DType = DType.FLOAT

# --------------------------------------------------------------------------------------------------

@dataclass
class observations(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Which observations do you want to include?"
    data_type: DType = DType.LIST

# --------------------------------------------------------------------------------------------------

@dataclass
class observing_system_records_mksi_path(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the path to the GSI formatted observing system records?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class observing_system_records_mksi_path_tag(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the GSI formatted observing system records tag?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class observing_system_records_path(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the path to the Swell formatted observing system records?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class path_to_ensemble(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_marine"
    ])
    prompt: str = "What is the path to where ensemble members are stored?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class path_to_geos_adas_background(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = (
        "What is the path for the GEOSadas cubed sphere backgrounds?")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class path_to_gsi_bc_coefficients(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the location where GSI bias correction files can be found?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class path_to_gsi_nc_diags(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the path to where the GSI ncdiags are stored?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class perhost(TaskQuestion):
    default_value: str = None
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the number of processors per host?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class produce_geovals(TaskQuestion):
    default_value: str = "defer_to_model"
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = ("When running the ncdiag to ioda converted do you "
                    "want to produce GeoVaLs files?")
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class publish_directory(TaskQuestion):
    default_value: str = None
    prompt: str = "Provide an external directory to publish relevant results to."
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class cache_fetch(TaskQuestion):
    default_value: bool = True
    options: List[bool] = mutable_field([
        True,
        False
    ])
    prompt: str = "Use cached observation files if they already exist?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class fetch_obs_from_public_s3(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    prompt: str = "Fetch observations directly from a public S3 bucket if they are available?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class save_geovals(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    prompt: str = "When running hofx do you want to output the GeoVaLs?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class single_observations(TaskQuestion):
    default_value: bool = False
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "Is it a single-observation test?"
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class swell_static_files(TaskQuestion):
    default_value: str = "defer_to_platform"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What is the path to the Swell Static files directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class swell_static_files_user(TaskQuestion):
    default_value: str = "None"
    prompt: str = "What is the path to the user provided Swell Static Files directory?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class total_processors(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_marine",
    ])
    prompt: str = "What is the number of processors for JEDI?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class vertical_localization_apply_log_transform(TaskQuestion):
    default_value: bool = True
    options: List[bool] = mutable_field([
        True,
        False
    ])
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = ("Should a log (base 10) transformation be applied "
                    "to vertical coordinate when "
                    "constructing vertical localization?")
    data_type: DType = DType.BOOLEAN

# --------------------------------------------------------------------------------------------------

@dataclass
class vertical_localization_function(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "Which localization scheme should be applied in the vertical?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class vertical_localization_ioda_vertical_coord(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "Which coordinate should be used in constructing vertical localization?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class vertical_localization_ioda_vertical_coord_group(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = ("Which vertical coordinate group should be used "
                    "in constructing vertical localization?")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class vertical_localization_lengthscale(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = "What is the length scale for vertical covariance localization?"
    data_type: DType = DType.INTEGER

# --------------------------------------------------------------------------------------------------

@dataclass
class vertical_localization_method(TaskQuestion):
    default_value: str = "defer_to_model"
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "geos_atmosphere"
    ])
    prompt: str = ("What localization scheme should be applied in "
                    "constructing a vertical localization?")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class vertical_resolution(TaskQuestion):
    default_value: str = "defer_to_model"
    
    options: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What is the vertical resolution for the forecast model and background?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class window_length(TaskQuestion):
    default_value: str = "defer_to_model"
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "What is the duration for the data assimilation window?"
    data_type: DType = DType.ISO_DURATION

# --------------------------------------------------------------------------------------------------

@dataclass
class window_type(TaskQuestion):
    default_value: str = "defer_to_model"
    options: List[str] = mutable_field([
        "3D",
        "4D"
    ])
    models: List[str] = mutable_field([
        "all_models"
    ])
    prompt: str = "Do you want to use a 3D or 4D (including FGAT) window?"
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------

@dataclass
class background_source_path(TaskQuestion):
    default_value: str = (
        '/css/gmao/geos-cf/NRTv2/priv/ana/Y%Y/M%m/D%d/'
        'GEOS.cf.ana.jdi_inst_1hr_glo_C360x360x6_v72.%Y%m%d_%H%Mz.R0.nc4'
    )
    models: List[str] = mutable_field(['geos_cf'])
    prompt: str = ("Path template for background files. Uses Python strftime format codes, "
                    "e.g. Y%Y/M%m/D%d gives Y2025/M10/D02 and %Y%m%d_%H%Mz gives "
                    "20251002_0900z.")
    data_type: DType = DType.STRING

# --------------------------------------------------------------------------------------------------
