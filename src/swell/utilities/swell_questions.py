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
from isodate import parse_datetime, parse_duration, ISO8601Error


# --------------------------------------------------------------------------------------------------

class WidgetType(Enum):
    STRING = "string"
    STRING_CHECK_LIST = "string-check-list"
    STRING_DROP_LIST = "string-drop-list"
    BOOLEAN = "boolean"
    ISO_DURATION = "iso-duration"
    ISO_DATETIME = "iso-datetime"
    INTEGER = "integer"
    INTEGER_LIST = "integer-list"
    FILE_CHECK_LIST = "file-check-list"

    @property
    def is_drop_list(self) -> bool:
        return 'drop-list' in self.value

    @property
    def is_check_list(self) -> bool:
        return 'check-list' in self.value

    @property
    def base_type(self) -> type:
        """ Get the base type of the value based on the widget type. """
        if 'string' in self.value:
            return str
        if 'boolean' in self.value:
            return bool
        if 'integer' in self.value:
            return int
        if 'float' in self.value:
            return float
        if 'iso-' in self.value:
            return str

    def validate_value(self, value) -> bool:
        """ Validate that the value matches the type and format of the widget type. """
        base_type = self.base_type()

        # Check that the answer fits the base type
        if base_type == float:
            try:
                float(value)
            except ValueError:
                return False
        elif base_type == int:
            try:
                int(value)
            except ValueError:
                return False
        else:
            try:
                str(value)
            except ValueError:
                return False

        # If the widget is a datetime, ensure it is in the right format
        if self == WidgetType.ISO_DATETIME:
            try:
                parse_datetime(value)
            except ISO8601Error:
                return False

        # Ensure the value is a duration
        if self == WidgetType.ISO_DURATION:
            try:
                parse_duration(value)
            except ISO8601Error:
                return False

        return True


# --------------------------------------------------------------------------------------------------

@dataclass
class SwellQuestion:
    """Basic dataclass for defining Swell questions for suites and tasks"""
    default_value: str
    question_name: str
    widget_type: WidgetType
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

    def expand_question_list(self, model: Optional[str] = None):
        question_list = []

        # Loop through the items in the questions list
        for question_obj in self.questions:

            # If the item is a reference to an external list, get its value
            if isinstance(question_obj, Enum):
                question_obj = question_obj.value

            # Convert the dataclass into a dictionary
            question = asdict(question_obj)

            # If the item is a question list, expand its contents
            if 'list_name' in question.keys():
                question_list.extend(question_obj.expand_question_list())
            elif model is None:
                # Add to the model_independent question list
                question_list.append(question)

        # Look specifically for model-dependent questions
        if model is not None and hasattr(self, model):
            for model_obj in getattr(self, model):
                question = asdict(question_obj)

                if 'list_name' in question.keys():
                    question_list.extend(model_obj.expand_question_list(model))
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
