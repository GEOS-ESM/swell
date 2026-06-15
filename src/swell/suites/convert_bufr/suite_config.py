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
from swell.suites.base.suite_attributes import suite_configs


# --------------------------------------------------------------------------------------------------

suite_name = 'convert_bufr'

convert_bufr = QuestionList(
    questions=[
        common,
        qd.start_cycle_point("2023-10-10T00:00:00Z"),
        qd.final_cycle_point("2023-10-10T06:00:00Z"),
        qd.jedi_build_method("use_existing"),
        qd.model_components(['geos_atmosphere']),
    ],
    geos_atmosphere=[
        qd.cycle_times(['T00', 'T06', 'T12', 'T18']),
        qd.clean_patterns([
            "gsi_bcs/*.nc4",
            "gsi_bcs/*.txt",
            "ioda/*/temporary*.nc",
        ]),
        qd.bufr_obs_classes([
            "ncep_1bamua_bufr",
            "ncep_atms_bufr",
            "ncep_avcsam_bufr",
            "ncep_avcspm_bufr",
            "ncep_mhs_bufr",
            "ncep_mtiasi_bufr",
            "ncep_gpsro_bufr",
            # "ncep_ssmis_bufr",
            # "ncep_crisfsr_bufr",  DNE in 2023
            # "ncep_acftpfl_bufr",
            # "disc_airs_bufr",
            # "disc_amsua_bufr",
            # "gmao_amsr2_bufr",
            # "gmao_gmi_bufr",
            # "gmao_mlst_bufr",
            # "m2scr_n21_ompslp_nc",
            # "mls_nrt_nc",
            # "ncep_acftpfl_bufr",
            # "ncep_aura_omi_bufr",
            # "ncep_goesfv_bufr",
            # "ncep_gpsro_bufr",
            # "ncep_prep_bufr",
            # "ncep_satwnd_bufr",
            # "ncep_tcvitals",
            # "npp_ompsnm_bufr",
            # "r21c_npp_ompslp_nc",
        ]),
    ]
)

suite_configs.register(suite_name, 'convert_bufr', convert_bufr)

# --------------------------------------------------------------------------------------------------
