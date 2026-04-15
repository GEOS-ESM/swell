# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
import swell.configuration.question_defaults as qd
from swell.suites.base.suite_questions import marine
from swell.suites.base.suite_attributes import suite_configs

suite_name = '3dfgat_cycle'

# --------------------------------------------------------------------------------------------------

_3dfgat_cycle_tier1 = QuestionList(
    questions=[
        marine,
        qd.cycling_varbc(),
        qd.start_cycle_point("2021-07-02T06:00:00Z"),
        qd.final_cycle_point("2021-07-02T12:00:00Z"),
        qd.runahead_limit("P2"),
        qd.jedi_build_method("use_existing"),
        qd.geos_build_method("use_existing"),
        qd.model_components(['geos_marine']),
        qd.comparison_log_type('fgat'),
    ],
    geos_marine=[
        qd.cycle_times([
            "T00",
            "T06",
            "T12",
            "T18"
        ]),
        qd.analysis_variables([
            "sea_water_salinity",
            "sea_water_potential_temperature",
            "sea_surface_height_above_geoid",
            "sea_water_cell_thickness",
            "sea_ice_area_fraction",
            "sea_ice_thickness",
            "sea_ice_snow_thickness"
        ]),
        qd.window_length("PT6H"),
        qd.window_type("4D"),
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
            "icec_amsr2_north",
            "icec_amsr2_south",
            "icec_nsidc_nh",
            "icec_nsidc_sh",
            "sst_ostia",
            "sss_smos",
            "sss_smapv5",
            "sst_abi_g16_l3c",
            "sst_gmi_l3u",
            "sst_viirs_n20_l3u",
            "temp_profile_xbt"
        ]),
        qd.number_of_iterations([10]),
        qd.mom6_iau(True),
        qd.background_time_offset("PT9H"),
        qd.clean_patterns([
            "*.txt",
            "*.rc",
            "*.bin"
        ]),
    ]
)

suite_configs.register(suite_name, '3dfgat_cycle_tier1', _3dfgat_cycle_tier1)

<<<<<<< HEAD:src/swell/suites/3dfgat_cycle/suite_config.py
# --------------------------------------------------------------------------------------------------
=======
    _3dvar_marine_cycle = QuestionList(
        list_name="3dvar_marine_cycle",
        questions=[
            sq.marine,
            qd.start_cycle_point("2021-07-02T06:00:00Z"),
            qd.final_cycle_point("2021-07-02T12:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.geos_build_method("use_existing"),
            qd.model_components(['geos_marine']),
            qd.comparison_log_type('variational'),
        ],
        geos_marine=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18",
            ]),
            qd.window_length("PT6H"),
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
            qd.mom6_iau(True),
            qd.marine_models(['mom6']),
            qd.background_time_offset("PT9H"),
            qd.clean_patterns([
                "*.nc4",
                "*.txt",
                "*.rc",
                "*.bin"
            ]),
        ]
    )
>>>>>>> develop:src/swell/suites/3dvar_marine_cycle/suite_config.py

_3dfgat_cycle = QuestionList(
    questions=[
        _3dfgat_cycle_tier1
    ]
)

<<<<<<< HEAD:src/swell/suites/3dfgat_cycle/suite_config.py
suite_configs.register(suite_name, '3dfgat_cycle', _3dfgat_cycle)
=======
    _3dvar_marine_cycle_tier1 = QuestionList(
        list_name="3dvar_marine_cycle_tier1",
        questions=[
            _3dvar_marine_cycle
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_marine_cycle_tier2 = QuestionList(
        list_name="3dvar_marine_cycle_tier2",
        questions=[
            _3dvar_marine_cycle,
            qd.start_cycle_point("2023-07-02T12:00:00Z"),
            qd.final_cycle_point("2023-07-02T18:00:00Z"),
            qd.forecast_duration("PT12H"),
            qd.geos_homdir("/discover/nobackup/projects/gmao/advda/SwellStaticFiles/geos/homdirs/"
                           "dataatm_025")
        ],
        geos_marine=[
            qd.cycle_times([
                "T00",
                "T06",
                "T12",
                "T18",
            ]),
            qd.analysis_variables([
                "sea_water_salinity",
                "sea_water_potential_temperature",
                "sea_surface_height_above_geoid",
                "sea_water_cell_thickness",
            ]),
            qd.window_length("PT6H"),
            qd.horizontal_resolution("1440x1080"),
            qd.vertical_resolution("75"),
            qd.total_processors(720),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3",
                "adt_jason3n",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "adt_sentinel6a",
                "adt_swot_nadir",
                "insitu_profile_argo",
                "insitu_profile_ctd",
                "insitu_profile_pirata",
                "insitu_profile_rama",
                "insitu_profile_tao",
                "sst_ostia",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_avhrrf_mb_l3u",
                "sst_avhrrf_mc_l3u",
                "sst_viirs_n20_l3u",
                "sst_viirs_npp_l3u",
                "temp_profile_xbt"
            ]),
            qd.number_of_iterations([50]),
            qd.background_time_offset("PT9H"),
        ]
    )
>>>>>>> develop:src/swell/suites/3dvar_marine_cycle/suite_config.py

# --------------------------------------------------------------------------------------------------
