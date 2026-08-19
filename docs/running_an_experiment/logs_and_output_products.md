# Logs and Output Products

Swell experiments produce two broad categories of files: workflow-management logs written by Cylc
and output files and products written under the experiment directory. Check both when
verifying a run or investigating a failed task.

## Cylc task logs

Cylc records task submission and execution information in its run directory, normally under:

```text
$HOME/cylc-run/<workflow-name>/<run-name>/log/job/
```

Logs are organized by cycle, task, and submit attempt. The most frequently used files are:

- `job.out`, which contains standard output from the task.
- `job.err`, which contains standard error from the task.
- `job`, which records the generated job script and environment used for the submission.
- `job-activity.log`, which details slurm request details in case the request fails.

When a task fails, note its cycle, task name, and submit attempt in the Cylc TUI before opening the
corresponding log directory.

## Experiment and application output

Swell places model-dependent runtime files under:

```text
<experiment_root>/<experiment_id>/run/<cycle-time>/<model-component>/
```

Depending on the workflow, a cycle directory can contain:

- Generated JEDI application YAML, such as `jedi_<application>_config.yaml`.
- JEDI executable output, such as `jedi_<application>_log.log`.
- Staged background, observation, bias-correction, and restart files.
- Analysis, increment, HofX, forecast, or converted-observation products.
- EVA configuration, diagnostics, and plots under `eva/`.
- A `cycle_done_<timestamp>` marker after cycle cleanup completes.

File names and expected products vary by suite and model. Use the appropriate
[workflow guide](../practical_examples/README.md) to identify the scientific products expected from
a particular experiment.

Some workflows also store products in R2D2. In that case, the local cycle directory contains the
files used or generated during execution, while R2D2 provides the persistent experiment data
record. See [R2D2 Concepts](../introduction/r2d2_overview.md).

## Which log should I inspect?

| Problem | Start here |
| --- | --- |
| Cylc could not submit or start a task | The task's `job.err`, generated `job` script, and scheduler messages |
| A Swell Python task failed | The task's `job.out` and `job.err` |
| A JEDI executable failed | The task logs, then `jedi_<application>_log.log` in the cycle directory |
| A result is missing or scientifically unexpected | Generated JEDI YAML, application log, staged inputs, and the workflow guide |
| EVA failed or plots are missing | The EVA task logs and the cycle's `eva/` directory |

Developers who need to reproduce a task outside Cylc can continue to
[Manually Running Tasks](manually_running_tasks.md).
