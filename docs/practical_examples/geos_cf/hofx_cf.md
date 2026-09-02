## Create a Swell hofx_cf experiment:

To create a `hofx_cf` suite, run the following command:

```bash
swell create hofx_cf
```

This uses the suite's tier-1 test defaults for every key (including `experiment_root` and
`experiment_id`), and no override file is required to get a working experiment.

Any default key can be changed by supplying your own override YAML with the `-o`/`--override` option.

```bash
swell create hofx_cf -o override.yaml
```

Where `override.yaml` contains only the keys you want to change, e.g.:

```yaml
experiment_root: /path/to/your/experiments
experiment_id: hofx_cf_test
```

With this, the following experiment folder will be created:
`/path/to/your/experiments/hofx_cf_test`

Before launching the experiment, let's take a look at the `experiment.yaml` experiment configuration.

## Inside `experiment.yaml`:

`hofx_cf` is a non-cycling H(x) suite: it computes model equivalents of observations (no analysis, no
increment) for a single 6-hourly window. Its tier-1 test sets the following base keys:

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
```

The suite also sets these `geos_cf`-specific defaults:

```yaml
models:
  geos_cf:
    window_type: 3D
    window_length: PT6H
```

The default 3D configuration uses a single background at the center of the window. To run H(x) over a
4D window, set `window_type` to `4D` in your override file:

```yaml
models:
  geos_cf:
    window_type: 4D
    window_length: PT6H
    background_frequency: PT3H
    jedi_forecast_model: pseudo_model
```

In 4D, the JEDI `PSEUDO` forecast model does not integrate GEOS-CF forward in time. Instead, it reads
the precomputed backgrounds staged throughout the window, with one background for each
`background_frequency` step. Adjust `window_length` and `background_frequency` together to match the
available background times.

Other values in the generated `models.geos_cf` section, such as resolution and observations, continue
to use the standard `geos_cf` question defaults. Inspect your generated `experiment.yaml` for the exact
values and use an `override.yaml` to change them.

If you would like to change any of these parameters, it is suggested to copy `experiment.yaml`
to `override.yaml`, make the desired configuration changes, then create the experiment again:

```bash
swell create hofx_cf -o override.yaml
```

## Launch the experiment:

After the `create` step finishes, Swell will provide the command to launch the experiment, which will
depend on your `experiment_root` and `experiment_id`, and look something like:

```bash
swell launch /path/to/your/experiments/hofx_cf_test/hofx_cf_test-suite
```

Executing this command will launch the experiment and bring up the TUI.

## What runs

For each cycle and each `model_component` (only `geos_cf` in this suite), the following tasks run, after
`CloneJedi` and `BuildJedi`/`BuildJediByLinking` have completed:

- `GetBackground`: fetch one background for a 3D window, or the sequence of precomputed backgrounds
  needed at each `background_frequency` step for a 4D window.
- `GetObservations`: fetch the observations for the window.
- `StageJediCycle`: stage cycle-dependent files.
- `RenderJediObservations`: render the JEDI observation configuration.
- `RunJediHofxExecutable`: run the JEDI H(x) executable.
- `EvaObservations`: generate observation-space diagnostic plots.
- `SaveObsDiags` (unless `skip_r2d2` is `true`): store the observation diagnostics in R2D2.
- `CleanCycle`: remove large intermediate files matching `clean_patterns`.

For the exact task dependency graph, look at the `hofx_cf` suite's workflow definition in the Swell
source code, and compare it with the generated `flow.cylc` written into your experiment directory
(`<experiment_root>/<experiment_id>/<experiment_id>-suite/flow.cylc`), which has all templating
resolved using your `experiment.yaml` values.

## After the run is complete

Under the cycle directory, `geos_cf/eva/` will contain the observation-space plots (driven by
`observations-geos_cf.yaml`) for each observation type configured. Since `hofx_cf` performs no
analysis, there is no `jedi_log` or `increment` diagnostic output, unlike the `3dvar_cf` suites.
