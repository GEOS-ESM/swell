# Creating an Experiment

After [choosing a workflow](choosing_a_workflow.md) and deciding how to
[configure it](understanding_configuration.md), create the experiment with:

```bash
swell create <suite> <options>
```

For example, the following command creates a `3dvar_marine` experiment using its default
configuration and the default platform:

```bash
swell create 3dvar_marine
```

Use `swell create --help` to see the available suites and command-line options. Common variations
include:

```bash
# Ask each configuration question interactively.
swell create 3dvar_marine -m cli

# Apply reproducible settings from an override file.
swell create 3dvar_marine -o override.yaml

# Select a platform explicitly.
swell create 3dvar_marine -p nccs_discover_sles15
```

Before creating an experiment, make sure Swell is installed, Cylc is configured, and R2D2
credentials are available when the workflow retrieves or stores R2D2 data. See
[Installing Swell](../installation_and_setup/installing_swell.md),
[Configuring Cylc](../installation_and_setup/configuring_cylc.md), and
[R2D2 Credentials](../configuration_reference/r2d2_v3_credentials.md).

## What `swell create` does

`swell create` prepares the files needed to run the selected suite. It:

- Resolves suite, model, platform, override, and command-line configuration values.
- Optionally assigns an `r2d2_experiment_id` and registers the experiment with R2D2.
- Creates `<experiment_root>/<experiment_id>/`.
- Writes the fully resolved configuration to `experiment.yaml`.
- Renders the scheduling information and Jinja templates into `flow.cylc`.
- Copies platform environment files, suite EVA templates when present, and Swell configuration
  files into the experiment directory.

Creation does not install or start the Cylc workflow. A successful command prints the suite path
to pass to `swell launch` later.

Before launching, review the [generated directory layout](experiment_directory.md), especially
`experiment.yaml` and the resolved experiment path.
