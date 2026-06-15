# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
from swell.configuration import question_defaults as qd
from swell.suites.base.suite_questions import common
from swell.suites.base.suite_attributes import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = '3dvar_cf'

_3dvar_cf_tier1 = QuestionList(
    questions=[
        common,
        qd.swell_static_files("/discover/nobackup/projects/gmao/geos_cf_dev/SwellStaticFiles"),
        qd.start_cycle_point("2023-08-05T18:00:00Z"),
        qd.final_cycle_point("2023-08-05T18:00:00Z"),
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
        qd.observations([
            "tempo_no2_tropo",
            "tropomi_s5p_no2_tropo",
        ]),
        qd.clean_patterns(['*.txt', 'logfile.*.out']),
    ]
)

suite_configs.register(suite_name, '3dvar_cf_tier1', _3dvar_cf_tier1)

# --------------------------------------------------------------------------------------------------

_3dvar_cf = QuestionList(
    questions=[
        _3dvar_cf_tier1
    ]
)

suite_configs.register(suite_name, '3dvar_cf', _3dvar_cf)

# --------------------------------------------------------------------------------------------------
