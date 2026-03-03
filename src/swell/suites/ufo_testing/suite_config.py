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
from swell.suites.base.suite_questions import common
from swell.suites.base.all_suites import suite_configs

# --------------------------------------------------------------------------------------------------

suite_name = 'ufo_testing'

ufo_testing_tier1 = QuestionList(
    list_name="ufo_testing",
    questions=[
        common,
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
        qd.path_to_gsi_bc_coefficients("/discover/nobackup/projects/gmao/dadev/rtodling/"
                                        "archive/541/Milan/x0050/ana/Y%Y/M%m/"
                                        "*bias*%Y%m%d_%Hz.txt"),
        qd.path_to_gsi_nc_diags("/discover/nobackup/projects/gmao/dadev/rtodling/archive/"
                                "541/Milan/x0050/obs/Y%Y/M%m/D%d/H%H/"),
    ]
)

suite_configs.register(suite_name, 'ufo_testing_tier1', ufo_testing_tier1)

# --------------------------------------------------------------------------------------------------

ufo_testing = QuestionList(
    list_name="ufo_testing",
    questions=[
        ufo_testing_tier1
    ]
)

suite_configs.register(suite_name, 'ufo_testing', ufo_testing)

# --------------------------------------------------------------------------------------------------
