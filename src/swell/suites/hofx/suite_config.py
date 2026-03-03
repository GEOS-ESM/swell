# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
from swell.configuration.question_defaults import QuestionDefaults as qd
from swell.suites.base.suite_questions import marine
from swell.suites.base.all_suites import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = 'hofx'

hofx_tier1 = QuestionList(
    list_name="hofx",
    questions=[
        marine,
        qd.cycling_varbc(),
        qd.window_type(),
        qd.jedi_build_method("use_existing"),
        qd.save_geovals(True),
        qd.model_components(['geos_atmosphere']),
    ],
    geos_atmosphere=[
        qd.horizontal_resolution("91"),
        qd.geos_x_background_directory("/discover/nobackup/projects/gmao/dadev/"
                                        "rtodling/archive/Restarts/JEDI/541x"),
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

suite_configs.register(suite_name, 'hofx_tier1', hofx_tier1)

# --------------------------------------------------------------------------------------------------

hofx = QuestionList(
    list_name="hofx",
    questions=[
        hofx_tier1
    ]
)

suite_configs.register(suite_name, 'hofx', hofx)

# --------------------------------------------------------------------------------------------------
