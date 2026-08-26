# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


import os
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Self, Union, Literal
from enum import Enum
from collections.abc import Mapping

from swell.utilities.datetime_util import is_datetime, is_duration
from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


class DataType(Enum):
    STRING = "string"
    BOOLEAN = "boolean"
    ISO_DURATION = "iso-duration"
    ISO_DATETIME = "iso-datetime"
    INTEGER = "integer"
    INTEGER_LIST = "integer-list"
    FLOAT = "float"
    LIST = "list"
    MAPPING = "mapping"
    NONE = "none"

    def is_type(self, value) -> bool:
        """ Validate that the value matches the data type. """

        if self == DataType.NONE:
            return value is None

        # Ensure value is in ISO datetime format
        if self == DataType.ISO_DATETIME:
            return is_datetime(value)

        # Ensure the value is in ISO duration format
        if self == DataType.ISO_DURATION:
            return is_duration(value)

        if self == DataType.STRING:
            return isinstance(value, str)
        
        if self == DataType.BOOLEAN:
            return isinstance(value, bool)

        if self == DataType.INTEGER:
            return isinstance(value, int)
        
        if self == DataType.INTEGER_LIST:
            if isinstance(value, list):
                return all([isinstance(item, int) for item in value])
            else:
                return False

        if self == DataType.FLOAT:
            return isinstance(value, float)    

        if self == DataType.LIST:
            return isinstance(value, list)

        if self == DataType.MAPPING:
            return isinstance(value, Mapping)

        return True


# --------------------------------------------------------------------------------------------------

@dataclass
class SwellQuestion:
    """Basic dataclass for defining Swell questions for suites and tasks"""
    default_value: str
    data_type: DataType
    prompt: str
    question_name: str | None = None
    question_type: str = None
    options: Optional[str] = None

    def __post_init__(self) -> None:
        if self.question_name is None:
            self.question_name = self.__class__.__name__

# --------------------------------------------------------------------------------------------------


class QuestionContainer:
    """ Class to extend question lists for suites and tasks, use with Enum """

    def __init__(self, *args):
        arg_dict = asdict(args[0])
        setattr(self, arg_dict['list_name'], args[0])

    @classmethod
    def get_all(cls):
        return cls._member_names_

# --------------------------------------------------------------------------------------------------


@dataclass
class QuestionList:
    """Basic dataclass containing a list of questions for each model, suite, task"""
    list_name: str
    questions: List[Union[SwellQuestion, Self]]

    geos_atmosphere: list = field(default_factory=lambda: [])
    geos_cf: list = field(default_factory=lambda: [])
    geos_marine: list = field(default_factory=lambda: [])

    # --------------------------------------------------------------------------------------------------

    def get_all_question_names(self, suite_task: Optional[Literal['suite', 'task']] = None) -> None:
        question_list = []
        for model in [None] + os.listdir(os.path.join(get_swell_path(),
                                                      'configuration', 'jedi', 'interfaces')):
            question_list.extend([q for q in self.expand_question_list(model)])

        if suite_task is not None:
            out_list = [q['question_name'] for q in question_list if
                        q['question_type'] == suite_task]
        else:
            out_list = [q['question_name'] for q in question_list]

        return sorted(list(set(out_list)))

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
                question_list.extend(question_obj.expand_question_list(model))
            elif model is None:
                # Add to the model_independent question list
                question_list.append(question)

        # Look specifically for model-dependent questions
        if model is not None and hasattr(self, model):
            for question_obj in getattr(self, model):
                # If the item is a reference to an external list, get its value
                if isinstance(question_obj, Enum):
                    question_obj = question_obj.value
                question = asdict(question_obj)

                if 'list_name' in question.keys():
                    question_list.extend(question_obj.expand_question_list(model))
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
