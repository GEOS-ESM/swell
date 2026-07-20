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

    localensembleda_tier1 = QuestionList(
        list_name="localensembleda",
        questions=[
            sq.marine,
            qd.ensemble_hofx_packets(),
            qd.ensemble_hofx_strategy(),
            qd.ensemble_num_members(),
            qd.skip_ensemble_hofx(),
            qd.final_cycle_point("2023-10-10T12:00:00Z"),
            qd.jedi_build_method("use_existing"),
            # Demonstrate multi-model settings
            qd.model_components(['geos_atmosphere', 'geos_marine']),
        ],
        geos_atmosphere=[
            qd.horizontal_resolution('91'),
            qd.background_experiment('x0050'),
            qd.geos_x_background_directory('/discover/nobackup/projects/gmao/dadev/'
                                           'rtodling/archive/Restarts/JEDI/541x'),
            qd.geos_x_ensemble_directory('/discover/nobackup/projects/gmao/dadev/'
                                         'rtodling/archive/541/Milan'),
            qd.npx_proc(3),
            qd.npy_proc(3),
            qd.cycle_times(['T00']),
            qd.background_time_offset("PT3H"),
            qd.ensemble_num_members(2),
            qd.skip_ensemble_hofx(True),
            qd.local_ensemble_solver("Deterministic GETKF"),
            qd.local_ensemble_use_linear_observer(False),
            qd.ensmean_only(False),
            qd.local_ensemble_save_posterior_mean(True),
            qd.local_ensemble_save_posterior_mean_increment(True),
            qd.local_ensemble_save_posterior_ensemble(False),
            qd.local_ensemble_save_posterior_ensemble_increments(False),
            qd.obs_thinning_rej_fraction(0.75),
            qd.observations([
                "atms_n20",
            ]),
            qd.window_type("3D"),
            qd.clean_patterns(['*.txt'])
        ],
        # Demonstrator for different values of ensemble_num_members
        geos_marine=[
            qd.ensemble_num_members(7)
        ]
    )


    # --------------------------------------------------------------------------------------------------

    localensembleda = QuestionList(
        list_name="localensembleda",
        questions=[
            localensembleda_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------
