# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum


# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    letkf_marine = QuestionList(
        list_name="letkf_marine",
        questions=[
            sq.marine,
            qd.ensemble_hofx_packets(),
            qd.ensemble_hofx_strategy(),
            qd.skip_ensemble_hofx(),
            qd.start_cycle_point("2023-01-02T12:00:00Z"),
            qd.final_cycle_point("2023-01-02T12:00:00Z"),
            qd.model_components(['geos_marine']),
        ],q
        geos_marine=[
            qd.cycle_times(['T12']),
            qd.marine_models(['mom6']),
            qd.window_length("P1D"),
            qd.horizontal_resolution("72x36"),
            qd.vertical_resolution("50"),
            qd.total_processors(6),
            qd.observations([
                "adt_sentinel6a",
                "insitu_profile_argo",
                "sss_smos",
                "sst_viirs_n20_l3u",
            ]),
            qd.background_time_offset("PT18H"),
            qd.background_experiment("fgat_jra55"),
            qd.ensemble_num_members(3),
            qd.skip_ensemble_hofx(True),
            qd.local_ensemble_use_linear_observer(False),
            qd.ensmean_only(False),
            qd.local_ensemble_save_posterior_mean(True),
            qd.local_ensemble_save_posterior_mean_increment(True),
            qd.local_ensemble_save_posterior_ensemble(False),
            qd.local_ensemble_save_posterior_ensemble_increments(False),
            qd.obs_thinning_rej_fraction(0.75),
            qd.window_type("3D"),
            qd.clean_patterns(['*.nc4', '*.txt']),
        ]
    )

    # --------------------------------------------------------------------------------------------------
