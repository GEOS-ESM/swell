## Introduction
In this section, some practical examples for different suites (workflows) will be presented.

It will be assumed that SWELL has already been installed and loaded as a module following the installation instructions. You can execute `swell --help` and `module list` to check if `swell` is loaded properly and commands work.

## Creating an Experiment Directory

There are common elements in these examples in terms of [creating](../creating_an_experiment.md) and [launching](../launching_an_experiment.md) experiments. We will take a closer look at the `experiment.yaml` that controls the different aspects of the JEDI configuration creations.


### Using Defaults:
To create a `3dvar` suite run the following command. This will use the default `3dvar-tier1` test configuration:

```bash
swell create 3dvar
```
This will create the experiment directory in the default `experiment_root` with the
default `experiment_id`, which are currently:

```yaml
experiment_root: /discover/nobackup/{$USER}/SwellExperiments
experiment_id: {suite_name}-suite
```

<details>
  <summary> <strong> Advanced Tip:</strong> </summary>

If you would like to create the experiment folder at a different location, you can use the override option (`-o` or `--override`):

```bash
swell create 3dvar -o override.yaml
```

The `override.yaml` should contain the following keys to override defaults:

```yaml

experiment_root: /discover/nobackup/{your_username}/different_folder
experiment_id: test001
```

</details>

### Using CLI (Questionary):

Alternatively, you can use the CLI option to create your experiment folder:

```bash
swell create 3dvar -m cli
```

This will walk you through different options depending on the suite type which is very similar
to `gcm_setup` method used within GEOSgcm.

Either method (defaults with override or CLI) will



## Experiment Directory:

Inside the experiment folder, there will be multiple folders and subfolders. After launching an experiment,
and as different tasks start running, there will be additional folders, however prior
to launching there will be

```bash
{experiment_id}/
├── configuration
└── {experiment_id}-suite/
    ├── eva/
    ├── experiment.yaml
    ├── flow.cylc
    ├── modules
    └── modules-csh
```
Let's breakdown these two folders here:

**configuration:** This copies model, observations, and satellite channel information from the
Swell source installation folder. Most users wouldn't change this unless some changes are required
for modifying the configurations and parametrizations in JEDI applications. Even then, it is suggested
to do these type of modifications by creating a seperate Swell branch and reinstalling Swell. Otherwise,
they will likely get overwritten.

**{experiment_id}-suite:**

Contains suite (or workflow) specific files.

`modules` and `modules-csh` are automatically generated and used by Cylc to load `spack-stack` modules,
additonal installations (such as R2D2/EVA), and `$PATH` dependencies.

`eva/`: contains batch processed EVA yamls that could be defined for each model. They are created at
each cycle and currently have three different options: increments (in Model space), observations (in IODA space),
and jedi_log, which is used to plot Cost functions by parsing JEDI log outputs.

`flow.cylc`: (Users don't need to modify this) This is the Cylc workflow file that desribes task inner and inter
dependencies. For each suite, this will have a different structure and different scripts/tasks within.

`experiment.yaml`: This is the key configuration file that dictates the inputs for contain configuration variables that will be used for different scripts in the workflow.

For each JEDI bundle type (i.e., fv3-jedi, soca) and suite (3dvar, hofx etc.) in this section, we will display the `experiment.yaml` and talk about details.