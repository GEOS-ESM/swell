# SLURM configuration

Swell uses SLURM to submit many workflow tasks on supported HPC platforms. SLURM
settings can come from four places:

1. Platform defaults distributed with Swell.
2. Built-in defaults for individual tasks and models.
3. User-wide defaults in `~/.swell/swell-slurm.yaml`.
4. Experiment and task overrides supplied when an experiment is created.

Settings from the more specific sources override settings from the more general
sources. See [Configuration precedence](#configuration-precedence) for the full
order.

## User-wide defaults

Use `~/.swell/swell-slurm.yaml` for directives that should apply to all of your
Swell experiments. The file contains a flat mapping of `sbatch` directive names
to values:

```yaml
account: x1234
partition: compute
qos: normal
no-requeue: ''
```

Do not include the leading `--` used on the `sbatch` command line. For example,
write `account`, not `--account`. Set a directive that takes no argument, such
as `--no-requeue`, to an empty string. This is how Cylc represents a
[flag-style directive](https://cylc.github.io/cylc-doc/stable/html/user-guide/task-implementation/job-submission.html#directives-section-quirks-pbs-sge).

Platform-specific defaults are stored in
`src/swell/deployment/platforms/<platform>/slurm.yaml`. For example, the NCCS
Discover Cascade and SLES15 configurations set the appropriate `constraint`
value. The user-wide file overrides these platform defaults without requiring
you to modify files distributed with Swell.

Swell validates directive names against its supported `sbatch` options, but it
does not validate every value. Quote a value when YAML could interpret it as a
different type; for example, use `time: '01:30:00'`.

## Experiment and task overrides

To customize one experiment, create a YAML file and pass it to `swell create`
with `-s` or `--slurm`:

```shell
swell create 3dvar_marine --slurm myslurm.yaml
```

The file can define directives for the whole experiment and overrides for
individual tasks:

```yaml
slurm_directives_global:
  account: x1234
  nodes: 1

slurm_directives_tasks:
  RunJediHofxExecutable:
    all:
      nodes: 2
    geos_atmosphere:
      nodes: 4

  BuildJedi:
    all:
      nodes: 2
```

Entries under `slurm_directives_global` apply to every SLURM task in the
experiment. Under `slurm_directives_tasks`, task names are case-sensitive and
must match a task that Swell configures for SLURM; an unknown task name causes
experiment creation to fail.

Within a task, `all` applies to every model. A model-specific mapping, such as
`geos_atmosphere` above, overrides `all` for that model. Model-agnostic tasks,
such as `BuildJedi`, normally need only an `all` mapping.

A task can also set `execution_time_limit` using an ISO 8601 duration. This
controls how long Cylc waits for the job, independently of SLURM's `time`
directive:

```yaml
slurm_directives_tasks:
  RunJediHofxExecutable:
    execution_time_limit: PT2H
    all:
      time: '01:30:00'
```

## Configuration precedence

For a model-specific task, Swell uses the first applicable value in this list
when the same directive is defined in more than one place:

1. The task-and-model mapping in the file passed with `--slurm`.
2. The task's `all` mapping in the file passed with `--slurm`.
3. `slurm_directives_global` in the file passed with `--slurm`.
4. User-wide defaults in `~/.swell/swell-slurm.yaml`.
5. Swell's built-in defaults for that task and model.
6. Swell's built-in defaults for that task across all models.
7. Platform defaults in `src/swell/deployment/platforms/<platform>/slurm.yaml`.

For a model-agnostic task, which uses the task's `all` mapping, the order is:

1. The task's `all` mapping in the file passed with `--slurm`.
2. Swell's built-in `all` mapping for that task.
3. `slurm_directives_global` in the file passed with `--slurm`.
4. User-wide defaults in `~/.swell/swell-slurm.yaml`.
5. Platform defaults in `src/swell/deployment/platforms/<platform>/slurm.yaml`.

This means a global override does not replace a built-in task default for a
model-agnostic task. Put the override in that task's `all` mapping instead.
Directives not set at a higher level are inherited from the levels below it.

For the complete set of SLURM directives and their accepted values, see the
[SLURM `sbatch` documentation](https://slurm.schedmd.com/sbatch.html).
