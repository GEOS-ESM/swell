# A Guide to Suite Configurations in Swell

# Introduction

This document provides a high-level overview of the structure of a Swell suite, with the goal of providing context and basic instructions to a user looking to add a suite to Swell. It can also serve as a primer for users less familiar to Swell. 

## Definitions

- Experiment: A particular set of parameters and instructions for execution. These are stored in the "experiment directory", along with any necessary input files and results once it is run. Part of Swell's functionality is to dynamically generate experiments, and then run them.

- Suite: A class of experiments. Suites form the highest level of structure for generating experiments.

- Task: A step in the experiment. Tasks have various functions, some simple, some more complex. The `flow.cylc` file of the suite determines the order that tasks are executed in. Depending on need, tasks can be run sequentially or in parallel, with complex dependency trees.

- Questions: Used to set parameters during experiment creation. In the Swell context, these are objects that store information including default values, prompts describing the meaning of the answer, valid answer options and data types, and conditionals. Suites and tasks have sets of associated questions, which are consulted when building the experiment.

# Broad Overview of Experiments

The two most basic parts to an experiment are the `experiment.yaml` config, and the `flow.cylc` workflow file. Examples of each follow. Workflows and configs for existing suites are also a good source of more detailed examples.

## Example Experiment Config

`experiment.yaml` sets values for parameters used in the code. This is an example snippet from the Swell suite `3dvar_marine`:

```yaml
# What is the experiment id?
experiment_id: swell-3dvar_marine

# What is the experiment root (the directory where the experiment will be stored)?
experiment_root: /discover/nobackup/manstett/SwellExperiments

# What is the time of the first cycle (middle of the window)?
start_cycle_point: '2021-07-01T12:00:00Z'

# What is the time of the final cycle (middle of the window)?
final_cycle_point: '2021-07-01T12:00:00Z'

# List of models in this experiment
model_components:
- geos_marine

# Configurations for the model components.
models:

  # Configuration for the geos_marine model component.
  geos_marine:

    # Enter the cycle times for this model.
    cycle_times:
    - T12

    # Which background error model do you want to use?
    background_error_model: explicit_diffusion
```

The questions near the top of the file are suite questions, and are referred to as "model independent". The section under "models" describes parameters used by the `geos_marine` model. Some tasks are shared across models, necessitating different values for the same parameter depending on model. Thus, these parameters are referred to as "model dependent".

## Example Experiment Workflow

The `flow.cylc` file instructs `cylc` which tasks to run, and in what order. The `scheduler` section sets the order of tasks and their dependencies. For example, here is a small snippet of a `flow.cylc` generated for `3dvar_marine`.

```
[scheduling]

    initial cycle point = 2021-07-01T12:00:00Z
    final cycle point = 2021-07-01T12:00:00Z
    runahead limit = P4

    [[graph]]
        R1 = """
            # Triggers for non cycle time dependent tasks
            # -------------------------------------------
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi

        """
```
For context, tasks in `R1` are run as setup for later tasks. Here, `CloneJedi` is triggered first. When `CloneJedi` completes, `BuildJediByLinking` is triggered, but the question mark denotes that it is optional to complete. Should it fail, the task `BuildJedi` is triggered.

The actions associated with these tasks is defined in the `runtime` section of `flow.cylc`. Here is the runtime section for the tasks above:

```
[runtime]

    # Task defaults
    # -------------
    [[root]] 
        pre-script = "source $CYLC_SUITE_DEF_PATH/modules"
    
        [[[environment]]]
            datetime = $CYLC_TASK_CYCLE_POINT
            config   = $CYLC_SUITE_DEF_PATH/experiment.yaml
            
    # Tasks 
    # -----
    [[CloneJedi]]
        script = "swell task CloneJedi $config"

    [[BuildJediByLinking]]
        script = "swell task BuildJediByLinking $config"

    [[BuildJedi]]
        script = "swell task BuildJedi $config"
        platform = nccs_discover_sles15
        execution time limit = PT3H
        [[[directives]]]
            --job-name = BuildJedi
            --qos = allnccs
            --nodes = 1
            --ntasks-per-node = 64
            --constraint = mil

``` 

The `root` section defines actions and variables shared by all tasks. Note that `BuildJedi` has more complex cylc options than the other tasks.

## How the experiment is created

When an experiment is created using `swell create <suite>`, a dictionary of questions is pieced together from questions associated with the suite and its member tasks. Answers for these questions are set either from default configurations, from user input on the command line, or overridden from a specified file. In a complex process, the answers provided are then used to generate the `experiment.yaml` and the experiment's `flow.cylc file. 

# Creating a Suite

There are multiple steps and things to account when for creating a suite for Swell. This is a crude overview of the basic steps to consider when implementing a suite. Development of new suites will likely require more advanced consideration than what is described here. 

In abstract, these are the steps towards designing swell workflows:
1. Envision a set of tasks that need to be done:
- Tasks should be thought of as a unit of work comprising a complete step in the process. 
- Ideally, unneeded redundancy should be minimized, with an eye towards modularity.
- If practical, consider generalizing tasks to be used in multiple contexts.
- Consider the computational requirements for the task. 
2. Figure out a workflow that most efficiently runs these tasks. Some things to consider:
- Which tasks depend on the status of other tasks, and which are independent?
- Do some tasks need to be run multiple times?
3. Figure out the important "questions" that need to be asked about the experiment.
- Separate these into suite and task questions (most questions being added will likely be task questions).

Creating visualizations such as flowcharts may help in designing workflows.

In practice, there are three major steps towards creating a suite. Completing all of these steps is necessary to make the suite work, so these steps will likely be done iteratively/non-linearly:

1. Write the tasks.
2. Create the `flow.cylc` file.
3. Add the appropriate suite and task question lists.

More detailed instructions and examples for these steps follows in this section.

### Writing tasks

For more information on tasks, see: [Adding Tasks](adding_a_suite.md)

### Creating the flow.cylc template

For more detailed information on cylc workflows, see the [cylc documentation](https://cylc.github.io/cylc-doc/latest/html/index.html). Existing Swell suite workflows can also provide useful examples to consider. 

Suite workflows are stored in `src/swell/suites/<suite>`.

The experiment `flow.cylc` file is generated from a suite template using a `jinja2` process. For example, here is part of a suite template, versus a filled-in experiment `flow.cylc`. During creation, specified questions are used to fill in the template:

```
[scheduling]

    initial cycle point = {{start_cycle_point}}
    final cycle point = {{final_cycle_point}}
    runahead limit = {{runahead_limit}}
```
```
[scheduling]

    initial cycle point = 2021-07-01T12:00:00Z
    final cycle point = 2021-07-01T12:00:00Z
    runahead limit = P4
```

For initial development/testing purposes, it may be easier to create a `flow.cylc` using hard-coded values, then replace these with `jinja2` templated values as the suite nears completion.

### Question Lists

Each individual suite and most tasks have an associated list of questions which are used to create the experiment. For more on questions themselves, see [Adding questions](adding_questions.md).

Suite question lists are stored in `src/swell/suites/<suite>/suite_config.py`
Task question lists are stored in `src/swell/tasks/task_questions.py`

`QuestionList` objects store and handle questions in an object-oriented manner. They can store questions directly, or store other lists to use their questions. Here is an example of a question list for a task: 

```python
    BuildJediByLinking = QuestionList(
        list_name="BuildJediByLinking",
        questions=[
            qd.existing_jedi_build_directory(),
            qd.existing_jedi_build_directory_pinned(),
            qd.jedi_build_method()
        ]
    )
```

During experiment creation, Swell scans the suite's `flow.cylc` file to find all of the tasks used in the workflow. It then finds the corresponding task lists in `src/swell/tasks/task_questions.py`, and fits together a list of uniquely named questions from all of the lists. Questions have a priority depending on order. In the case of duplicate questions, those further DOWN the list take priority. For this reason, it is NOT RECOMMENDED to set different default values for tasks in `task_questions.py`, since questions may be overridden by a questions in a different task. 

In this question infrastructure, **suites take priority over tasks**. Any question specified in a suite configuration will override the default value for a question in one of its member tasks. This allows for easily setting different configurations for suites without having to specify redundant questions. For ease of use, model-dependent questions can be assigned directly in their respective lists.

Consider the following example of suite questions for `3dvar_marine` (in python, variable names cannot begin with digits):

```python
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.suites.suite_questions import SuiteQuestions as sq

class SuiteQuestions(QuestionContainer, Enum):

    # --------------------------------------------------------------------------------------------------
    # Shared groups of questions across suites
    # --------------------------------------------------------------------------------------------------

    all_suites = QuestionList(
        list_name="all_suites",
        questions=[
            qd.experiment_id(),
            qd.experiment_root()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    common = QuestionList(
        list_name="common",
        questions=[
            all_suites,
            qd.cycle_times(),
            qd.start_cycle_point(),
            qd.final_cycle_point(),
            qd.model_components(),
            qd.runahead_limit()
        ]
    )

    # --------------------------------------------------------------------------------------------------

    marine = QuestionList(
        list_name="marine",
        questions=[
            common,
            qd.marine_models()
        ]
    )
```


```python
class SuiteConfig(QuestionContainer, Enum):

    _3dvar_marine_base = QuestionList(
        list_name="3dvar_marine_base",
        questions=[
            sq.marine
        ]
    )

    # --------------------------------------------------------------------------------------------------

    _3dvar_marine_tier1 = QuestionList(
        list_name="3dvar_marine_tier1",
        questions=[
            _3dvar_base,
            qd.start_cycle_point("2021-07-01T12:00:00Z"),
            qd.final_cycle_point("2021-07-01T12:00:00Z"),
            qd.jedi_build_method("use_existing"),
            qd.model_components(['geos_marine']),
        ],
        geos_marine=[
            qd.cycle_times(['T12']),
            qd.marine_models(['mom6']),
            qd.window_length("P1D"),
            qd.horizontal_resolution("72x36"),
            qd.vertical_resolution("50"),
            qd.total_processors(6),
            qd.obs_experiment("s2s_v1"),
            qd.observations([
                "adt_cryosat2n",
                "adt_jason3",
                "adt_saral",
                "adt_sentinel3a",
                "adt_sentinel3b",
                "insitu_profile_argo",
                "sst_ostia",
                "sss_smos",
                "sss_smapv5",
                "sst_abi_g16_l3c",
                "sst_gmi_l3u",
                "sst_viirs_n20_l3u",
                "temp_profile_xbt"
            ]),
            qd.obs_provider(['odas', 'gdas_marine']),
            qd.background_time_offset("PT18H"),
            qd.clean_patterns(['*.nc4', '*.txt']),
        ]
    )
```
The class `SuiteQuestions` contains lists of questions which are common to many suites. This avoids the need for redundantly setting the same questions for every suite.

`_3dvar_marine_base` is responsible for establishing the baseline for questions used by the suite. The 'base' list should be used to associate all questions used by the suite. This list will be populated with the questions that match the defaults in `QuestionDefaults` (`src/swell/utilities/question_defaults.py`). However, in many cases, those defaults will not be ideal defaults for the individual suite. Thus, `_3dvar_marine_tier1` sets different default values which override the question defaults. If desired, other configurations can then inherit question defaults from `_3dvar_marine_tier1`, and set their own defaults on top of the existing ones.
