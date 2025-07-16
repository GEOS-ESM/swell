# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------

import importlib

from swell.utilities.swell_questions import QuestionContainer, QuestionList
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

from enum import Enum

_3dvar_container = importlib.import_module(f'swell.suites.3dvar.suite_config')
_3dvar_config = getattr(_3dvar_container, 'SuiteConfig')
_3dvar = getattr(_3dvar_config, '_3dvar')

# --------------------------------------------------------------------------------------------------

class SuiteConfig(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------

    compare_variational = QuestionList(
        list_name="compare",
        questions=[
            sq.compare,
            qd.runahead_limit(),
        ]
    )

    # --------------------------------------------------------------------------------------------------

    compare_3dvar = QuestionList(
        list_name="compare_3dvar",
        questions=[
            compare_variational,
            qd.model_components(['geos_marine']),
            _3dvar,

        ]
    )

    # --------------------------------------------------------------------------------------------------
