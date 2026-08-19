# Launching an Experiment

After reviewing the [generated experiment directory](experiment_directory.md), launch the workflow
by passing its suite directory to `swell launch`:

```bash
swell launch <experiment_root>/<experiment_id>/<experiment_id>-suite
```

The command installs the generated workflow in Cylc, starts it, and opens the Cylc Terminal User
Interface (TUI). The TUI shows the cycles and task states as the workflow progresses. Leaving the
TUI does not by itself stop the workflow.

Continue to [Monitoring, Restarting, and Stopping](monitoring_an_experiment.md) for routine workflow
control.
