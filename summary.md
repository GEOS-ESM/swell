# Implementation Summary: `forecast_coupled_ensemble_geos` Suite

## Overview

A new prototype ensemble forecast suite was added to Swell for use in ensemble DA contexts. N GEOSgcm members run concurrently under `GEOSgcm/mem001/`, `GEOSgcm/mem002/`, ..., `GEOSgcm/memNNN/`, each with stochastic physics perturbations (SPPT/MEMID in `AGCM.rc`) and optional stochastic ocean perturbations via `MOM_stoch`.

---

## New Files

### `src/swell/tasks/prep_coupled_ensemble_geos_run_dir.py`

Task `PrepCoupledEnsembleGeosRunDir`. Runs once per cycle to create and populate all ensemble member directories.

- Reads `ensemble_num_members` from config.
- Loops over members 1..N; for each constructs `ens_dir = GEOSgcm/mem{m:03d}/`.
- Copies all static GEOS experiment files from `geos_homdir`/`geos_expdir` into `ens_dir/`.
- **First-cycle detection**: if no `*_rst` files are in `ens_dir/`, copies restarts from `GEOSgcm/forecast/` (populated by `GetCoupledGeosRestart`) to seed ICs for the first run.
- Rewrites `gcm_run.j` so `EXPDIR`/`HOMDIR` point to `ens_dir/`.
- Rewrites `CAP.rc` and optionally `AGCM.rc` (RECORD entries).
- **Stochastic AGCM flags**: appends `SPPT: 1`, `SKEB: 0`, `STOCH_shutoff: 0`, `MEMID: <N>` to each member's `AGCM.rc`.
- **MOM_stoch**: if `geos_homdir/MOM_stoch` exists, prepends its content to `ens_dir/MOM_override`.
- Writes `cap_restart` and calls `process_nml()` for `input.nml`.

### `src/swell/tasks/move_ensemble_forecast_restarts.py`

Task `MoveEnsembleForecastRestarts`. Mirrors `MoveForecastRestart` but loops over all N members.

- For each `mem{m:03d}/`: moves `scratch/*_checkpoint` → `*_rst`, renames checkpoints via `Geos.rename_checkpoints()`, and moves marine restarts (`tile.bin`, `iced.nc`, `MOM.res*.nc`).

### `src/swell/suites/forecast_coupled_ensemble_geos/suite_config.py`

Suite configuration including:
- Standard suite questions (cycle points, build method)
- `forecast_duration` (default `P1D`)
- `ensemble_num_members` (default 20, suite-level key — not under `models:`)

### `src/swell/suites/forecast_coupled_ensemble_geos/flow.cylc`

Jinja2 Cylc workflow. Key features:

- `{% set members = range(1, ensemble_num_members + 1) %}` — N is resolved at experiment creation time.
- Each member gets its own Cylc task `RunGeosEns_001` ... `RunGeosEns_NNN`, each independently retryable.
- `R1` graph: `GetCoupledGeosRestart => PrepCoupledEnsembleGeosRunDir` (also waits for build).
- Cycling graph: `PrepCoupledEnsembleGeosRunDir => [all members in parallel] => MoveEnsembleForecastRestarts`; inter-cycle dependency `MoveEnsembleForecastRestarts[-{{forecast_duration}}] => PrepCoupledEnsembleGeosRunDir`.
- SLURM directives for all `RunGeosEns_NNN` tasks drawn from `scheduling["RunGeosEns"]` (single shared key).

---

## Modified Files

### `src/swell/utilities/question_defaults.py`

Added `ensemble_num_members_suite` — a `SuiteQuestion` (integer, default 20, not model-scoped). This sits alongside the existing model-scoped `ensemble_num_members` used by DA suites.

### `src/swell/tasks/task_questions.py`

Registered question lists for both new tasks:
- `PrepCoupledEnsembleGeosRunDir`: static file questions + GEOS build/forecast questions + `ensemble_num_members_suite`
- `MoveEnsembleForecastRestarts`: `forecast_duration` + `ensemble_num_members_suite`

### `src/swell/utilities/slurm.py`

Added `'RunGeosEns'` to the `slurm_tasks` set so SLURM directive handling and the `slurm_directives_tasks` validation work for ensemble member jobs.

### `src/swell/deployment/create_experiment.py`

Three additions to `prepare_cylc_suite_jinja2`:

1. **Top-level fallback for `ensemble_num_members`**: checks `experiment_dict` directly before iterating model sub-dicts (required because this suite has no `model_components`).
2. **`forecast_duration` in render dict**: added so the Jinja2 inter-cycle offset expression `[-{{forecast_duration}}]` resolves correctly.
3. **`RunGeosEns` execution time limit**: `scheduling["RunGeosEns"]["execution_time_limit"] = 'PT30M'` (same default as `RunGeos`).

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| MOM_stoch application | Always prepend if file exists in homdir | No extra config flag needed; presence of file is the signal |
| SLURM config for ensemble members | Single shared `RunGeosEns` key | Simpler; all members have identical resource requirements |
| Initial restart source | Copy from `forecast/` to all `mem**/` | Reuses existing `GetCoupledGeosRestart` without changes |
| Per-member retry | One Cylc task per member | Each `RunGeosEns_NNN` is tracked independently; failure of member 5 retries only that member |
| `ensemble_num_members` scope | Top-level experiment key (not under `models:`) | Ensemble suite has no model sub-components |

---

## Verification Steps

```bash
# 1. Create experiment — confirms config renders correctly
swell create forecast_coupled_ensemble_geos

# 2. Validate Cylc graph syntax
cylc validate <exp_suite_path>

# 3. Dry-run prep task — confirms ens dirs created with correct AGCM.rc, gcm_run.j
swell task PrepCoupledEnsembleGeosRunDir <config.yaml> -d <datetime>

# 4. After a full cycle, verify restart movement
ls GEOSgcm/mem001/*_rst   # should exist after MoveEnsembleForecastRestarts
```
