# ingest_files.py - R2D2 v3 File Ingestion Standalone Script

## Overview

`ingest_files.py` is a command-line utility for batch ingesting data files to R2D2 v3. It automatically parses filenames, extracts metadata, and stores files with proper R2D2 indexing.

**Features**:
- ✅ Batch processing (can ingest entire directories)
- ✅ Metadata extraction from filenames
- ✅ Dry-run mode (test before actual ingestion)
- ✅ Duplicate file detection (tracks ingested files)
- ✅ Ingests observations, bias corrections, and backgrounds
- ✅ Error logging

---

## Quick Start
- [Installation](#installation)
- [Register Your Experiment](#register-your-experiment)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Examples](#examples)
- [More Usage](#more-usage)

---

## Installation

### Prerequisites

**Quick Setup** (Recommended - Use This!):

Use the provided setup scripts:

```bash
# Load R2D2 client module
source load_r2d2.sh

# For production R2D2:
# Edit prod_setup_env.sh with your credentials, then:
source prod_setup_env.sh
```

**Manual Setup** (Alternative):

1. **Load R2D2 Client Module**:
   ```bash
   mod_swell
   module use -a /discover/nobackup/projects/gmao/advda/JediOpt/modulefiles/core
   module load r2d2-client/sles15_0604
   ```

2. **R2D2 Credentials**: Ensure `~/.swell/r2d2_credentials.yaml` exists with:
   ```yaml
   compute_host: "discover-gmao-intel"
   storage_host: "discover"
   user: "your_username"
   api_version: "v3"
   url: "https://r2d2-api.jcsda.org"
   ```

   Or set environment variables:
   ```bash
   export R2D2_USER=your_username
   export R2D2_API_KEY=your_api_key
   export R2D2_HOST=discover-gmao
   export R2D2_COMPILER=intel
   ```

3. **Python 3.7+** with `r2d2` package

### Script Location

All scripts are in the same directory:

```bash
/swell/src/swell/utilities/scripts/
├── ingest_files.py          # This script
├── load_r2d2.sh            # Load R2D2 module
├── prod_setup_env.sh       # Production environment setup
└── README_INGEST_FILES.md  # This documentation
```

**Usage**:
```bash
# From the scripts directory:
cd /path/to/swell/src/swell/utilities/scripts/

# Setup environment
source load_r2d2.sh

# Run the script
python ingest_files.py /path/to/files/ bias_correction --ingest
```

---

## Register Your Experiment

**Before ingesting files**, you must register your experiment in R2D2 v3.

### Quick Registration Script

```python
import r2d2
import os

# Set your details
experiment_name = 'my-experiment'  # Change this
user = os.environ.get('R2D2_USER', 'your_username')
host = os.environ.get('R2D2_HOST', 'discover-gmao')
compiler = os.environ.get('R2D2_COMPILER', 'intel')

# Register experiment
r2d2.R2D2Client.register_experiment(
    name=experiment_name,
    compute_host=f'{host}-{compiler}',
    user=user,
    lifetime='science'  # Options: debug, science, publication, release
)

print(f"Registered experiment: {experiment_name}")
```

### Lifetime Options

| Lifetime | Duration | Use Case |
|----------|----------|----------|
| `debug` | Days/weeks | Testing, development |
| `science` | Months | Research experiments |
| `publication` | Years | Published results |
| `release` | Permanent | Operational/reference data |

### Check if Experiment Exists

```python
import r2d2
import os

user = os.environ.get('R2D2_USER')
results = r2d2.R2D2Client.search_experiment(user=user)

for exp in results:
    print(f"{exp['name']}: {exp['lifetime']}")
```

### Update Experiment Lifetime

```python
import r2d2

r2d2.R2D2Client.update_experiment(
    name='my-experiment',
    key='lifetime',
    value='publication'  # Change to new lifetime
)
```

---

## Quick Start

### Step 0: Setup Environment

```bash
# First, set up R2D2 environment
source load_r2d2.sh

# Or for production with credentials:
# Edit prod_setup_env.sh first, then:
source prod_setup_env.sh
```

### 1. Dry Run (Test Mode)
```bash
# Test without actually ingesting
python ingest_files.py /path/to/files/ bias_correction
```

### 2. Actual Ingestion
```bash
# Actually ingest files to R2D2
python ingest_files.py /path/to/files/ bias_correction --ingest
```

### 3. Single File
```bash
# Ingest one specific file
python ingest_files.py /path/to/file.acftbias bias_correction --ingest
```

---

## Usage

### Basic Syntax

```bash
python ingest_files.py <path> <item_type> [--ingest]
```

### Arguments

| Argument | Required | Description | Values |
|----------|----------|-------------|--------|
| `path` | Yes | File or directory path | File path or directory |
| `item_type` | Yes | Type of data | `observation`, `bias_correction`, `background`, `forecast` |
| `--ingest` | No | Actually ingest (omit for dry run) | Flag |

### Item Types

| Item Type | R2D2 Item | Description |
|-----------|-----------|-------------|
| `observation` | `observation` | IODA observation files |
| `bias_correction` | `bias_correction` | Bias correction coefficients/errors |
| `background` | `forecast` | Model backgrounds |
| `forecast` | `forecast` | Model forecasts |

---

## Supported File Types

### Observations (`.nc4`, `.nc`)

**Extensions**: `.nc4`, `.nc`

**R2D2 Parameters**:
- `item`: `'observation'`
- `provider`: Auto-detected from path or filename
- `observation_type`: Extracted from filename
- `file_extension`: `'nc4'` or `'nc'`
- `window_start`: Extracted from filename timestamp
- `window_length`: `'PT6H'` (default)

**Example Filename**:
```
gdas.aircraft_temperature.2023-10-09T15:00:00Z.nc4
```

---

### Bias Corrections (`.acftbias`, `.satbias`, `.tlapse`, `*_cov`)

**Extensions**: `.acftbias`, `.acftbias_cov`, `.satbias`, `.satbias_cov`, `.tlapse`

**R2D2 Parameters**:
- `item`: `'bias_correction'`
- `model`: `'geos'` (default)
- `experiment`: Extracted from filename
- `provider`: Extracted from filename
- `observation_type`: Extracted from filename
- `file_extension`: Actual file extension
- `file_type`: Mapped from extension to R2D2 enum
- `date`: Extracted from filename timestamp

**Extension → file_type Mapping**:
```python
'acftbias'      → 'obsbias_coefficients'
'acftbias_cov'  → 'obsbias_coeff_errors'
'satbias'       → 'satbias'
'satbias_cov'   → 'obsbias_coeff_errors'
'tlapse'        → 'obsbias_tlapse'
```

**Example Filenames**:
```
gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias_cov
gsi.x0050.bc.amsua_n19.2023-10-09T15:00:00Z.satbias
gsi.x0050.bc.amsua_n19.2023-10-09T15:00:00Z.satbias_cov
gsi.x0050.bc.amsua_n19.2023-10-09T15:00:00Z.tlapse
```

---

### Backgrounds/Forecasts (`.nc4`, `.nc`, `.res`)

**Extensions**: `.nc4`, `.nc`, `.res`

**R2D2 Parameters**:
- `item`: `'forecast'`
- `model`: Auto-detected (default: `'geos'`)
- `experiment`: Hardcoded or extracted
- `resolution`: Hardcoded or extracted
- `file_type`: `'bkg'` or `'fc'`
- `file_extension`: Actual extension
- `date`: Extracted from filename
- `step`: Forecast length

**Example Filenames**:
```
geos.C180.x0050.bkg.20231009_12z.nc4
mom6.72x36.s2s.MOM.res.20231009.nc
```

---

## Filename Requirements

### General Format

All filenames must be **dot-separated** with at least **4 parts**:

```
part1.part2.part3.part4.extension
```

### Bias Correction Format (Required)

```
{provider}.{experiment}.bc.{observation_type}.{timestamp}.{extension}

Example:
gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
│   │     │  │                     │                       │
│   │     │  │                     │                       └─ Extension
│   │     │  │                     └─ ISO 8601 timestamp
│   │     │  └─ Observation type
│   │     └─ "bc" indicator (bias correction)
│   └─ Experiment ID
└─ Provider
```

**Requirements**:
- Minimum **6 parts** (provider, experiment, bc, obs_type, timestamp, extension)
- Timestamp must be **ISO 8601** format: `YYYY-MM-DDTHH:MM:SSZ`
- Extension must match one of: `acftbias`, `acftbias_cov`, `satbias`, `satbias_cov`, `tlapse`

### Observation Format

```
{provider}.{observation_type}.{timestamp}.{extension}

Example:
gdas.aircraft_temperature.2023-10-09T15:00:00Z.nc4
```

### Background/Forecast Format

```
{model}.{resolution}.{experiment}.{file_type}.{date}.{extension}

Example:
geos.C180.x0050.bkg.20231009_12z.nc4
```

---

## Examples

### Example 1: Ingest All Bias Corrections for an Experiment

**Scenario**: You have a directory with all bias correction files for experiment `x0050`

**Directory Structure**:
```
/discover/.../gsi/bc/x0050/2023-10-09/
├── gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
├── gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias_cov
├── gsi.x0050.bc.amsua_n19.2023-10-09T15:00:00Z.satbias
├── gsi.x0050.bc.amsua_n19.2023-10-09T15:00:00Z.satbias_cov
└── gsi.x0050.bc.amsua_n19.2023-10-09T15:00:00Z.tlapse
```

**Step 1: Dry Run**
```bash
python ingest_files.py \
    /discover/nobackup/projects/gmao/advda/R2D2DataStore/Shared/gsi/bc/x0050/2023-10-09/ \
    bias_correction
```

**Expected Output**:
```
DRY RUN bias_correction files from: /discover/.../2023-10-09/
Found 5 files

gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
   BIAS CORRECTION:
      provider=gsi, experiment=x0050
      model=geos, obs_type=aircraft_temperature
      file_extension=acftbias, file_type=obsbias_coefficients
      date=2023-10-09T15:00:00Z
   DRY RUN

[... similar for other 4 files ...]

Successfully processed 5/5 files

This was a DRY RUN. Use --ingest to actually ingest files
```

**Step 2: Actual Ingestion**
```bash
python ingest_files.py \
    /discover/nobackup/projects/gmao/advda/R2D2DataStore/Shared/gsi/bc/x0050/2023-10-09/ \
    bias_correction \
    --ingest
```

**Expected Output**:
```
INGESTING bias_correction files from: /discover/.../2023-10-09/
Found 5 files

gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
   BIAS CORRECTION:
      provider=gsi, experiment=x0050
      model=geos, obs_type=aircraft_temperature
      file_extension=acftbias, file_type=obsbias_coefficients
      date=2023-10-09T15:00:00Z
   SUCCESS

[... similar for other 4 files ...]

Successfully processed 5/5 files
```

---

### Example 2: Ingest Single Bias Correction File

```bash
python ingest_files.py \
    /path/to/gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias \
    bias_correction \
    --ingest
```

---

### Example 3: Ingest Observations for a Month

**Directory Structure**:
```
/obs/aircraft/2023-10/
├── gdas.aircraft_temperature.2023-10-01T00:00:00Z.nc4
├── gdas.aircraft_temperature.2023-10-01T06:00:00Z.nc4
├── ...
└── gdas.aircraft_temperature.2023-10-31T18:00:00Z.nc4
```

**Command**:
```bash
python ingest_files.py \
    /obs/aircraft/2023-10/ \
    observation \
    --ingest
```

---

### Example 4: Batch Ingest Multiple Dates

```bash
# Script to ingest bias corrections for multiple dates

DATES=("2023-10-09" "2023-10-10" "2023-10-11")
BASE_PATH="/discover/nobackup/projects/gmao/advda/R2D2DataStore/Shared/gsi/bc/x0050"

for date in "${DATES[@]}"; do
    echo "Processing $date..."
    python ingest_files.py \
        "${BASE_PATH}/${date}/" \
        bias_correction \
        --ingest
done
```

---

## Output Interpretation

### Success Output

```
gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
   BIAS CORRECTION:
      provider=gsi, experiment=x0050
      model=geos, obs_type=aircraft_temperature
      file_extension=acftbias, file_type=obsbias_coefficients
      date=2023-10-09T15:00:00Z
   SUCCESS
```

**Meaning**: File successfully ingested to R2D2

---

### Error Output

```
gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
   BIAS CORRECTION:
      provider=gsi, experiment=x0050
      model=geos, obs_type=aircraft_temperature
      file_extension=acftbias, file_type=obsbias_coefficients
      date=2023-10-09T15:00:00Z
   ERROR: R2D2Client.store_bias_correction() got an unexpected keyword argument 'window_start'
```

**Meaning**: Ingestion failed - check error message for details

---

### Skipped Output

```
**** gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias - already ingested
```

**Meaning**: File was previously ingested (tracked in `ingested_files.txt`)

---

### Summary Output

```
Successfully processed 143/144 files
Skipped 1 files (already ingested or invalid format)
```

**Meaning**: 
- 143 files ingested successfully
- 1 file skipped (already ingested or invalid)

---

### Failed Files Output

```
Failed to ingest 1 file(s):
   gsi.x0050.bc.bad_filename.acftbias: Ingestion failed
```

**Meaning**: Lists all files that failed with reasons

---

## Troubleshooting

### Issue 1: "Failed to import r2d2"

**Error**:
```
ImportError: Failed to import r2d2
Load module: module load r2d2-client/sles15_0604
```

**Solution**:
```bash
module load r2d2-client/sles15_0604
```

---

### Issue 2: "File doesn't have a valid extension"

**Error**:
```
File /path/to/file.txt doesn't have a valid extension for bias_correction
Valid extensions: .acftbias, .satbias, .tlapse, .acftbias_cov, .satbias_cov
```

**Solution**: Ensure file has correct extension for the item type

---

### Issue 3: "Not enough parts"

**Error**:
```
Skip filename.nc4 - not enough parts
```

**Solution**: Filename must have at least 4 dot-separated parts

**Bad**: `file.nc4` (2 parts)
**Good**: `provider.obs_type.timestamp.nc4` (4 parts)

---

### Issue 4: "400 Client Error: BAD REQUEST"

**Error**:
```
ERROR: 400 Client Error: BAD REQUEST for url: https://r2d2-api.jcsda.org:443/...
Content info: "Record does not exist in MySQL Database..."
```

**Possible Causes**:
1. **Invalid `file_type`**: Using extension instead of R2D2 enum
   - Bad: `file_type='acftbias'`
   - Good: `file_type='obsbias_coefficients'`

2. **Experiment not registered**: Register experiment first
   ```python
   r2d2.register(
       item='experiment',
       name='x0050',
       compute_host='discover-gmao-intel',
       user='your_username',
       lifetime='science'
   )
   ```

3. **Model not registered**: Contact R2D2 admins

**Solution**: Check the script's `file_ext_to_type` mapping is correct

---

### Issue 5: "Permission denied"

**Error**:
```
ERROR: Permission denied for data_store 'r2d2-experiments-nccs-gmao'
```

**Solution**: Check your R2D2 credentials and permissions with R2D2 admin

---

### Issue 6: Can't Find Failed File (143/144 success)

**Solution**: Look for files without "SUCCESS" in output:

```bash
# If you saved output to file
grep -B 10 "ERROR" output.log

# Or look for files without SUCCESS
grep "BIAS CORRECTION:" output.log -A 1 | grep -v "SUCCESS"
```

The failed file will be the one with an ERROR message or missing SUCCESS.

---

## More Usage

### Tracking Ingested Files

The script maintains an `ingested_files.txt` file in the current directory:

```bash
# View ingested files
cat ingested_files.txt

# Clear ingestion history (re-ingest everything)
rm ingested_files.txt
```

---

### Custom Provider Detection

Edit the `guess_provider_from_path()` function:

```python
def guess_provider_from_path(file_path):
    path_lower = file_path.lower()
    if 'ncdiag' in path_lower:
        return 'ncdiag'
    elif 'my_custom_provider' in path_lower:
        return 'my_provider'
    # Add more...
    else:
        return 'unknown'
```

---

### Custom Model Detection

Edit the `register_bias_correction()` function:

```python
# Around line 190-200
path_lower = file_path.lower()
if 'gfs' in path_lower:
    model = 'gfs'
elif 'fv3' in path_lower:
    model = 'fv3'
else:
    model = 'geos'  # default
```

---

## Best Practices

### 1. Always Dry Run First
```bash
# Test first
python ingest_files.py /path/to/files/ bias_correction

# Then ingest
python ingest_files.py /path/to/files/ bias_correction --ingest
```

### 2. Process by Date/Experiment
```bash
# Good: Process one date at a time
python ingest_files.py /path/to/bc/x0050/2023-10-09/ bias_correction --ingest

# Avoid: Processing entire experiment at once (harder to debug)
python ingest_files.py /path/to/bc/x0050/ bias_correction --ingest
```

### 3. Verify in R2D2
```python
# After ingestion, verify with R2D2 search
import r2d2

results = r2d2.search(
    item='bias_correction',
    model='geos',
    experiment='x0050',
    observation_type='aircraft_temperature',
    date='2023-10-09T15:00:00Z'
)

print(f"Found {len(results)} files")
```

---

## File Organization

### Directory Structure

```
R2D2DataStore/
├── Shared/
│   ├── gsi/
│   │   └── bc/
│   │       ├── x0050/
│   │       │   ├── 2023-10-09/
│   │       │   │   ├── *.acftbias
│   │       │   │   ├── *.acftbias_cov
│   │       │   │   ├── *.satbias
│   │       │   │   ├── *.satbias_cov
│   │       │   │   └── *.tlapse
│   │       │   └── 2023-10-10/
│   │       └── x0051/
│   └── obs/
│       ├── aircraft/
│       │   └── 2023-10/
│       │       └── *.nc4
│       └── satellite/
└── Experiments/
    └── [auto-managed by R2D2]
```

---

## Some Limitations

1. **Hardcoded values**: Some parameters (model, resolution) are hardcoded
2. **Limited validation**: Minimal validation of file contents
3. **Filename dependency**: Relies heavily on filename format

---

## Future Enhancements

Planned improvements:
- [ ] Create a Swell suite for file ingestion.
