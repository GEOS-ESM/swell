# Templating cylc workflows within swell
The `flow.cylc` file informs the `Cylc` workflow engine on how to run an experiment. This includes the order in which tasks should be run, and the scripts and environment variables necessary for each task. Templating a workflow within Swell previously used `jinja2` templating on a file named `flow.cylc` under each suite. This has been replaced with an approach that uses a python class to manipulate strings to generated the `flow.cylc` used in the experiment. This allows for more complex logic to be performed in generating the workflow, but also may be confusing to users. This documentation serves to explain the new method of templating workflows under these changes.

## Cylc sections

The `flow.cylc` that is generated under this method is not much different from the one generated before, and users shouldn't notice a difference when it comes to creating an experiment, using overrides, etc. When creating an experiment, `swell` consults a file `src/swell/suites/<suite>/workflow.py` on how to construct the suite. This file should be an extension of the `CylcWorkflow` class (defined in `src/swell/utilities/cylc_workflow.py`). The method `get_workflow_string` is called to return a string which fills the contents of the `flow.cylc` file. Overriding this method is used to manually specify the contents of the file. Typically, the graph section is templated in `jinja2`, and the runtime sections for each task are generated using swell's `TaskAttribute` class. However, the entire `flow.cylc` file can be templated in `jinja`, if necessary.


## Tasks and the runtime section

Swell will parse the graph section, which is constructed first, to obtain the tasks which are used by the experiment. It will then build the runtime section by consulting `src/swell/tasks/task_attributes.py`. Since swell tasks broadly fall into only a few categories (model-dependent or independent, cycling or non-cycling) that do not differ much between suites, they are easily abstracted into a `Task` class. This class will dynamically set attributes such as messaging parameters and slurm settings.

```python
class CloneJedi(Task):
    def set_attributes(self):
        self.question_list = QuestionList([
            qd.bundles(),
            qd.existing_jedi_source_directory(),
            qd.existing_jedi_source_directory_pinned(),
            qd.jedi_build_method()
        ])


class EvaObservations(Task):
    def set_attributes(self):
        self.time_limit = True
        self.is_cycling = True
        self.is_model = True
        self.slurm = {}
        self.question_list = QuestionList([
            background_crtm_obs,
            qd.marine_models(),
            qd.observing_system_records_path(),
            qd.window_offset(),
            qd.marine_models(),
        ])
```

Attributes are set by override the `set_attributes` method in `Task`. This has been combined with the previously-used `task_questions.py` for simplicity. Here, the tags `is_cycling` and `is_model` are used to specify what tags the task needs to be appended with in the runtime section. These are set to `False` by default. Tasks with a specified `slurm` dictionary (rather than set to null, as by default) will use their contents to build the `directives` section. For the task specification above for `EvaObservations`, the runtime section will be renderend as the following:

```
[[EvaObservations-geos_marine]]
    script = "swell task EvaObservations $config -d $datetime -m geos_marine"
    platform = nccs_discover_sles15
    execution time limit = PT30M
    [[[directives]]]
        --job-name = EvaObservations-geos_marine
        --qos = allnccs
        --nodes = 1
        --ntasks-per-node = 64
        --constraint = mil
        --no-requeue =
        --account = <account>
```

This can be used to set task-specific defaults in `task_attributes.py`, rather than being set in `slurm.py`. For example, the task below defaults to slurm setting `--nodes=1`.

```python
class RunJediConvertStateSoca2ciceExecutable(Task):
    def set_attributes(self):
        self.is_cycling = True
        self.is_model = True 
        self.time_limit = True
        self.slurm = {'nodes': 1}
```

This supports setting platform-specific overrides, for example:

```python
class RunJediConvertStateSoca2ciceExecutable(Task):
    def set_attributes(self):
        self.is_cycling = True
        self.is_model = True 
        self.time_limit = True
        self.slurm = {'all': 1,
                      'nccs_discover_cascade': 2}
```

On the `nccs_discover_cascade` platform, `nodes` will be set as 2, but on any other platform it will be 1. User overrides will still work as they did previously.
