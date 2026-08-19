# Manually Running Tasks

Manually running a task is an advanced development and debugging technique. For normal execution
and recovery, use Cylc so that task dependencies and state are managed by the workflow.

1. The first step is ensure the full suite of modules that Swell tasks need is loaded. Navigate to the suite directory of the experiment and load the modules:

```bash
cd <experiment_root>/<experiment_id>/<experiment_id>-suite
source modules
```

Note that a `modules-csh` is also provided.


2. Set the configuration and datetime environment variables:

```bash
config=experiment.yaml
datetime=<yyyymmddhh>
```

3. Open the `flow.cylc` file and copy the command for running the task you want to run. Then paste it, e.g.:

```bash
swell task <task> $config -d $datetime -m <model>
```

Each task has dependencies, i.e. tasks that should have already run. If running manually it would be important to ensure that these dependencies ran successfully. In practice you may want to use Cylc to run the workflow and then stop when it's running the task you wish to rerun manually. This will ensure that everything else ran accordingly.

If a manual run does not behave as expected, use the application and task logs described in
[Logs and Output Products](logs_and_output_products.md).
