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

Swell has a variety of tasks, many of which are shared across suites. Tasks in Swell are defined as classes which extend the `taskBase` parent class, which has many helpful functions and attributes. When a task is run by swell, it calls the `execute` function.

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

In order to know which questions to associate with which tasks, it is necessary to update `src/swell/tasks/task_questions.py` with all task questions used by the task. This tells Swell to ask the question during suite creation, and makes the parameter available to be used in the tasks `self.config` object. Suite questions are accessible to all tasks, so long as they have entries in `experiment.yaml`. For more information, see [Adding questions](adding_tasks.md)

`task_questions.py`:
```
CloneGeosMksi = QuestionList(
    list_name="CloneGeosMksi",
    questions=[
        qd.observing_system_records_mksi_path(),
        qd.observing_system_records_mksi_path_tag()
    ]
)
```

Tasks that have a slurm requirement need to be specified in `src/swell/utilities/slurm.py`.

For debugging purposes, it may be easier to first create and test some tasks outside of Swell, and then port them to Swell by changing relevant variables and path specifications. Alternatively, `experiment.yaml` can be populated manually and tested using `swell task <task> experiment.yaml`.