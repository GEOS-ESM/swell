# Monitoring, Restarting, and Stopping an Experiment

The `swell launch` step prints out instructions to start the Cylc TUI, which shows the status of each task.
Tasks are color-coded by state; for example, running tasks are blue and completed tasks are green.

## When a task fails

When a task fails it will show as red in the TUI. In TUI, you can go over the failed task with arrow keys on your keyboard, press enter and trigger the task.

Alternatively, it is possible to navigate to the log files and locate them manually. Lets say the experiment ID is `swell-hofx` and the `Stage` task has failed during the `2020-12-15T00:00:00Z` cycle on the users second attempt to run `swell_launch_experiment` and `cylc`'s first run of the particular task. The logs for this task would be located at:

```
cd $HOME/cylc-run/swell-hofx-suite/run2/log/job/20201215T0000Z/Stage/01/
```

In this directory, `job.err` and `job.out` contain details about the failure. After correcting the
cause, use the Cylc TUI to trigger the failed task again. Cylc retains the workflow state and
continues with downstream tasks after their dependencies succeed.

## Restarting or resuming a workflow

Leaving the TUI does not stop the workflow. Reopen it with the `cylc tui` command printed by
`swell launch`.

If a workflow was stopped, its completed-task state remains in the Cylc run directory. Resume that
same Cylc run rather than calling `swell launch` again, which can create a new numbered run.
Review that task's logs and outputs, correct the underlying problem, and then use Cylc to
resume or trigger the appropriate task.

## Stopping jobs

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

After the workflow finishes—or when diagnosing a failed task—continue to
[Logs and Output Products](logs_and_output_products.md).
