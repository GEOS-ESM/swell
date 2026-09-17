## Adding questions

### Overview
Questions in swell are classes that are used to store information for parameters. This includes information such as default value, expected type, meaning, and conditions for relevance. They are used during experiment creation to fill out parameters in `experiment.yaml`, and template `flow.cylc`. Upon task execution, they are used to determine which parameters are available to the task's config.

Questions for swell are stored as dataclass instances, in the file `src/swell/utilities/question_defaults.py`. Dataclasses allow for simple declaration of data fields, and powerful type checking capabilities. Each question is an extension of the `SuiteQuestion` or `TaskQuestion` class, which are extensions of the `SwellQuestion` parent:

```python
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
```

Arguments:
- default_value: default value for the answer
- question_name: name of the question (should usually match the class).
- widget_type: A custom enum specifying the data type of the answer, as well as the way the question will be asked on the command line interface. Options include drop lists, check lists, and direct entry.
- prompt: A sentence or two describing the question.
- question_type: "task" or "suite", use the `SuiteQuestion` or `TaskQuestion` parent classes to set this automatically.
- depends: A dictionary specifying default values to be used if certain other questions are asked.
- models: List of models the question applies to, can also use `["all_models"]` or `None`.
- ask_question: (Currently unused)
- options: List of valid options for the answer

An example question class:
```python
@dataclass
class existing_jedi_build_directory(TaskQuestion):
    default_value: str = "defer_to_platform"
    question_name: str = "existing_jedi_build_directory"
    ask_question: bool = True
    # Need construct lists and dictionaries using this constructor method because
    # dataclass fields cannot be initialized to mutable types.
    # https://docs.python.org/3/library/dataclasses.html#mutable-default-values
    depends: Dict = mutable_field({
        "jedi_build_method": "use_existing"
    })
    prompt: str = "What is the path to the existing JEDI build directory?"
    widget_type: WidgetType = WidgetType.STRING
```
Calling `existing_jedi_build_directory()` creates an object matching the default values for the class. The specific values `defer_to_platform`, `defer_to_model`, and `defer_to_code` are special values that will be substituted as follows, depending on the `platform` and `model`: 
- defer_to_platform: src/swell/deployment/platforms/<platform>
- defer_to_model: src/swell/configuration/jedi/interfaces/<model>
- defer_to_code: Set by src/swell/deployment/prepare_config_and_suite/prepare_config_and_suite.py

Alternative values can be set as needed for different applications, using positional or keyword arguments:
```python
question = existing_jedi_build_directory('/example')
```
```python
question = existing_jedi_build_directory(options=['example1', 'example2'])
```

### Suite and task questions
Swell questions are divided into two categories, suite and task. Suite questions are *exclusively* set in each suite's `suite_config.py` file, and are understood to *always* be asked at the beginning of experiment creation (For more about suite configs, see [Adding a suite](adding_a_suite.md)). These are high-level options used to set decisions in workflow execution, such as deciding which tasks are run in `flow.cylc`. Because they make large decisions that have impacts on other files, such as `flow.cylc`, suite questions should be changed *only* at experiment creation, using the override file or cli (not by altering `experiment.yaml` after creation).

Task questions are associated with tasks, and are only asked if their parent task is called by the workflow's `flow.cylc` file. The file `src/swell/tasks/task_questions.py` is used to associate questions with tasks.

task_questions.py
```
CloneGeosMksi = QuestionList(
    list_name="CloneGeosMksi",
    questions=[
        qd.observing_system_records_mksi_path(),
        qd.observing_system_records_mksi_path_tag()
    ]
)
```

`task_questions.py` is used during experiment creation to determine which questions are asked. It is also used during runtime to construct the task's `config` object, thus it is necessary to update `task_questions.py` with the parameters that are needed by the task so they can be used (even if they are already present in `experiment.yaml`). 

Task question parameters are *generally* safer to alter after creation than suite questions. This, along with the fact that suite questions are always asked, means that suite vs task questions can also be thought of as `fixed` vs `dynamic` configuration options.