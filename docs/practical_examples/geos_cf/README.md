# GEOS-CF Composition Data Assimilation Workflows

Swell provides three suites for GEOS-CF (atmospheric composition) data assimilation, all based on the
JEDI `geos_cf` model interface:

- [HofX GEOS-CF](hofx_cf.md) — non-cycling observation operator only run (no analysis), useful for
  verifying that backgrounds, observations, and the JEDI interface are correctly staged.
- [3DVAR GEOS-CF](3dvar_cf.md) — a single non-cycling 3DVar analysis.
- [3DVAR GEOS-CF Cycle](3dvar_cf_cycle.md) — a cycling 3DVar, where each analysis is followed by a
  short GEOS-CF forecast that produces the background and restarts for the next cycle.

All three share the same `geos_cf` model configuration keys (window length, resolution, observations,
etc.); the cycling suite additionally configures the forecast and restart handling. See
[Storing Observations and Backgrounds in R2D2](../r2d2/r2d2_ingest.md) for how to ingest the
observations and backgrounds these suites consume.

