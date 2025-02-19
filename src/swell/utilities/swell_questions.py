# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


from dataclasses import dataclass, asdict
from typing import List, Union, Optional


# --------------------------------------------------------------------------------------------------

@dataclass
class SwellQuestion:
    """Basic dataclass for defining Swell questions for suites and tasks"""
    question_name: str
    dtype: str
    default_value: str
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
    list_type: str = None
    
    def expand_question_list(self):
        question_list=[]
        for question_obj in self.questions:
            #print(question_obj)
            question = asdict(question_obj)

            if 'list_type' in question.keys():
                # This is a sub-list, expand its contents
                question_list.extend(question_obj.expand_question_list())
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
