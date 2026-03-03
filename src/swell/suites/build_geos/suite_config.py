# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
from swell.suites.base.suite_questions import all_suites
from swell.suites.base.all_suites import suite_configs

suite_name = 'build_geos'

# --------------------------------------------------------------------------------------------------

build_geos = QuestionList(
    list_name="build_geos",
    questions=[
        all_suites
    ]
)

suite_configs.register(suite_name, 'build_geos', build_geos)

# --------------------------------------------------------------------------------------------------
