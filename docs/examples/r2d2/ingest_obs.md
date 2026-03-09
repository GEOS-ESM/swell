# R2D2 Observation Ingestion Suite

This suite ingests observation files into R2D2 so they can be used in experiments. You tell it where your files are and what date range you want, and it handles the rest.

## I Have Observation Files - How Do I Ingest Them?

Let's say you have ocean observation files on Discover that you want to ingest into R2D2. Here's exactly what to do:

### Step 1: Add your observation to the suite config

Edit `src/swell/suites/ingest_obs/suite_config.py`. If you're ingesting marine observations, update the `ingest_obs_marine` section. If different (atmosphere, etc.), you can create a similar snippet like `ingest_obs_atmosphere` following the same pattern.

Add your observation name to the list and set the date range:

```python
qd.obs_to_ingest(['adt_cryosat2n', 'my_obs'])   # Add yours here
qd.start_cycle_point("2021-07-02T06:00:00Z")    # When to start
qd.final_cycle_point("2021-07-03T06:00:00Z")    # When to stop
```

### Step 2: Make sure your observation is registered

Your observation needs an entry in `observation_ioda_names.yaml` so the system knows which provider it comes from:

```yaml
ioda instrument names:
  - ioda name: ioda_name
    full name: "Observation Type/Name"
    provider: provider_name
```

If your observation is already in that file, you can skip this step.

### Step 3: Create a YAML file describing your observation

Create a file named after your observation (e.g., `my_obs.yaml`) in `src/swell/configuration/jedi/interfaces/<model>/ingest_observations/` (`geos_marine` for marine obs):
```yaml
retrieval_method: 'cp'
cp_source: '/discover/nobackup/your/path/.../obs/YYYY/MM/obs_YYYYMMDDHH.nc'
```

The path uses placeholders that get replaced with actual dates at runtime:
- `YYYY` → 2021
- `MM` → 07
- `DD` → 02
- `HH` → 06
- `YYYYMMDDHH` → 2021070206

So `/path/YYYY/MM/obs-YYYYMMDDHH.nc` becomes `/path/2021/07/obs-2021070206.nc` for the July 2, 2021 06Z cycle.

### Step 4: Create and run the experiment

```bash
# Create the experiment (this copies everything to your experiment directory)
swell create ingest_obs_marine

# Launch it
swell launch <experiment_path>
```

That's it. The workflow runs through each cycle time (00Z, 06Z, 12Z, 18Z by default), finds your files, and ingests them to R2D2.

# Extra

If you just want to ingest marine observations that are already set up, it's even simpler.
When you run `swell create`, the observation YAML files from the source code are copied into your experiment directory under:

```
<experiment_path>/configuration/jedi/interfaces/<model>/ingest_observations/
```

For example, your experiment is at `/discover/nobackup/your_name/SwellExperiments/swell-ingest_obs/`:

```
swell-ingest_obs/configuration/jedi/interfaces/geos_marine/ingest_observations/
├── adt_cryosat2n.yaml
├── adt_sentinel6a.yaml
└── your_obs.yaml
```

The task reads from **this experiment copy**, not the swell source code. This means you can edit these files directly in your experiment directory to change file paths or other settings without modifying the source code or re-installing swell. Changes take effect on the next task run.

For example, to change the source path for an observation in an existing experiment:

```bash
# Edit the YAML in your experiment directory
vim swell-ingest_obs/configuration/jedi/interfaces/geos_marine/ingest_observations/adt_cryosat2n.yaml
```
## Using the Pre-configured Marine Obs Ingestion Suite

If you just want to ingest marine observations that are already set up:

```bash
swell create ingest_obs_marine
swell launch <experiment_path>
```

This uses the defaults in `suite_config.py` which are already configured for `adt_cryosat2n` observations from July 2021. The suite runs in **dry-run mode by default** so you can see what it would do without actually ingesting anything.

To actually ingest, change `dry_run` to `False` in the suite config before creating the experiment.


### Suite Configuration (`suite_config.py`)

These settings control what gets ingested:

```python
qd.start_cycle_point("2021-07-02T06:00:00Z")  # First cycle to process
qd.final_cycle_point("2021-07-03T06:00:00Z")  # Last cycle to process
qd.cycle_times(['T00', 'T06', 'T12', 'T18'])  # Which hours of the day
qd.obs_to_ingest(['adt_cryosat2n'])           # Which observations to ingest
qd.dry_run(True)                              # True = test/dry-run mode, False = actually ingest
```

### Observation YAML Files

Each observation type has its own YAML in your experiment's `configuration/jedi/interfaces/<model>/ingest_observations/` directory.

Example (`adt_cryosat2n.yaml`):
```yaml
retrieval_method: 'cp'
cp_source: '/discover/nobackup/projects/gmao/soca/obs/ioda/ocean/adt_cryosat2n/YYYY/MM/ioda-obs-YYYYMMDDHH-adt_cryosat2n.nc'
```

The `retrieval_method` is `'cp'` for files on the local filesystem (Discover). The `cp_source` is the path pattern with date placeholders.

## How It Works

When you launch the workflow, Cylc runs through each cycle point (e.g., 2021-07-02T06:00:00Z, 2021-07-02T12:00:00Z, ...) and for each one:

1. Reads the list of observations from `experiment.yaml`
2. For each observation, loads its YAML config from the experiment directory and looks up the provider
3. Builds the file path by replacing date placeholders with the actual cycle time
4. Calls `r2d2.store()` to ingest the file with the right metadata

The metadata stored in R2D2 includes the provider, observation type, window start/length, and file extension which is everything needed to fetch the data later.

## Dry Run Mode

By default, the suite runs in dry-run mode. This means it goes through all the steps but doesn't actually call R2D2.

This is useful to verify your paths are correct before doing real ingestion. When you're ready, set `dry_run` to `False` in the suite config.


```

## Problems that you might encounter

**"File not found"** - Check that your `cp_source` path pattern is correct and the files actually exist for your date range. Make sure the date placeholders match your file naming convention. You can edit the YAML directly in your experiment directory.

**"No provider found for observation X"** - Your observation isn't in `observation_ioda_names.yaml`. Add an entry with the provider name.


