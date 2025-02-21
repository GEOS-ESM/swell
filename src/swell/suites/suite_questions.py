# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from enum import Enum
from dataclasses import asdict

from swell.utilities.swell_questions import QuestionList, QuestionContainer
from swell.suites.suite_question_defaults import SuiteQuestionDefaults as sq
from swell.tasks.task_question_defaults import TaskQuestionDefaults as tq


# --------------------------------------------------------------------------------------------------

class SuiteQuestions(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    all_suites = QuestionList(
        list_name="all_suites",
        questions=[
            sq.experiment_id(),
            sq.experiment_root()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    common = QuestionList(
        list_name="common",
        questions=[
            all_suites,
            sq.cycle_times(),
            sq.start_cycle_point(),
            sq.final_cycle_point(),
            sq.model_components(),
            sq.runahead_limit()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    marine = QuestionList(
        list_name="marine",
        questions=[
            common,
            sq.marine_models()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dfgat_atmos = QuestionList(
        list_name="3dfgat_atmos",
        questions=[
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dfgat_cycle = QuestionList(
        list_name="3dfgat_cycle",
        questions=[
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_tier1 = QuestionList(
        list_name="3dvar_tier1",
        questions=[
            marine,
            sq.start_cycle_point(default_value='2021-07-01T12:00:00Z'),
            sq.final_cycle_point(default_value='2021-07-01T12:00:00Z'),
            tq.jedi_build_method(default_value='use_existing'),
            sq.model_components(default_value=['geos_ocean'])
        ],
        geos_ocean=[
            sq.cycle_times(default_value=['T12']),
            tq.window_length(default_value='P1D'),
            tq.window_offset(default_value='P12H'),
            tq.horizontal_resolution(default_value='72x36'),
            tq.vertical_resolution(default_value=50),
            tq.total_processors(default_value=6),
            tq.obs_experiment(default_value='s2s_v1'),
            tq.observations(default_value=[
                'adt_cryosat2n',
                'adt_jason3',
                'adt_saral',
                'adt_sentinel3a',
                'adt_sentinel3b',
                'insitu_profile_argo',
                'sst_ostia',
                'sss_smos',
                'sss_smapv5',
                'sst_abi_g16_l3c',
                'sst_gmi_l3u',
                'sst_viirs_n20_l3u',
                'temp_profile_xbt'
            ]),
            tq.obs_provider(default_value=['odas', 'gdas_marine']),
            tq.analysis_forecast_window_offset(default_value='-PT12H'),
            tq.background_time_offset(default_value='PT18H'),
            tq.clean_patterns(default_value=['*.nc4', '*.txt'])
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar = QuestionList(
        list_name="3dvar",
        questions=[
            _3dvar_tier1
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_atmos = QuestionList(
        list_name="3dvar_atmos",
        questions=[
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_cycle = QuestionList(
        list_name="3dvar_cycle",
        questions=[
            marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    convert_ncdiags = QuestionList(
        list_name="convert_ncdiags",
        questions=[
            common
        ]
    )

    # --------------------------------------------------------------------------------------------------

    forecast_geos = QuestionList(
        list_name="forecast_geos",
        questions=[
            sq.cycle_times(),
            sq.final_cycle_point(),
            sq.start_cycle_point()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    hofx = QuestionList(
        list_name="hofx",
        questions=[
            marine,
            sq.window_type()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    localensembleda = QuestionList(
        list_name="localensembleda",
        questions=[
            marine,
            sq.ensemble_hofx_packets(),
            sq.ensemble_hofx_strategy(),
            sq.skip_ensemble_hofx(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    ufo_testing = QuestionList(
        list_name="ufo_testing",
        questions=[
            common,
        ]
    )


# --------------------------------------------------------------------------------------------------
