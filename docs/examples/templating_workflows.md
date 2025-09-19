# Templating cylc workflows within swell
The `flow.cylc` file informs the `Cylc` workflow engine on how to run an experiment. This includes the order in which tasks should be run, and the scripts and environment variables necessary for each task. Templating a workflow within Swell previously used `jinja2` templating on a file named `flow.cylc` under each suite. This has been replaced with an approach that uses a python class to manipulate strings to generated the `flow.cylc` used in the experiment. This allows for more complex logic to be performed in generating the workflow, but also may be confusing to users. This documentation serves to explain the new method of templating workflows under these changes.

## Cylc sections

The `flow.cylc` that is generated under this method is not much different from the one generated before, and users shouldn't notice a difference when it comes to creating an experiment, using overrides, etc. When creating an experiment, `swell` consults a file `src/swell/suites/<suite>/workflow.py` on how to construct the suite. This file should be an extension of the `CylcWorkflow` class (defined in `src/swell/utilities/cylc_workflow.py`). The method `get_workflow_str` is called to return a string which fills the contents of the `flow.cylc` file. Overriding this method can be used to manually specify the contents of the file, but the intended method of using this class is to override methods which comprise the individual sections of the file. Since every suite within Swell contains roughly the same sections, some of which share the same content, it is only necessary to override a few of the methods, most notably the graph section.

```python
def define_graph_section(self):
    # Define the string of the graph section
    graph_str = ''

    # Define the string for the R1 (first non-cycling) section
    r1 = r1_template

    for model_component in self.experiment_dict['model_components']:
        r1 += r1_model.format(model_component=model_component)

    # Format the R1 cycle and add it to the graph
    graph_str += self.format_cycle('R1', r1)

    # Format the string for each cycle
    for model_component in self.experiment_dict['model_components']:
        if 'cycle_times' in self.experiment_dict['models'][model_component]:
            for cycle_time in self.experiment_dict['models'][model_component]['cycle_times']:
                cycle_str = cycle_template.format(model_component=model_component)

                # Add the cycle string to the graph string
                graph_str += self.format_cycle(cycle_time, cycle_str)

    # Create the graph section
    graph_section = self.create_new_section('graph', graph_str)

    return graph_section
```

The `define_graph_section` task is used to set the graph. There are a few built-in methods used to format the strings into cylc syntax. The `format_cycle` method is used to construct properly indented blocks for cycling intervals. `create_new_section` creates a section object that tracks indentation levels, and can be added to other sections, with properly handled indentation and spacing. Here the `graph` is constructed as one of the sections, since it itself is a sub-member of the `scheduling` block in a cylc graph. Any suite questions in the config can be referenced from `self.experiment_dict`. For example, this is often used to format the model component.

## Tasks and the runtime section

Swell will parse the graph section, which is constructed first, to obtain the tasks which are used by the experiment. It will then build the runtime section by consulting `src/swell/tasks/task_runtimes.py`. Since swell tasks broadly fall into only a few categories (model-dependent or independent, cycling or non-cycling) that do not differ much between suites, they are easily abstracted into a `Task` class.

```python
@dataclass
class CloneJedi(Task):
    pass

@dataclass
class CloneGeosMksi(Task):
    is_model: bool = True

@dataclass
class EvaJediLog(Task):
    is_cycling: bool = True
    is_model: bool = True

@dataclass
class EvaObservations(Task):
    time_limit: bool = True
    is_cycling: bool = True
    is_model: bool = True
    slurm: dict = mutable_field({})

```

Here, the tags `is_cycling` and `is_model` are used to specify what tags the task needs to be appended with in the runtime section. These are set to `False` by default. Tasks with a specified `slurm` dictionary (rather than set to null, as by default) will use their contents to build the `directives` section.

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

This can be used to set task-specific defaults in `task_runtimes.py`, rather than being set in `slurm.py`:

```python
@dataclass
class RunJediConvertStateSoca2ciceExecutable(Task):
    is_cycling: bool = True
    is_model: bool = True
    time_limit: bool = True
    slurm: dict = mutable_field({'nodes': 1})
```

This supports setting platform-specific overrides, for example:

```python
@dataclass
class RunJediConvertStateSoca2ciceExecutable(Task):
    is_cycling: bool = True
    is_model: bool = True
    time_limit: bool = True
    slurm: dict = mutable_field({'nodes': {'all': 1,
                                           'nccs_discover_cascade': 2}})
```

On the `nccs_discover_cascade` platform, `nodes` will be set as 2, but on any other platform it will be 1. User overrides will still work as they did previously.
