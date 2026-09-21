## Create a Swell 3dvar_cf experiment:

To create a `3dvar_cf` suite, run the following command:

```bash
swell create 3dvar_cf
```

This uses the suite's tier-1 test defaults for every key (including `experiment_root` and
`experiment_id`), and no override file is required to get a working experiment.

Any default key can be changed by supplying your own override YAML with the `-o`/`--override` option.
For example, to change where the experiment is created:

```bash
swell create 3dvar_cf -o override.yaml
```

Where `override.yaml` contains only the keys you want to change, e.g.:

```yaml
experiment_root: /path/to/your/experiments
experiment_id: 3dvar_cf_test
```

With this, the following experiment folder will be created:
`/path/to/your/experiments/3dvar_cf_test`

Before launching the experiment, let's take a look at the `experiment.yaml` experiment configuration.

## Inside `experiment.yaml`:

`3dvar_cf` is a non-cycling 3DVar suite for the GEOS-CF composition model. Its tier-1 test sets the
following keys (some abbreviated for clarity):

```yaml
# What is the time of the first cycle (middle of the window)?
start_cycle_point: '2023-08-05T18:00:00Z'

# What is the time of the final cycle (middle of the window)?
final_cycle_point: '2023-08-05T18:00:00Z'

# List of models in this experiment
model_components:
- geos_cf

# Do you want to use an existing JEDI build or create a new build?
jedi_build_method: use_existing

# Perform check for observations? Set to false for debugging purposes.
check_for_obs: false

# What is the path to the Swell Static files directory?
swell_static_files: /discover/nobackup/projects/gmao/geos_cf_dev/SwellStaticFiles

# Configurations for the model components.
models:

  # Configuration for the geos_cf model component.
  geos_cf:

    # What is the duration for the data assimilation window?
    window_length: PT6H

    # Do you want to use a 3D or 4D (including FGAT) window?
    window_type: 3D

    # What is the horizontal resolution for the forecast model and backgrounds?
    horizontal_resolution: c90

    # Number of grid points on the cubed-sphere face, in x and y.
    npx: 91
    npy: 91

    # Processor layout for the cubed-sphere face, in x and y.
    npx_proc: 2
    npy_proc: 2

    # What is the vertical resolution for the forecast model and background?
    vertical_resolution: 72

    # SABER background error central/outer blocks.
    saber_central_block: bump_nicas
    saber_outer_block: stddev_bkg_scaled

    # What are the analysis variables?
    analysis_variables:
    - volume_mixing_ratio_of_no2

    # What is the name of the experiment providing the backgrounds?
    background_experiment: swell_test

    # Which observations do you want to include?
    observations:
    - tempo_no2_tropo
    - tropomi_s5p_no2_tropo

    # Provide a list of patterns that you wish to remove from the cycle directory.
    clean_patterns:
    - '*.txt'
    - 'logfile.*.out'
```

If you would like to change any of these parameters, it is suggested to copy `experiment.yaml`
to `override.yaml`, make the desired configuration changes, then create the experiment again:

```bash
swell create 3dvar_cf -o override.yaml
```

However, as with other suites, most of these settings — especially the DA window and observation
list — are tied to how observation and background files are organized in R2D2, so changing them may
require ingesting matching data first (see [Storing Observations and Backgrounds in R2D2](../r2d2/r2d2_ingest.md)).

## Launch the experiment:

After the `create` step finishes, Swell will provide the command to launch the experiment, which will
depend on your `experiment_root` and `experiment_id`, and look something like:

```bash
swell launch /path/to/your/experiments/3dvar_cf_test/3dvar_cf_test-suite
```

Executing this command will launch the experiment and bring up the TUI.

## What runs

For each cycle and each `model_component` (only `geos_cf` in this suite), the following tasks run, after
`CloneJedi` and `BuildJedi`/`BuildJediByLinking` have completed:

- `GetBackground`: fetch the background valid for the window.
- `GetObservations`: fetch the observations for the window.
- `StageJediCycle`: stage cycle-dependent files.
- `RenderJediObservations`: render the JEDI observation configuration.
- `RunJediVariationalExecutable`: run the JEDI 3DVar executable.
- `EvaObservations`: generate observation-space diagnostic plots.
- `EvaJediLog`: generate JEDI log (cost function/iteration) diagnostic plots.
- `EvaIncrement`: generate analysis increment diagnostic plots.
- `SaveObsDiags` (unless `skip_r2d2` is `true`): store the observation diagnostics in R2D2.
- `CleanCycle`: remove large intermediate files matching `clean_patterns`.

For the exact task dependency graph, look at the `3dvar_cf` suite's workflow definition in the Swell
source code, and compare it with the generated `flow.cylc` written into your experiment directory
(`<experiment_root>/<experiment_id>/<experiment_id>-suite/flow.cylc`), which has all templating
resolved using your `experiment.yaml` values.

## After the run is complete

Under the cycle directory, `geos_cf/eva/` will contain the plots for each of the three diagnostic
configurations: `observations-geos_cf.yaml` (observation space), `jedi_log-geos_cf.yaml` (cost function
and iteration information from the JEDI log), and `increment-geos_cf.yaml` (analysis increment for the
configured `analysis_variables`).
