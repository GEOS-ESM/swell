# Manually running tasks

When developing Swell it may provide a faster development cycle to run the tasks manually rather than using Cylc.

1. The first step is ensure the full suite of modules that Swell tasks need is loaded. Navigate to the suite directory of the experiment and load the modules:

```bash
cd <experiment_root>/<experiment_id>/<experiment_id>-suite
source modules
```

Note that a `modules-csh` is also provided. Note that use of `csh` is not fully tested so it might be better to switch to bash when working with Swell.


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
