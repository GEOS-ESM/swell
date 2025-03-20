# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from swell.utilities.swell_questions import QuestionList
from swell.suites.suite_questions import SuiteQuestions as sq

# --------------------------------------------------------------------------------------------------

build_geos_base = QuestionList(
    list_name="build_geos",
    questions=[
        sq.all_suites
    ]
)

# --------------------------------------------------------------------------------------------------

build_geos = QuestionList(
    list_name="build_geos",
    questions=[
        build_geos_base
    ]
)

# --------------------------------------------------------------------------------------------------
