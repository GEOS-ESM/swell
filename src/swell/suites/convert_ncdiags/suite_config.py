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
from swell.suites.base.suite_questions import common
from swell.suites.base.all_suites import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = 'convert_ncdiags'

convert_ncdiags_tier1 = QuestionList(
    questions=[
        common,
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
        qd.observations([
            "aircraft",
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
        qd.path_to_gsi_nc_diags("/discover/nobackup/projects/gmao/advda/SwellTestData/"
                                "ufo_testing/ncdiagv2/%Y%m%d%H"),
    ]
)

suite_configs.register(suite_name, 'convert_ncdiags_tier1', convert_ncdiags_tier1)

# --------------------------------------------------------------------------------------------------

convert_ncdiags = QuestionList(
    questions=[
        convert_ncdiags_tier1
    ]
)

suite_configs.register(suite_name, 'convert_ncdiags', convert_ncdiags)

# --------------------------------------------------------------------------------------------------
