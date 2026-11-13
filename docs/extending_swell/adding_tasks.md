# Adding tasks

## How tasks are called

In Swell parlance, a `task` is a small step in the process of running a workflow, and range from very simple to complex scripts.

Tasks are called from the command line using `swell task <task_name> <config_file>`, with additional parameters including `-m`, for model_component, `-d`, for cycle point, `-p`, for ensemble packet (relevant for ensemble experiments), and `-a`, which is a contextual parameter used by some tasks for different purposes.

Tasks are located under the source location `src/swell/tasks`. As different model components may have different requirements for the same task, it is sometimes necessary to have *model-specific* versions of tasks. These are selected by swell when the model component is specified on the command line:

```text
src/swell/
|-- tasks/
|   |-- geos_marine/
|   |   |__ get_ensemble.py
|   |__ get_ensemble_geos_marine.py
```

For example, if `swell task GetEnsemble -m geos_atmosphere ...`, is run, the file `get_ensemble.py` would be used (Note the camel to snake-case conversion). If `swell task GetEnsemble -m geos_marine ...` is run, `get_ensemble_geos_marine.py` would be used.

## Writing a task

Swell has a variety of tasks, many of which are shared across suites. Tasks in Swell are defined as classes which extend the `taskBase` parent class, which has many helpful functions and attributes. When a task is run by swell, it calls the `execute` function. Information on how to run the task and the parameters the task needs are specified in the `TaskSetup` class.

Calls to parameters are made using either functions of `taskBase`, for more common parameters, or using `self.config.<parameter>`.

### Example Swell Task
```python
class CloneGeosMksi(taskBase):

    def execute(self) -> None:

        """
        Generate the satellite channel record from GEOSmksi files
        """

        # This task should only execute for geos_atmosphere
        # -------------------------------------------------
        if self.get_model() != 'geos_atmosphere':
            self.logger.info('Skipping GenerateObservingSystemRecords for: ' + self.get_model())
            return

        # Parse config
        # ------------
        path_to_geos_mksi = self.config.observing_system_records_mksi_path()
        tag = self.config.observing_system_records_mksi_path_tag()
```
This example shows the basics of writing a task, including task definition and the execute function. The current model is accessed by the `self.get_model()` function, inherited from `taskBase`. The variables `path_to_geos_mksi`, and `tag`, are pulled from the experiment configuration, which is sourced from the `experiment.yaml`.

The `TaskSetup` class informs swell how to construct the task's cylc parameters, as well as the questions that are used by the task. The `TaskSetup` class for `CloneGeosMksi` looks like the following:

```python

task_name = 'CloneGeosMksi'
@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.model_dep = True
        self.questions = [
            qd.observing_system_records_mksi_path(),
            qd.observing_system_records_mksi_path_tag()
        ]

```

The `set_attributes` abstract method is used to set values for the class. The `self.questions` list sets needed question parameters for the config. Slurm requirements are also set in the the `TaskSetup`. For more information, see documentation in `src/swell/tasks/base/task_setup.py`.

For debugging purposes, it may be easier to first create and test some tasks outside of Swell, and then port them to Swell by changing relevant variables and path specifications. Alternatively, `experiment.yaml` can be populated manually and tested using `swell task <task> experiment.yaml`.
