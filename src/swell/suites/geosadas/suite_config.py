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
from swell.suites.base.suite_questions import all_suites
from swell.suites.base.all_suites import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = 'geosadas'

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

suite_configs.register(suite_name, 'geosadas_tier1', geosadas_tier1)

# --------------------------------------------------------------------------------------------------

geosadas = QuestionList(
    list_name="geosadas",
    questions=[
        geosadas_tier1
    ]
)

suite_configs.register(suite_name, 'geosadas', geosadas)

# --------------------------------------------------------------------------------------------------
