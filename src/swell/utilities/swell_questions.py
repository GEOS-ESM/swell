# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from dataclasses import dataclass, asdict, field
from typing import Optional
from enum import Enum


# --------------------------------------------------------------------------------------------------

@dataclass
class SwellQuestion:
    """Basic dataclass for defining Swell questions for suites and tasks"""
    default_value: str
    question_name: str
    dtype: str
    prompt: str
    question_type: str = None
    depends: Optional[dict] = None
    models: Optional[list] = None
    ask_question: bool = False
    options: Optional[str] = None

# --------------------------------------------------------------------------------------------------


class QuestionContainer:
    """ Class to extend question lists for suites and tasks, use with Enum """

    def __init__(self, *args):
        arg_dict = asdict(args[0])
        setattr(self, arg_dict['list_name'], args[0])

    @classmethod
    def get_all(self):
        return self._member_names_

# --------------------------------------------------------------------------------------------------


@dataclass
class QuestionList:
    """Basic dataclass containing a list of questions for each model, suite, task"""
    list_name: str
    questions: list

    geos_ocean: list = field(default_factory=lambda: [])
    geos_atmosphere: list = field(default_factory=lambda: [])
    geos_marine: list = field(default_factory=lambda: [])

    # --------------------------------------------------------------------------------------------------

    def expand_question_list(self):
        question_list = []

        for question_obj in self.questions:

            if isinstance(question_obj, Enum):
                question_obj = question_obj.value
            question = asdict(question_obj)

            if 'list_name' in question.keys():
                question_list.extend(question_obj.expand_question_list())
            else:
                question_list.append(question)

        return question_list

    # --------------------------------------------------------------------------------------------------

    def expand_question_list_model(self, model):
        question_list = []

        # Check the default question list to see if any groups have
        # Model specific questions specified
        for question_obj in self.questions:

            if isinstance(question_obj, Enum):
                question_obj = question_obj.value

            question = asdict(question_obj)

            if 'list_name' in question.keys():
                question_list.extend(question_obj.expand_question_list_model(model))

        # Add the model-specific questions
        if hasattr(self, model):
            for question_obj in getattr(self, model):
                question = asdict(question_obj)

                if 'list_name' in question.keys():
                    question_list.extend(question_obj.expand_question_list_model(model))
                else:
                    question_list.append(question)

        return question_list


# --------------------------------------------------------------------------------------------------


@dataclass
class SuiteQuestion(SwellQuestion):
    question_type: str = "suite"


# --------------------------------------------------------------------------------------------------

@dataclass
class TaskQuestion(SwellQuestion):
    question_type: str = "task"


# --------------------------------------------------------------------------------------------------

class QDtype(Enum):
    STRING = "string"
    STRING_CHECK_LIST = "string-check-list"
    STRING_DROP_LIST = "string-drop-list"
    BOOLEAN = "boolean"
    ISO_DURATION = "iso-duration"
    ISO_DATETIME = "iso-datetime"
    INTEGER = "integer"
    INTEGER_LIST = "integer-list"


# --------------------------------------------------------------------------------------------------
