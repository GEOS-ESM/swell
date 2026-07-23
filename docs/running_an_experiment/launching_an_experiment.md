# Launching an experiment

After running `swell create` the output will provide the directive needed to launch the experiment. It is typically something along the lines of:

```bash
swell launch --suite_path <experiment_root>/<experiment_id>/<experiment_id>-suite
```

The above script will install the workflow with `cylc`, start the workflow running and start the `cylc`-provided Terminal User Interface (TUI) that will allow you to monitor the progress of the tasks.


### Stopping jobs

Once the workflow is installed and running it can be stopped with:

```bash
cylc stop swell-hofx-suite/runX
```

Where X is replaced with the run you wish to stop. Alternatively you can issue without `/runX` to stop all runs of that experiment.

The above command will stop after currently active tasks have finished. Alternatively you could issue

```bash
cylc stop --kill swell-hofx-suite
```

to stop all runs of the swell-hofx-suite experiment after killing current active tasks.

See `cylc stop --help` for the full list of options.
