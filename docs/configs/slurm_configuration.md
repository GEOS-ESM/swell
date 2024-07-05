# SLURM configuration for SWELL

Many SWELL tasks are submitted using the SLURM scheduler.
These tasks have some default SLURM directives that are stored within the SLURM source code (`src/swell/utilities/slurm.py`).
However, in many cases, users may want to override the defaults with their own directives, or add additional options.
There are two ways to do this:

The first is via the `$HOME/.swell/swell-slurm.yaml` file, which provides a single set of global overrides.
The syntax of this file is unnested YAML that directly maps SLURM directives (e.g., `account`, `nodes`) to their values, as follows:

```yaml
account: x1234
nodes: 1
qos: allqueues
```

This corresponds to the command:

```sh
sbatch ... --account=x1234 --nodes=1 --qos=allqueues
```

All `sbatch` directives are supported (see [`man sbatch`](https://slurm.schedmd.com/sbatch.html)).
However, note that SWELL will only validate that a given directive exists; we do not validate data types, or do anything fancy with type conversion (e.g., concatenation of arrays).
If in doubt about types, use double quotes around values to force things to be strings.

The second is to use the `-s / --slurm <somefile>` argument to SWELL (e.g., `slurm create 3dvar -s myslurm.yaml`).
This works similarly to the above but provides much finer-grained control over the ways that directives set for different tasks, though at the cost of more verbose syntax:

```yaml
# Global user-specified default directives. These apply to all tasks and override
# *all* hard-coded values.
slurm_directives_global:
  account: x1234
  nodes: 1

# Task-specific directives. These always override the globals (above) and any
# hard-coded values.
slurm_directives_tasks:
  RunHofxExecutable:
    # For model-specific tasks, "all" applies to all models.
    all:
      nodes: 2
    # Overrides for specific models.
    geos_atmosphere:
      nodes: 4
  BuildJEDI:
    # The "all" group is always required, even for tasks that aren't model-specific
    all:
      nodes: 2
```

When SLURM directives conflict, the pattern of overrides generally proceeds such that user-specified targets override hard-coded targets and more specific targets override more general ones.
The full priority list is as follows (directives higher in this list override directives lower):

1. Task- and model-specific directives (`slurm_directives_tasks`) set via `--slurm <somefile.yaml>` (e.g., `RunHofxExecutable.geos_atmosphere` would have `--nodes=4`).
2. Task-specific (but model-agnostic) directives (`slurm_directives_tasks`) from `--slurm <somefile.yaml>` (e.g., `RunHofxExecutable.geos_ocean` and all other `RunHofxExecutable` tasks would have `--nodes=2`)
3. Global directives set from `--slurm <somefile.yaml>` (e.g., all tasks use account `x1234`; all tasks _except_ `RunHofxExecutable` and `BuildJEDI` use `--nodes=1`)
4. User-level global directives in `$HOME/.swell/swell-slurm.yaml`
5. Hard-coded platform specific directives (in SWELL source code `.../platforms/{platform_name}/slurm.yaml`)
6. Hard-coded task- and model-specific directives (in SWELL source code)
7. Hard-coded task-specific (but model-generic) directives (in SWELL source code)
8. Hard-coded global defaults (in SWELL source code)
