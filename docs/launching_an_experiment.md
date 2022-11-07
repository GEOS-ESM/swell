# Launching an experiment

After running `swell_create_experiment` the output will provide the directive needed to launch the experiment. It is typically something along the lines of:

```
swell_launch_experiment --suite_path $NOBACKUP/SwellExperiments/swell-hofx/swell-hofx-suite
```

where `swell-hofx` is the name of the experiment that is set in the configuration file.

The above script will install the workflow with `cylc`, start the workflow running and start the `cylc`-provided Terminal User Interface (TUI) that will allow you to monitor the progress of the tasks.


### Stopping jobs

Once the workflow is installed and running it can be stopped with:

```
cylc stop swell-hofx-suite/runX
```

Where X is replaced with the run you wish to stop. Alternatively you can issue without `/runX` to stop all runs of that experiment.

The above command will stop after currently active tasks have finished. Alternatively you could issue

```
cylc stop --kill swell-hofx-suite
```

to stop all runs of the swell-hofx-suite experiment after killing current active tasks.

See `cylc stop --help` for the full list of options.
