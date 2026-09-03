# Launching an Experiment

After reviewing the [generated experiment directory](experiment_directory.md), launch the workflow
by passing its suite directory to `swell launch`:

```bash
swell launch <experiment_root>/<experiment_id>/<experiment_id>-suite
```

The command installs the generated workflow in Cylc, starts it, and opens the Cylc Terminal User
Interface (TUI). The TUI shows the cycles and task states as the workflow progresses. Leaving the
TUI does not by itself stop the workflow.

## Running in the foreground

By default, Cylc detaches from the terminal and runs the workflow in the background. Use `-b` or
`--no-detach` to keep the workflow attached to the terminal:

```bash
swell launch --no-detach <experiment_root>/<experiment_id>/<experiment_id>-suite
```

In this mode, the command occupies the terminal until the workflow finishes and returns the
workflow's exit status. Swell does not open the Cylc TUI automatically. This option is useful for
automated scripts and debugging; omit it for the usual interactive workflow-monitoring experience.

Continue to [Monitoring, Restarting, and Stopping](monitoring_an_experiment.md) for routine workflow
control.
