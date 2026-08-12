# QuickStart

This walks through creating, launching, and monitoring a small example experiment, assuming Swell and Cylc are already installed (see [Prerequisites](prerequisites.md)).

## 1. Verify Your Setup

```bash
swell --help
cylc --version
```

Both commands should return without error. If they don't, revisit [Installing Swell](../installation_and_setup/installing_swell.md) and [Configuring Cylc](../installation_and_setup/configuring_cylc.md).

## 2. Create an Experiment

Create an experiment from one of the maintained 3DVar suites, using its tier-1 test defaults. Pick the one matching the model you want to try:

| Model | Suite name | Command |
|---|---|---|
| Ocean/marine | `3dvar_marine` | `swell create 3dvar_marine` |
| Atmosphere | `3dvar_atmos` | `swell create 3dvar_atmos` |
| Atmospheric Composition | `3dvar_cf` | `swell create 3dvar_cf` |

For example:

```bash
swell create 3dvar_marine
```

This registers the experiment in R2D2 and creates a directory (default `/discover/nobackup/$USER/SwellExperiments/<suite>-suite`) containing `experiment.yaml` and a generated `flow.cylc`. See [Creating an Experiment](../running_an_experiment/creating_an_experiment.md) for options like overrides and platform selection.

### Useful Options

| Option | Applies to | Purpose |
|---|---|---|
| `-o`, `--override <file.yaml>` | `swell create` | Override any `experiment.yaml` value, e.g. `experiment_root` (the run directory) or `experiment_id`. |
| `-p`, `--platform <platform>` | `swell create` | Select platform-specific defaults (e.g. `nccs_discover_sles15`). |
| `-s`, `--slurm <file.yaml>` | `swell create` | Override SLURM directives (account, nodes, qos, etc.), globally or per task/model. See [SLURM Configuration](../configuration_reference/slurm_configuration.md). |
| `-k`, `--skip-r2d2` | `swell create` | Skip registering the experiment and storing products in R2D2. |
| `-l`, `--log_path <dir>` | `swell launch` | Directory to receive workflow manager (Cylc) logging output, instead of the default `$HOME/cylc-run/<suite_name>`. |

Run `swell create --help` or `swell launch --help` for the full, up-to-date list.

## 3. Launch It

`swell create` prints the exact command to run next, typically:

```bash
swell launch --suite_path <experiment_root>/<experiment_id>/<experiment_id>-suite
```

This instanciates the workflow with `cylc`, runs it, and opens the Cylc Terminal User Interface (TUI). See [Launching an Experiment](../running_an_experiment/launching_an_experiment.md).


## 4. Monitor It

In the TUI, tasks turn blue while running and green when complete. A task that fails turns red. You can select a failed task in the TUI and open its logs directly with the keyboard (check the TUI's help footer for the exact key) instead of navigating the filesystem.

Alternatively, logs can be found under:

```
$HOME/cylc-run/<experiment_id>-suite/run1/log/job/<cycle_point>/<TaskName>/01/
```

Look at `job.out` and `job.err` in that directory for details. See [Monitoring an Experiment](../running_an_experiment/monitoring_an_experiment.md).

If the TUI gets closed you can reopen it by typing `cylc tui` in the terminal.

## 5. Verify the Result

Once all tasks complete (all green), the experiment directory will contain the generated files for each cycle. By default `skip_r2d2` is `false`, so outputs (backgrounds, analyses, diagnostics) will also be registered and stored in R2D2; set `skip_r2d2: true` in `experiment.yaml` (or pass `-k`/`--skip-r2d2` to `swell create`) if you want to skip that. From here, see [Choosing a Workflow](../running_an_experiment/choosing_a_workflow.md) to explore other suites.

