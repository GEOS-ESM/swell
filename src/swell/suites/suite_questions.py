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

class SuiteQuestions(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------
    # Shared groups of questions across suites
    # --------------------------------------------------------------------------------------------------

    all_suites = QuestionList(
        list_name="all_suites",
        questions=[
            qd.experiment_id(),
            qd.experiment_root()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    common = QuestionList(
        list_name="common",
        questions=[
            all_suites,
            qd.cycle_times(),
            qd.start_cycle_point(),
            qd.final_cycle_point(),
            qd.model_components(),
            qd.runahead_limit()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    marine = QuestionList(
        list_name="marine",
        questions=[
            common,
            qd.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------
    # Basic definition of what questions are used for each suite, using the 
    # defaults for each question.
    # --------------------------------------------------------------------------------------------------

    _3dfgat_atmos_base = QuestionList(
        list_name="3dfgat_atmos",
        questions=[
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dfgat_cycle_base = QuestionList(
        list_name="3dfgat_cycle",
        questions=[
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_base = QuestionList(
        list_name="3dvar",
        questions=[
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_atmos_base = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cycle_base = QuestionList(
        list_name="3dvar_cycle",
        questions=[
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    convert_ncdiags_base = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    forecast_geos_base = QuestionList(
        list_name="forecast_geos",
        questions=[
            qd.cycle_times(),
            qd.final_cycle_point(),
            qd.start_cycle_point()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    hofx_base = QuestionList(
        list_name="hofx",
        questions=[
            marine,
            qd.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    localensembleda_base = QuestionList(
        list_name="localensembleda",
        questions=[
            marine,
            qd.ensemble_hofx_packets(),
            qd.ensemble_hofx_strategy(),
            qd.skip_ensemble_hofx()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    ufo_testing_base = QuestionList(
        list_name="ufo_testing",
        questions=[
            common,
        ]
    )


    # --------------------------------------------------------------------------------------------------
    # Tier 1 defaults
    # --------------------------------------------------------------------------------------------------

    _3dfgat_atmos_tier1 = QuestionList(
        list_name="3dfgat_atmos",
        questions=[
            _3dfgat_atmos_base,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
            qd.runahead_limit("P2"),
        ],
        geos_atmosphere=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18"
            ]),
            qd.horizontal_resolution("91"),
            qd.geos_x_background_directory("/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x"),
            qd.window_type("4D"),
            qd.observations([
                "aircraft_temperature",
                "aircraft_wind",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                "amsua_n18",
                "amsua_n19",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n18",
                "avhrr3_n19",
                "cris-fsr_n20",
                "cris-fsr_npp",
                "gmi_gpm",
                "gps",
                "iasi_metop-b",
                "iasi_metop-c",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "mls55_aura",
                "omi_aura",
                "ompsnm_npp",
                "pibal",
                "satwind",
                "scatwind",
                "sfcship",
                "sfc",
                "sondes",
                "ssmis_f17"
            ]),
            qd.gradient_norm_reduction("1e-3"),
            qd.number_of_iterations([10]),
            qd.clean_patterns(['*.txt', '*.csv']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dfgat_cycle_tier1 = QuestionList(
        list_name="3dfgat_cycle",
        questions=[
            _3dfgat_cycle_base,
            qd.start_cycle_point("2021-06-01T12:00:00Z"),
            qd.final_cycle_point("2021-06-02T00:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.geos_build_method("use_existing"),
            qd.model_components(['geos_marine']),
        ],
        geos_marine=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18"
            ]),
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
            qd.horizontal_resolution("72x36"),
            qd.vertical_resolution("50"),
            qd.total_processors(6),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "insitu_profile_argo",
                "sst_ostia",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_gmi_l3u",
                "sst_viirs_n20_l3u",
                "temp_profile_xbt"
            ]),
            qd.number_of_iterations([10]),
            qd.obs_provider(['odas', 'gdas_marine']),
            qd.mom6_iau(True),
            qd.analysis_forecast_window_offset("-PT3H"),
            qd.background_time_offset("PT9H"),
            qd.clean_patterns([
                "*.nc4",
                "*.txt",
                "*.rc",
                "*.bin"
            ]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_tier1 = QuestionList(
        list_name="3dvar",
        questions=[
            _3dvar_base,
            qd.start_cycle_point("2021-07-01T12:00:00Z"),
            qd.final_cycle_point("2021-07-01T12:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_ocean']),
        ],
        geos_ocean=[
            qd.cycle_times(['T12']),
            qd.window_length("P1D"),
            qd.window_offset("PT12H"),
            qd.horizontal_resolution("72x36"),
            qd.vertical_resolution("50"),
            qd.total_processors(6),
            qd.obs_experiment("s2s_v1"),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "insitu_profile_argo",
                "sst_ostia",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_gmi_l3u",
                "sst_viirs_n20_l3u",
                "temp_profile_xbt"
            ]),
            qd.obs_provider(['odas', 'gdas_marine']),
            qd.analysis_forecast_window_offset("-PT12H"),
            qd.background_time_offset("PT18H"),
            qd.clean_patterns(['*.nc4', '*.txt']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_atmos_tier1 = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            _3dvar_atmos_base,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18"
            ]),
            qd.geos_x_background_directory("/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x"),
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
            qd.window_type("3D"),
            qd.horizontal_resolution("91"),
            qd.vertical_resolution("72"),
            qd.observations([
                "aircraft_temperature",
                "aircraft_wind",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                "amsua_n18",
                "amsua_n19",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n18",
                "avhrr3_n19",
                "cris-fsr_n20",
                "cris-fsr_npp",
                "gmi_gpm",
                "gps",
                "iasi_metop-b",
                "iasi_metop-c",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "mls55_aura",
                "omi_aura",
                "ompsnm_npp",
                "pibal",
                "satwind",
                "scatwind",
                "sfcship",
                "sfc",
                "sondes",
                "ssmis_f17"
            ]),
            qd.clean_patterns(['*.txt', '*.csv']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cycle_tier1 = QuestionList(
        list_name="3dvar_cycle",
        questions=[
            _3dvar_cycle_base,
            qd.start_cycle_point("2021-06-01T12:00:00Z"),
            qd.final_cycle_point("2021-06-02T00:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.geos_build_method("use_existing"),
            qd.model_components(['geos_ocean']),
        ],
        geos_ocean=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18",
            ]),
            qd.window_length("PT6H"),
            qd.window_offset("PT3H"),
            qd.horizontal_resolution("72x36"),
            qd.vertical_resolution("50"),
            qd.total_processors(6),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "insitu_profile_argo",
                "sst_ostia",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_gmi_l3u",
                "sst_viirs_n20_l3u",
                "temp_profile_xbt"
            ]),
            qd.number_of_iterations([10]),
            qd.obs_provider(['odas', 'gdas_marine']),
            qd.mom6_iau(True),
            qd.analysis_forecast_window_offset("-PT3H"),
            qd.background_time_offset("PT9H"),
            qd.clean_patterns([
                "*.nc4",
                "*.txt",
                "*.rc",
                "*.bin"
            ]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    convert_ncdiags_tier1 = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            convert_ncdiags_base,
            qd.start_cycle_point("2021-12-12T00:00:00Z"),
            qd.final_cycle_point("2021-12-12T06:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.bundles("REMOVE"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times(['T00', 'T06']),
            qd.clean_patterns([
                "gsi_bcs/*.nc4",
                "gsi_bcs/*.txt",
                "gsi_bcs/*.yaml",
                "gsi_bcs",
                "gsi_ncdiags/*.nc4",
                "gsi_ncdiags/aircraft/*.nc4",
                "gsi_ncdiags/aircraft",
                "gsi_ncdiags"
            ]),
            qd.path_to_gsi_nc_diags("/discover/nobackup/projects/gmao/advda/SwellTestData/ufo_testing/ncdiagv2/%Y%m%d%H"),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    forecast_geos_tier1 = QuestionList(
        list_name="forecast_geos",
        questions=[
            forecast_geos_base,
            qd.start_cycle_point("2021-06-20T00:00:00Z"),
            qd.final_cycle_point("2021-06-21T00:00:00Z"),
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18"
            ]),
            qd.geos_build_method("use_existing"),
            qd.forecast_duration("PT6H"),
        ],
    )

    # --------------------------------------------------------------------------------------------------

    geosadas_tier1 = QuestionList(
        list_name="geosadas",
        questions=[
            all_suites,
            qd.jedi_build_method("use_existing"),
            qd.bundles("REMOVE"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.horizontal_resolution("13"),
            qd.observations([
                "aircraft_temperature",
                "aircraft_wind",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                "amsua_n18",
                "amsua_n19",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n18",
                "avhrr3_n19",
                "cris-fsr_n20",
                "cris-fsr_npp",
                "gmi_gpm",
                "iasi_metop-b",
                "iasi_metop-c",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "mls55_aura",
                "omi_aura",
                "ompsnm_npp",
                "satwind",
                "scatwind",
                "ssmis_f17"
            ]),
            qd.produce_geovals(False),
            qd.window_type("3D"),
            qd.gradient_norm_reduction("1e-6"),
            qd.number_of_iterations([5]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    hofx_tier1 = QuestionList(
        list_name="hofx",
        questions=[
            hofx_base,
            qd.jedi_build_method("use_existing"),
            qd.save_geovals(True),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.horizontal_resolution("91"),
            qd.geos_x_background_directory("/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x"),
            qd.npx_proc(2),
            qd.npy_proc(2),
            qd.observations([
                "aircraft_temperature",
                "aircraft_wind",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                "amsua_n18",
                "amsua_n19",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n18",
                "avhrr3_n19",
                "cris-fsr_n20",
                "cris-fsr_npp",
                "gmi_gpm",
                "gps",
                "iasi_metop-b",
                "iasi_metop-c",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "mls55_aura",
                "omi_aura",
                "ompsnm_npp",
                "pibal",
                "satwind",
                "scatwind",
                "sfcship",
                "sfc",
                "sondes",
                "ssmis_f17"
            ]),
            qd.clean_patterns([]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    localensembleda_tier1 = QuestionList(
        list_name="localensembleda",
        questions=[
            localensembleda_base,
            qd.final_cycle_point("2021-12-12T00:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.horizontal_resolution(91),
            qd.npx_proc(4),
            qd.npy_proc(4),
            qd.cycle_times(['T00']),
            qd.ensemble_num_members(5),
            qd.skip_ensemble_hofx(True),
            qd.local_ensemble_solver("GETKF"),
            qd.local_ensemble_use_linear_observer(True),
            qd.ensmean_only(False),
            qd.local_ensemble_save_posterior_mean(False),
            qd.local_ensemble_save_posterior_mean_increment(True),
            qd.local_ensemble_save_posterior_ensemble(False),
            qd.local_ensemble_save_posterior_ensemble_increments(False),
            qd.path_to_ensemble("/discover/nobackup/projects/gmao/advda/SwellTestData/letk/ensemble/91/Y%Y/M%m/D%d/H%H/geos*%Y%m%d_%H%M%Sz.nc4"),
            qd.observations([
                "aircraft_temperature",
                "aircraft_wind",
                "sondes",
                "gps",
                "amsua_aqua",
                "amsua_n15",
                "amsua_n18",
                "amsua_n19",
                "amsr2_gcom-w1",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n18",
                "avhrr3_n19",
                "scatwind",
                "sfcship",
                "sfc",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "mls55_aura",
                "omi_aura",
                "ompsnm_npp",
                "pibal",
                "ssmis_f17",
                "amsua_metop-b",
                "amsua_metop-c"
            ]),
            qd.background_experiment("x0048"),
            qd.window_type("3D"),
            qd.clean_patterns(['*.txt']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    ufo_testing_tier1 = QuestionList(
        list_name="ufo_testing",
        questions=[
            ufo_testing_base,
            qd.final_cycle_point("2023-10-10T00:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.bundles("REMOVE"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times(['T00']),
            qd.observations([
                "aircraft_temperature",
                "aircraft_wind",
                "airs_aqua",
                "amsr2_gcom-w1",
                "amsua_aqua",
                "amsua_metop-b",
                "amsua_metop-c",
                "amsua_n15",
                "amsua_n19",
                "atms_n20",
                "atms_npp",
                "avhrr3_metop-b",
                "avhrr3_n19",
                "cris-fsr_n20",
                "cris-fsr_npp",
                "gmi_gpm",
                "gps",
                "iasi_metop-b",
                "iasi_metop-c",
                "mhs_metop-b",
                "mhs_metop-c",
                "mhs_n19",
                "pibal",
                "satwind",
                "scatwind",
                "sfc",
                "sfcship",
                "sondes",
                "ssmis_f17"
            ]),
            qd.produce_geovals(False),
            qd.clean_patterns([
                "*.txt",
                "*.log",
                "*.yaml",
                "*.csv",
                "gsi_bcs/*.nc4",
                "gsi_bcs/*.txt",
                "gsi_bcs/*.yaml",
                "gsi_bcs",
                "gsi_ncdiags/*.nc4",
                "gsi_ncdiags/aircraft/*.nc4",
                "gsi_ncdiags/aircraft",
                "gsi_ncdiags"
            ]),
            qd.path_to_gsi_bc_coefficients("/discover/nobackup/projects/gmao/dadev/rtodling/archive/541/Milan/x0050/ana/Y%Y/M%m/*bias*%Y%m%d_%Hz.txt"),
            qd.path_to_gsi_nc_diags("/discover/nobackup/projects/gmao/dadev/rtodling/archive/541/Milan/x0050/obs/Y%Y/M%m/D%d/H%H/"),
        ]
    )

    # --------------------------------------------------------------------------------------------------
    # Tier 2 defaults
    # --------------------------------------------------------------------------------------------------

    _3dfgat_atmos = QuestionList(
        list_name="3dfgat_atmos",
        questions=[
            _3dfgat_atmos_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dfgat_cycle = QuestionList(
        list_name="3dfgat_cycle",
        questions=[
            _3dfgat_cycle_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar = QuestionList(
        list_name="3dvar",
        questions=[
            _3dvar_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_atmos = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            _3dvar_atmos_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cycle = QuestionList(
        list_name="3dvar_cycle",
        questions=[
            _3dvar_cycle_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    convert_ncdiags = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            convert_ncdiags_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    forecast_geos = QuestionList(
        list_name="forecast_geos",
        questions=[
            forecast_geos_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    geosadas = QuestionList(
        list_name="geosadas",
        questions=[
            geosadas_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    hofx = QuestionList(
        list_name="hofx",
        questions=[
            hofx_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    localensembleda = QuestionList(
        list_name="localensembleda",
        questions=[
            localensembleda_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    ufo_testing = QuestionList(
        list_name="ufo_testing",
        questions=[
            ufo_testing_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

