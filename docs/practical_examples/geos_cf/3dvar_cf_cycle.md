## Create a Swell 3dvar_cf_cycle experiment:

To create a `3dvar_cf_cycle` suite, run the following command:

```bash
swell create 3dvar_cf_cycle
```

This uses the suite's tier-1 test defaults for every key (including `experiment_root` and
`experiment_id`), and no override file is required to get a working experiment.

Any default key can be changed by supplying your own override YAML with the `-o`/`--override` option.
For example, to change where the experiment is created:

```bash
swell create 3dvar_cf_cycle -o override.yaml
```

Where `override.yaml` contains only the keys you want to change, e.g.:

```yaml
experiment_root: /path/to/your/experiments
experiment_id: 3dvar_cf_cycle_test
```

With this, the following experiment folder will be created:
`/path/to/your/experiments/3dvar_cf_cycle_test`

Before launching the experiment, let's take a look at the `experiment.yaml` experiment configuration.

## Inside `experiment.yaml`:

`3dvar_cf_cycle` extends `3dvar_cf` (see [3DVAR GEOS-CF](3dvar_cf.md) for the shared analysis keys) into
a **cycling** workflow: each cycle's analysis is followed by a short forecast that produces the
background and restart files for the next cycle. Its tier-1 test sets:

```yaml
# What is the time of the first cycle (middle of the window)?
start_cycle_point: '2023-08-10T00:00:00Z'

# What is the time of the final cycle (middle of the window)?
final_cycle_point: '2023-08-10T06:00:00Z'

# List of models in this experiment
model_components:
- geos_cf

# Do you want to use an existing JEDI build or create a new build?
jedi_build_method: use_existing

# Perform check for observations? Set to false for debugging purposes.
check_for_obs: false
```

In addition to the analysis keys shared with `3dvar_cf` (window length, resolution, observations,
etc.), the `models.geos_cf` section adds keys needed to run and register the forecast that connects
consecutive cycles:

```yaml
models:
  geos_cf:
    # What is the name of the experiment providing the restarts?
    rst_experiment: swell_test

    # Which restart file types to fetch/save (achem_internal, fvcore_internal, gocart_internal, ...)
    rst_file_types:
    - achem_internal
    - fvcore_internal
    - gocart_internal
    - ...

    # Use the Incremental Analysis Update (IAU) procedure for the forecast?
    iau: true

    # How long should the forecast run for?
    forecast_length: PT12H

    # How often should the forecast write output?
    forecast_output_frequency: PT3H

    # Template increment file used to build the forecast's IAU input.
    inc_template: /path/to/increment_template.nc4

    # Paths to the GEOS-CF install and run directories used to prepare/run the forecast.
    geos_cf_install_dir: /path/to/GEOSgcm/install
    geos_cf_run_dir: /path/to/GEOSgcm/rundir

    # Path to the Swell Static files directory.
    swell_static_files: /discover/nobackup/projects/gmao/geos_cf_dev/SwellStaticFiles

    # Path to GEOS-FP files used by the forecast.
    geosfp_path: /path/to/geosfp
```

If you would like to change any of these parameters, it is suggested to copy `experiment.yaml`
to `override.yaml`, make the desired configuration changes, then create the experiment again:

```bash
swell create 3dvar_cf_cycle -o override.yaml
```

## Launch the experiment:

After the `create` step finishes, Swell will provide the command to launch the experiment, which will
depend on your `experiment_root` and `experiment_id`, and look something like:

```bash
swell launch /path/to/your/experiments/3dvar_cf_cycle_test/3dvar_cf_cycle_test-suite
```

Executing this command will launch the experiment and bring up the TUI.

## What runs

For each cycle and each `model_component` (only `geos_cf` in this suite), the following tasks run, after
`CloneJedi` and `BuildJedi`/`BuildJediByLinking` have completed. The analysis chain is the same as
`3dvar_cf`, followed by a forecast chain that produces the background and restarts for the next cycle:

- `GetBackground`: fetch the background valid for the window.
- `GetObservations`: fetch the observations for the window.
- `StageJediCycle`: stage cycle-dependent files.
- `RenderJediObservations`: render the JEDI observation configuration.
- `RunJediVariationalExecutable`: run the JEDI 3DVar executable.
- `EvaObservations`: generate observation-space diagnostic plots.
- `EvaJediLog`: generate JEDI log (cost function/iteration) diagnostic plots.
- `EvaIncrement`: generate analysis increment diagnostic plots.
- `SaveObsDiags` (unless `skip_r2d2` is `true`): store the observation diagnostics in R2D2.
- `PrepForecastCf`: update RC files and create the forecast scratch directory from the analysis.
- `GetRestartCf`: fetch the restart files (of the types in `rst_file_types`) from R2D2.
- `RunForecast`: run the GEOS-CF forecast for `forecast_length`, writing output every
  `forecast_output_frequency`.
- `SaveForecastCf`: save the forecast history output.
- `SaveRestartCf`: save the checkpoint restart files (valid at the start of the next window) to R2D2.
- `CleanCycle`: remove large intermediate files matching `clean_patterns`, once diagnostics, forecast,
  and restarts have all completed.

The next cycle's `GetBackground` only starts once the previous cycle's `CleanCycle` has completed,
which is what makes this suite cycle.

For the exact task dependency graph, look at the `3dvar_cf_cycle` suite's workflow definition in the
Swell source code, and compare it with the generated `flow.cylc` written into your experiment directory
(`<experiment_root>/<experiment_id>/<experiment_id>-suite/flow.cylc`), which has all templating
resolved using your `experiment.yaml` values.

## After the run is complete

Under each cycle directory, `geos_cf/eva/` contains the same three diagnostic plot sets as `3dvar_cf`
(`observations-geos_cf.yaml`, `jedi_log-geos_cf.yaml`, `increment-geos_cf.yaml`). The forecast run
directory additionally contains the GEOS-CF history and restart output produced by `RunForecast`,
which becomes the background and restart input for the next cycle.
