# `forecast_coupled_ensemble_geos` Suite

## Overview

The `forecast_coupled_ensemble_geos` suite runs N coupled GEOSgcm ensemble members concurrently. It is designed for use as the forecast step in ensemble DA contexts. Each member receives stochastic physics perturbations (SPPT) and a unique member identifier (MEMID), and optionally stochastic ocean perturbations via a `MOM_stoch` file.

---

## Directory Layout

After the first cycle, the experiment's `GEOSgcm/` directory contains:

```
GEOSgcm/
├── forecast/        (deterministic staging area — used only for initial restarts)
├── mem001/
│   ├── AGCM.rc      (with SPPT:1, MEMID:1 appended)
│   ├── MOM_override (with MOM_stoch content prepended, if present)
│   ├── gcm_run.j    (EXPDIR/HOMDIR pointing to this directory)
│   ├── RESTART/
│   └── scratch/     (written by model at run time)
├── mem002/
...
└── memNNN/
```

The number of members is set by `ensemble_num_members` (default 20) in `experiment.yaml`.

---

## Workflow Graph

```
R1:
  CloneGeos
  CloneGeos => BuildGeosByLinking?
  BuildGeosByLinking:fail? => BuildGeos
  GetCoupledGeosRestart => PrepCoupledEnsembleGeosRunDir
  BuildGeosByLinking? | BuildGeos => PrepCoupledEnsembleGeosRunDir

Cycling:
  PrepCoupledEnsembleGeosRunDir => RunGeosEns_001 & RunGeosEns_002 & ... & RunGeosEns_NNN
  RunGeosEns_001 & ... & RunGeosEns_NNN => MoveEnsembleForecastRestarts
  MoveEnsembleForecastRestarts[-<forecast_duration>] => PrepCoupledEnsembleGeosRunDir
```

Each `RunGeosEns_NNN` is a distinct Cylc task, so member failures are retried independently.

---

## Key Tasks

> **See also**: [Coupled Marine GEOS Cycling](coupled_marine_geos_runs.md) for a full description
> of `GetCoupledGeosRestart` (initial restart sources and directory structure setup), which
> behaves identically in this suite.

### `PrepCoupledEnsembleGeosRunDir`

Runs once per cycle, before the ensemble members execute. Iterates over members 1..N and
calls `_prep_member` for each.

#### Timing Calculation

The forecast start time is computed as:

```
fc_dto = cycle_time − (3/4 × forecast_duration)
```

This is the same formula used by the deterministic `PrepCoupledGeosRunDir`. Example: with
`cycle_time = 2021-07-01T12Z` and `forecast_duration = P1D`, the forecast starts at
`2021-06-30T18Z`.

#### Static Files Copied into Each Member Directory

**Required** (from `geos_homdir`):

| File | Purpose |
|---|---|
| `AGCM.rc` | Atmosphere model configuration |
| `CAP.rc` | Coupled model controller |
| `gcm_run.j` | Job submission script |
| `HISTORY.rc` | History output configuration |
| `fvcore_layout.rc` | FV3 core layout |
| `input.nml` | Namelist inputs |
| `ice_in` | CICE6 configuration |
| `MOM_input` | MOM6 main configuration |
| `MOM_override` | MOM6 parameter overrides |
| `diag_table` | Diagnostic output table |
| `data_table` | Data input table |
| `fvcore_layout.rc`, `gcm_emip.setup`, `logging.yaml`, `__init__.py` | Supporting files |

**Optional** (copied only if present in `geos_homdir`):
- `MOM_oda_incupd` — MOM6 IAU configuration
- `MOM_saltrestore` — MOM6 salt restoring

**From `geos_expdir`**: `RC/` directory, `linkbcs`.

`GEOSgcm.x` is **not** copied into member directories — the ensemble shares the binary from the
build path (`existing_geos_gcm_build_path`).

#### First-Cycle Restart Seeding

**First cycle**: if no `*_rst` files are present in the member directory, all `*_rst` files and
the `RESTART/` contents are copied from `GEOSgcm/forecast/` (populated by `GetCoupledGeosRestart`)
to seed initial conditions. Every member starts from the same restarts; perturbations come solely
from the stochastic flags.

**Subsequent cycles**: restarts are already in place from `MoveEnsembleForecastRestarts`; the copy
step is skipped.

#### `gcm_run.j` Path Rewrite

`EXPDIR` and `HOMDIR` entries in `gcm_run.j` are rewritten to point to the member directory:

```python
if re.match(r'^\s*setenv\s+EXPDIR\b', line):
    f.write(f'setenv EXPDIR {ens_dir}\n')
elif re.match(r'^\s*setenv\s+HOMDIR\b', line):
    f.write(f'setenv HOMDIR {ens_dir}\n')
```

#### `CAP.rc` Modification

Updated for each member:

```
NUM_SGMT: 1
JOB_SGMT: 0000<days> HHMMSS   # derived from forecast_duration
END_DATE: 50010101 000000      # far future — prevents premature termination
```

#### `cap_restart` File

Written to each member directory as `YYYYMMDD HHMMSS` using `fc_dto`.

#### `input.nml` Warm Start

`process_nml()` switches `input.nml` from cold-start mode (`n`) to warm-restart mode (`r`) to
prevent the model from bootstrapping from scratch.

#### `AGCM.rc` RECORD_* Timing

If `RECORD_FREQUENCY` is present in the source `AGCM.rc`, the task rewrites the timing entries
so checkpoints align with DA window boundaries:

```
RECORD_FREQUENCY: <time_string>
RECORD_REF_DATE:  <DA window begin date>
RECORD_REF_TIME:  <DA window begin time>
```

where DA window begin = `fc_dto + forecast_duration / 2`.

Stochastic perturbation flags are appended **after** the RECORD_* update:

```
SPPT: 1           # Stochastically Perturbed Parameterization Tendencies
SKEB: 0           # Stochastic Kinetic Energy Backscatter (disabled by default)
STOCH_shutoff: 0
MEMID: <N>        # Member index (1-based)
```

#### MOM6 IAU (per member)

If `mom6_iau: true` in the `geos_marine` model config and a `RESTART/mom6_increment.nc` file
exists in the member directory, `MOM_input` is augmented with `MOM_oda_incupd` and
`ODA_INCUPD_NHOURS` is set from `mom6_iau_nhours`. This runs independently for each member,
so only members that have an increment file receive the IAU augmentation.

#### Ocean Stochastic Perturbations (`MOM_override`)

If `<geos_homdir>/MOM_stoch` exists, its content is prepended to each member's `MOM_override`.
No additional configuration is needed; the presence of the file is the activation signal.

#### Note: Background Frequency Not Processed

Unlike the deterministic `PrepCoupledGeosRunDir`, this task does **not** call `process_icein` or
`process_diag_table`. `ice_in` and `diag_table` are copied verbatim from `geos_homdir`. Set
background output frequency directly in those files before starting the suite.

---

### `MoveEnsembleForecastRestarts`

Runs after all members complete, preparing restarts for the next cycle. Iterates over members
1..N.

#### Atmosphere Restarts

Globs `scratch/*_checkpoint` (plain filenames only — no timestamp support) and moves each file to
the member root, stripping any extension suffix. `Geos.rename_checkpoints()` then renames
`*_checkpoint` → `*_rst` in place:

```
scratch/fvcore_internal_checkpoint  →  fvcore_internal_rst
scratch/moist_internal_checkpoint   →  moist_internal_rst
```

#### Marine Restarts

```
scratch/tile.bin             →  tile.bin
scratch/RESTART/iced.nc      →  RESTART/iced.nc
scratch/RESTART/MOM.res*nc   →  RESTART/<original filename>
```

MOM.res filenames are preserved as written by the model (no timestamp stripping or renaming).

#### Differences from the Deterministic `MoveDaRestart`

| Feature | `MoveEnsembleForecastRestarts` | `MoveDaRestart` |
|---|---|---|
| Time-stamped checkpoints | Not supported — only `*_checkpoint` | Supported |
| `.rcx` history restart files | Not moved | Moved |
| MOM.res timestamp stripping | Not applied | Applied (→ `MOM.res.nc`, `MOM.res_1.nc`, …) |
| MOM6 IAU increment | Not moved | Moved |

---

## Configuration

`experiment.yaml` keys specific to this suite:

| Key | Default | Description |
|---|---|---|
| `ensemble_num_members` | `20` | Number of ensemble members |
| `forecast_duration` | `P1D` | Forecast length (ISO 8601 duration); also sets the inter-cycle dependency offset |

All other keys follow the same pattern as `forecast_coupled_geos`.

---

## SLURM Directives

All `RunGeosEns_NNN` tasks share a single SLURM configuration key. Override resources in `experiment.yaml` or a SLURM override file under `slurm_directives_tasks`:

```yaml
slurm_directives_tasks:
  RunGeosEns:
    all:
      nodes: 6
      ntasks-per-node: 128
```

The default execution time limit is `PT30M`.

---

## Prototype Limitations

- All ensemble members are seeded from the same `forecast/` restarts on the first cycle (no initial perturbations beyond the stochastic flags).
- `SKEB` (stochastic kinetic energy backscatter) is disabled by default.
- Time-stamped checkpoint restarts (`*_checkpoint.YYYYMMDD_HHMMz.nc4`) are not supported; members must write plain `*_checkpoint` files (do not set `RECORD_FREQUENCY` without also verifying checkpoint naming).
- History restart (`.rcx`) files are not moved between cycles.
- MOM.res files retain their model-generated filenames; the timestamp-stripping rename applied by the deterministic `MoveDaRestart` is not performed.
- `ice_in` and `diag_table` are not adjusted for `background_frequency`; configure background output frequency directly in `geos_homdir`.
- The suite does not yet include an ensemble mean/spread diagnostic task or coupling back to a DA suite.
