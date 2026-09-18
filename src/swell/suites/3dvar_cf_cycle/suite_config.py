# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum


# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    _3dvar_cf_cycle_tier1 = QuestionList(
        list_name="3dvar_cf_cycle",
        questions=[
            sq.common,
            qd.start_cycle_point("2025-04-02T06:00:00Z"),
            qd.final_cycle_point("2025-04-02T12:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_cf']),
            qd.check_for_obs(False)
        ],
        geos_cf=[
            qd.window_length("PT6H"),
            qd.window_type("3D"),
            qd.horizontal_resolution("c90"),
            qd.npx(91),
            qd.npy(91),
            qd.npx_proc(2),
            qd.npy_proc(2),
            qd.vertical_resolution(72),
            qd.saber_central_block('bump_nicas'),
            qd.saber_outer_block('stddev_bkg_scaled'),
            qd.analysis_variables([
                "volume_mixing_ratio_of_o3",
                "volume_mixing_ratio_of_no2",
                "volume_mixing_ratio_of_co",
                ]),
            qd.background_experiment("swell_test"),
            qd.rst_experiment("swell_test"),
            qd.rst_file_types(['achem_internal',
                               'aiau_import',
                               'cabc_internal',
                               'cabr_internal',
                               'caoc_internal',
                               'catch_internal',
                               'du_internal',
                               'fvcore_internal',
                               'geoschemchem_import',
                               'geoschemchem_internal',
                               'gocart_import',
                               'gocart_internal',
                               'gwd_import',
                               'hemco_import',
                               'hemco_internal',
                               'irrad_internal',
                               'lake_internal',
                               'landice_internal',
                               'moist_import',
                               'moist_internal',
                               'ni_internal',
                               'openwater_internal',
                               'pchem_internal',
                               'saltwater_import',
                               'seaicethermo_internal',
                               'solar_internal',
                               'ss_internal',
                               'su_internal',
                               'surf_import',
                               'turb_import',
                               'turb_internal']),
            qd.observations([
                "omps_o3_nm_total",
                "tropomi_s5p_no2_tropo",
                "tropomi_s5p_co_total",  
            ]),
            qd.iau(True),
            qd.forecast_length('PT12H'),
            qd.forecast_output_frequency('PT3H'),
            qd.clean_patterns(['*.nc4', '*.txt', 'logfile.*.out']),
            qd.inc_template(
                '/discover/nobackup/projects/gmao/geos_cf_dev/GEOS-CF3-dev/'
                'handle_inc/GCC_c90_FPens.geoscf_jedi.20210805_0600z.nc4'
                ),
            qd.geos_cf_install_dir(
                '/discover/nobackup/projects/gmao/geos_cf_dev/GEOS-CF3-dev/'
                'GEOSgcm_21042026/install-SLES15'
                ),
            qd.geos_cf_rc_dir(
                '/discover/nobackup/projects/gmao/geos_cf_dev/GEOS-CF3-dev/'
                'RC_CFv2/RC'
                ),
            qd.swell_static_files(
                '/discover/nobackup/projects/gmao/geos_cf_dev/GEOS-CF3-dev/'
                'SwellStaticFiles'
                ),
            qd.met_replay_exp('d5294_geosit_jan18'),
            qd.met_replay_root('/home/dao_ops')
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cf_cycle = QuestionList(
        list_name="3dvar_cf_cycle",
        questions=[
            _3dvar_cf_cycle_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
