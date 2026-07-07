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

    eda_controlpert_atmos_tier1 = QuestionList(
        list_name="eda_controlpert_atmos_tier1",
        questions=[
            sq.common,
            qd.start_cycle_point("2023-10-10T00:00:00Z"),
            qd.final_cycle_point("2023-10-10T06:00:00Z"),
            qd.runahead_limit("P2"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_atmosphere']),
        ],
        geos_atmosphere=[
            qd.cycle_times([
                "T00",
            ]),
            qd.geos_x_background_directory("/discover/nobackup/projects/gmao/"
                                           "dadev/rtodling/archive/Restarts/JEDI/541x"),
            qd.geos_x_ensemble_directory('/discover/nobackup/projects/gmao/dadev/'
                                         'rtodling/archive/541/Milan'),
            qd.npx_proc(4),
            qd.npy_proc(5),
            qd.window_length("PT6H"),
            qd.window_type("3D"),
            qd.horizontal_resolution("91"),
            qd.gsibec_nlats("91"),
            qd.gsibec_nlons("144"),
            qd.vertical_resolution("72"),
            qd.ensemble_num_members(32),
            qd.ensemble_num_chunks(8),
            qd.number_of_iterations([100]),
            qd.gradient_norm_reduction(1.e-8),
            qd.analysis_variables([
                "eastward_wind",
                "northward_wind",
                "air_temperature",
                "water_vapor_mixing_ratio_wrt_moist_air",
                "air_pressure_at_surface",
                "cloud_liquid_ice",
                "cloud_liquid_water",
                "rain_water",
                "snow_water",
                "mole_fraction_of_ozone_in_air",
                "geopotential_height_times_gravity_at_surface",
                "fraction_of_ocean",
                "fraction_of_lake",
                "fraction_of_ice",
                "skin_temperature_at_surface"
            ]),
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
            qd.obs_thinning_rej_fraction(0.8),
#            qd.ensmeanvariance_spec([
#                {"state": "bkg",
#                 "fn_input": "ebkg/mem%mem%/geos.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4",
#                 "fn_output_mean": "geos.prior.mean",
#                 "fn_output_variance": "geos.prior.variance",
#                 "grid_type": ['cs', 'latlon']},
#                {"state": "analysis",
#                 "fn_input": "analysis/mem%mem%/eda.ana.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4",
#                 "fn_output_mean": "eda.ana.mean",
#                 "fn_output_variance": "eda.ana.variance",
#                 "grid_type": ['cs', 'latlon']},
#                ]),
#            qd.diffstates_spec({
#                "state1":
#                {"fn_input": "geos.prior.mean.%yyyy%mm%dd_%hh%MM%ssz.nc4"},
#                "state2":
#                {"fn_input": "eda.ana.mean.%yyyy%mm%dd_%hh%MM%ssz.nc4"},
#                "state_diff":
#                {"fn_output": "eda.mean-inc", "grid_type": ['cs', 'latlon']},
#                "state_type": "ensemble"
#                }),
            qd.clean_patterns(['*.txt', '*.csv']),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    eda_controlpert = QuestionList(
        list_name="eda_controlpert",
        questions=[
            eda_controlpert_atmos_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
