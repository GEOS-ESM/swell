# Modifying and experiment

You can run `swell_create_experiment` at any time and it will overwrite all the files within the
experiment directory. For demonstration purposes lets assume a user has successfully run a few cycles
and wants to run a few more. That user can modify the cycle points in the `experiment.yaml` and rerun
`swell_create_experiment`. It will update the suite files and allow the experiment to be launched
again. At that point the workflow manager will pick up the new cycle points and complete those runs.
