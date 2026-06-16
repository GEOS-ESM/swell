# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------

from swell.utilities.swell_questions import QuestionContainer, QuestionList, WidgetType
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum

# --------------------------------------------------------------------------------------------------


class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    compare = QuestionList(
        list_name="compare",
        questions=[
            sq.all_suites,
            qd.comparison_experiment_paths(),
            qd.start_cycle_point(default_value=None, widget_type=WidgetType.STRING),
            qd.final_cycle_point(default_value=None, widget_type=WidgetType.STRING),
            qd.cycle_times(default_value=[None], widget_type=WidgetType.STRING_CHECK_LIST),
            qd.model_components(),
            qd.runahead_limit(),
            qd.ioda_fields_for_comparison(['hofx0/{variable}']),
            qd.observations([]),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_variational_marine = QuestionList(
        list_name="compare_variational_marine",
        questions=[
            compare,
            qd.comparison_log_type('variational'),
            qd.model_components(['geos_marine']),
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
            ])
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_variational_atmosphere = QuestionList(
        list_name="compare_variational_atmosphere",
        questions=[
            compare,
            qd.comparison_log_type('variational'),
            qd.model_components(['geos_atmosphere']),
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
            ])
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_variational_cf = QuestionList(
        list_name="compare_variational_cf",
        questions=[
            compare,
            qd.comparison_log_type('variational'),
            qd.model_components(['geos_cf']),
            qd.observations([
                "tempo_no2_tropo",
                "tropomi_s5p_no2_tropo",
            ])
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_fgat_marine = QuestionList(
        list_name="compare_fgat_marine",
        questions=[
            compare,
            qd.comparison_log_type('fgat'),
            qd.model_components(['geos_marine']),
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
                "icec_amsr2_north",
                "icec_amsr2_south",
                "icec_nsidc_nh",
                "icec_nsidc_sh",
                "sst_ostia",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_avhrrf_mb_l3u",
                "sst_avhrrf_mc_l3u",
                "sst_viirs_n20_l3u",
                "sst_viirs_npp_l3u",
                "temp_profile_xbt"
            ])
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_hofx = QuestionList(
        list_name="compare_hofx",
        questions=[
            compare,
            qd.comparison_log_type('hofx'),
            qd.model_components(['geos_atmosphere']),
            qd.ioda_fields_for_comparison(['hofx/{variable}']),
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
            qd.mock_experiment(True)
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_hofx_cf = QuestionList(
        list_name="compare_hofx_cf",
        questions=[
            compare,
            qd.comparison_log_type('hofx'),
            qd.ioda_fields_for_comparison(['hofx/{variable}']),
            qd.model_components(['geos_cf']),
        ]
    )

    # --------------------------------------------------------------------------------------------------
