# Monitoring an experiment

The `swell_launch_experiment` step will automatically start the `cylc` TUI, that lets you see the status of each task that is running. It uses a color coding to determine the status of each task. Once a task is running the color turns purple and once complete it turns green.

### When a task fails

When a task fails it will show as red in the TUI. A limitation of the TUI is that you cannot use it to navigate to the log files and have to locate them manually. `cylc` does have a web-based monitoring tool and we are investigating whether this can be used with `cylc`.

Lets say the experiment ID is `swell-hofx` and the `Stage` task has failed during the `2020-12-15T00:00:00Z` cycle on the users second attempt to run `swell_launch_experiment` and `cylc's` first run of the particular task. The logs for this task would be located at:

```
cd $HOME/cylc-run/swell-hofx-suite/run2/log/job/20201215T0000Z/Stage/01/
```

In this directory you will find `job.err` and `job.out` where you should be able to see details of the failure.
