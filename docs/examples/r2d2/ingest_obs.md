# R2D2 Observation Ingestion Suite

This suite ingests observation files into R2D2.
There are two ingestion pipelines depending on where your data lives:

| Pipeline | When to use | Tasks run |
|----------|------------|-----------|
| **Direct copy** (`cp`) | IODA-formatted files already exist on Discover | `IngestObs` |
| **Download → Convert → Ingest** | Raw files (e.g. HDF5) need to be fetched from a remote server (NASA GES DISC, etc.) and converted to IODA format first | `DownloadObs → ConvertObsToIoda → IngestObs` |

---

## Pipeline 1: Direct Copy (files already on Discover)

Use this when IODA-formatted files are already available on the local filesystem.

### Step 1: Add your observation to the suite config

Edit `src/swell/suites/ingest_obs/suite_config.py` and update (or create) the appropriate
section. For example for marine observations, update `ingest_obs_marine`:

```python
qd.obs_to_ingest(['adt_cryosat2n', 'my_obs'])   # Add yours here
qd.start_cycle_point("2021-07-02T06:00:00Z")    # When to start
qd.final_cycle_point("2021-07-03T06:00:00Z")    # When to stop
```

### Step 2: Register your observation

Your observation needs an entry in `src/swell/configuration/observation_ioda_names.yaml` so the system knows the R2D2 metadata keys associated with the observations such as `provider` and `ioda_name`:

```yaml
ioda instrument names:
  - ioda name: ioda_name
    full name: "Observation Type/Name"
    inst type: inst_type
    provider: provider_name
```

Skip this step if your observation is already listed.

### Step 3: Create the ingest YAML

Create `src/swell/configuration/jedi/interfaces/<model>/ingest_observations/my_obs.yaml`:

```yaml
acquisition_method: 'cp'
cp_source: '/discover/nobackup/your/path/obs/YYYY/MM/obs_YYYYMMDDHH.nc'
```

Date placeholders in the path are replaced at runtime:

### Step 4: Create and run the experiment

```bash
swell create ingest_obs_marine
swell launch <experiment_path>
```

The workflow steps through each cycle time, finds your files, and stores them in R2D2.

---

## Pipeline 2: Download → Convert → Ingest

Use this pipeline when raw observation files (e.g. HDF5 granules from NASA GES DISC) need to be
downloaded from a remote HTTPS server and converted to IODA format before ingestion.
The `ingest_obs_cf` suite config uses this pipeline.

Enable the pipeline in `suite_config.py` with:

```python
qd.download_convert_pipeline(True)
```

With this flag set, each Cylc cycle runs three tasks in sequence:

```
DownloadObs → ConvertObsToIoda → IngestObs
```

### Step 1: Add your observation to the suite config

```python
qd.obs_to_download(['my_obs'])    # Used by DownloadObs and ConvertObsToIoda
qd.obs_to_ingest(['my_obs'])      # Used by IngestObs
qd.download_convert_pipeline(True)
qd.converter_path('/path/to/ioda-converter')  # Where ioda-converter scripts live
qd.start_cycle_point("2023-08-10T00:00:00Z")
qd.final_cycle_point("2023-08-11T00:00:00Z")
```

`converter_path` is optional, if omitted, the task looks in
`<experiment>/jedi_bundle/build/bin/`.

### Step 2: Register your observation

Same as the direct-copy pipeline, add an entry to `observation_ioda_names.yaml`.

### Step 3: Create the download YAML

Create `src/swell/configuration/jedi/interfaces/<model>/download_observations/my_obs.yaml`:

```yaml
remote_host: https://snpp-omps.gesdisc.eosdis.nasa.gov
remote_path_template: /data/SNPP_OMPS_Level2/OMPS_NPP_NMTO3_L2.2/YYYY/JJJ/
filename_pattern: OMPS-NPP_NMTO3-L2_v2.1_YYYYmMMDDtHH*.h5
auth_type: earthdata_token

# How far before window_begin to extend the file search.
# Use this to capture orbit granules that started before the DA window
# but contain data within it. Set to the maximum granule/orbit duration.
max_orbit_duration: PT2H
```

Supported placeholders in `remote_path_template` and `filename_pattern`:
`YYYY`, `MM`, `DD`, `JJJ` (day-of-year), `HH`. Use `*` as a wildcard in
`filename_pattern` where the exact timestamp is not known in advance.

With `auth_type` set to `earthdata_token`, Authentication uses `~/.netrc` and no tokens are stored in the config.
Follow the instructions on the NASA Earthdata website [here](https://urs.earthdata.nasa.gov/documentation/for_users/data_access/create_net_rc_file) to create
an account and set up the authentication.

`DownloadObs` task places files in `<cycle_dir>/download/<obs_name>/`.

### Step 4: Create the converter YAML

Create `src/swell/configuration/jedi/interfaces/<model>/convert_observations/my_obs.yaml`:

```yaml
# Name of the ioda-converters Python script (must be in converter_path or jedi_bundle/build/bin/)
converter_script: my_obs_h52ioda.py

# Output filename template — must match `source` in the ingest YAML below
output_filename_template: "my_obs_%Y%m%d%H.nc"

# Any additional flags passed to the converter after -i <inputs> -o <output>
extra_flags:
  -q: 128
  -e: atbd
```

The converter is invoked as:

```
python3 <converter_path>/<converter_script> \
    -i <file1> <file2> ... \
    -o <cycle_dir>/ioda/<obs_name>/<output_filename> \
    [extra_flags]
```

Input files are discovered automatically from the download directory using the
`filename_pattern` in the download YAML.

### Step 5: Create the ingest YAML

Create `src/swell/configuration/jedi/interfaces/<model>/ingest_observations/my_obs.yaml`:

```yaml
acquisition_method: local
source: ioda/my_obs/my_obs_%Y%m%d%H.nc   # path relative to cycle_dir
```

`acquisition_method: local` tells `IngestObs` to look for the file in the cycle
directory (produced by `ConvertObsToIoda`) rather than copying from a static path.
The `source` template must match `output_filename_template` in the converter YAML.

### Step 6: Create and run the experiment

```bash
swell create ingest_obs_cf
swell launch <experiment_path>
```

---

## Editing configs in an existing experiment

When you run `swell create`, observation YAML files are copied from the swell source
tree into your experiment directory:

```
<experiment_path>/configuration/jedi/interfaces/<model>/
├── download_observations/
├── convert_observations/
└── ingest_observations/
```

The tasks read from **this experiment copy**, not the source code. You can edit these
files directly in your experiment directory without modifying swell or re-running
`swell create`. Changes take effect on the next task run.

---

## Pre-configured suites

### `ingest_obs_marine` — ADT observations on Discover

```bash
swell create ingest_obs_marine
swell launch <experiment_path>
```

Ingests `adt_cryosat2n` from July 2021 using the direct-copy pipeline. Runs in
dry-run mode by default.

Example ingest YAML (`adt_cryosat2n.yaml`):
```yaml
acquisition_method: 'cp'
cp_source: '/discover/nobackup/projects/gmao/soca/obs/ioda/ocean/adt_cryosat2n/YYYY/MM/ioda-obs-YYYYMMDDHH-adt_cryosat2n.nc'
```

### `ingest_obs_cf` — OMPS-NM ozone from NASA GES DISC

```bash
swell create ingest_obs_cf
swell launch <experiment_path>
```

Downloads OMPS-NM HDF5 granules from GES DISC, converts them to IODA format, and
ingests the result into R2D2. Uses the `DownloadObs → ConvertObsToIoda → IngestObs`
pipeline. Requires Earthdata credentials in `~/.netrc`.

Suite configuration:
```python
qd.download_convert_pipeline(True)
qd.obs_to_download(['omps_o3_nm_total'])
qd.obs_to_ingest(['omps_o3_nm_total'])
qd.converter_path('/path/to/jedi-bundle/build/bin/')
qd.window_length("PT6H")
qd.dry_run(False)
```

If you are developing a new built-in observation configuration, update
`suite_config.py` and the source configuration files below. If you are running
from an installed/static Swell environment, prefer an override YAML or edit the
copied configuration in your experiment directory after `swell create`.

---

## Suite configuration reference

| Key | Used by | Description |
|-----|---------|-------------|
| `start_cycle_point` | Cylc | First cycle to process (ISO-8601) |
| `final_cycle_point` | Cylc | Last cycle to process (ISO-8601) |
| `cycle_times` | Cylc | Hours of day to process (e.g. `['T00','T06','T12','T18']`) |
| `obs_to_ingest` | `IngestObs` | List of observation names to ingest into R2D2 |
| `obs_to_download` | `DownloadObs`, `ConvertObsToIoda` | List of obs names to download and convert |
| `download_convert_pipeline` | `flow.cylc` | `True` enables the Download→Convert→Ingest pipeline |
| `converter_path` | `ConvertObsToIoda` | Directory containing ioda-converter scripts |
| `window_length` | `DownloadObs` | DA window length as ISO-8601 duration (e.g. `"PT6H"`) |
| `dry_run` | All tasks | `True` = log only, no files downloaded/stored |

---

## How it works

### Direct-copy pipeline

For each cycle, `IngestObs`:
1. Reads `obs_to_ingest` from `experiment.yaml`
2. Loads each obs's YAML from the experiment directory
3. Replaces date placeholders to build the source file path
4. Calls `r2d2.store()` with the file and its metadata (provider, obs type, window, extension)

### Download → Convert → Ingest pipeline

For each cycle:

1. **`DownloadObs`** reads `obs_to_download`, then for each obs:
   - Reads `download_observations/<obs_name>.yaml`
   - Extends the DA window backwards by `max_orbit_duration` to avoid missing partial orbits
   - Walks through each hour slot, lists the remote directory, and downloads matching files to `<cycle_dir>/download/<obs_name>/`

2. **`ConvertObsToIoda`** reads `obs_to_download`, then for each obs:
   - Reads `convert_observations/<obs_name>.yaml`
   - Collects all files from `<cycle_dir>/download/<obs_name>/`
   - Runs the ioda-converter Python script in a single call: `-i <all files> -o <cycle_dir>/ioda/<obs_name>/<output>`

3. **`IngestObs`** reads `obs_to_ingest` with `acquisition_method: local`:
   - Looks for the converted file in `<cycle_dir>/ioda/<obs_name>/`
   - Calls `r2d2.store()` to ingest it

---

## Dry run mode

All tasks respect `dry_run: True`. The suite logs what it would do — listing remote
directories, building converter commands, resolving file paths — without downloading,
converting, or writing to R2D2. Set `dry_run: False` in the suite config when you are
ready for real ingestion.

---

## Troubleshooting

**"File not found"** — For `cp` method: check that your `cp_source` path pattern is
correct and that files exist for your date range. For `local` method: check that
`ConvertObsToIoda` ran successfully and that the `source` path in the ingest YAML
matches the `output_filename_template` in the converter YAML.

**"No provider found for observation X"** — Add an entry for your observation in
`observation_ioda_names.yaml`.

**"Converter script not found"** — Check that `converter_path` (or
`jedi_bundle/build/bin/`) contains the script named in
`convert_observations/<obs_name>.yaml`.

**Download failures (401/403)** — Ensure your Earthdata credentials are in `~/.netrc`
in the format:
```
machine urs.earthdata.nasa.gov login <username> password <password>
```
