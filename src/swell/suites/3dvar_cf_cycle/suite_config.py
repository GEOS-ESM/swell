# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


import swell.configuration.question_defaults as qd
from swell.utilities.swell_questions import QuestionList
from swell.suites.base.suite_questions import common
from swell.suites.base.suite_attributes import suite_configs

# --------------------------------------------------------------------------------------------------

suite_name = '3dvar_cf_cycle'

_3dvar_cf_cycle_tier1 = QuestionList(
    questions=[
        common,
        qd.start_cycle_point("2023-08-10T00:00:00Z"),
        qd.final_cycle_point("2023-08-10T06:00:00Z"),
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
        qd.analysis_variables(["volume_mixing_ratio_of_no2"]),
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
                           'tr_import',
                           'tr_internal',
                           'turb_import',
                           'turb_internal']),
        qd.observations([
            "tempo_no2_tropo",
            "tropomi_s5p_no2_tropo",
        ]),
        # forecast settings
        # mom6_iau is available. I don't know if we want run 3dvar without iau
        qd.iau(True),
        qd.forecast_length('PT12H'),
        qd.forecast_output_frequency('PT3H'),
        qd.clean_patterns(['*.nc4', '*.txt', 'logfile.*.out']),
        qd.inc_template(
            '/discover/nobackup/mabdiosk/rundir/handle_inc/'
            'GCC_c90_FPens.geoscf_jedi.20210805_0600z.nc4'
        ),
        qd.geos_cf_install_dir('/discover/nobackup/mabdiosk/GEOS-mil/GEOSgcm/install'),
        qd.geos_cf_run_dir('/discover/nobackup/mabdiosk/rundir/GCv14.0_GCMv1.17_c90_Skylab'),
        qd.swell_static_files('/discover/nobackup/projects/gmao/geos_cf_dev/SwellStaticFiles'),
        qd.geosfp_path('/discover/nobackup/projects/gmao/geos_cf_dev/jbarre')
    ]
)

suite_configs.register(suite_name, '3dvar_cf_cycle_tier1', _3dvar_cf_cycle_tier1)

# --------------------------------------------------------------------------------------------------

_3dvar_cf_cycle = QuestionList(
    questions=[
        _3dvar_cf_cycle_tier1
    ]
)

suite_configs.register(suite_name, '3dvar_cf_cycle', _3dvar_cf_cycle)
# --------------------------------------------------------------------------------------------------
