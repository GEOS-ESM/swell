# Choosing a Workflow

A good first step when using Swell is to select a suite. A suite defines a workflow that can stage
files, generate input YAML files, run tasks, process output, clean up, and prepare a later cycle.
Swell provides suites for analysis, observation evaluation, ingestion, conversion, and experiment
comparison. Run `swell create --help` to see the complete list of suite configurations. Below is the list of
analysis suites and non-analysis suites such as ingest or compare that are currently available in Swell.

## Analysis suites

| Suite | Model | Goal |
| --- | --- | --- |
| `hofx` | `geos_atmosphere` | Run HofX with FV3-JEDI when you need simulated observations, departures (O-B), or observation diagnostics without minimizing a data-assimilation cost function or producing an analysis increment. |
| `hofx_cf` | `geos_cf` | Run HofX for GEOS-CF atmospheric composition when you need simulated observations, departures (O-B), or observation diagnostics without producing an analysis increment. |
| `3dvar_atmos` | `geos_atmosphere` | Run a non-cycling atmospheric 3DVAR analysis when one atmospheric background state represents each assimilation window and you need an analysis increment. |
| `3dvar_marine` | `geos_marine` | Run a non-cycling marine 3DVAR analysis when one marine background state represents each assimilation window and you need a SOCA analysis increment. |
| `3dvar_marine_cycle` | `geos_marine` | Run cycling marine 3DVAR with GEOS when each SOCA analysis must update the coupled forecast used by a later cycle. |
| `3dvar_cf` | `geos_cf` | Run a non-cycling GEOS-CF 3DVAR analysis when one composition background represents each assimilation window and you need a composition analysis increment. |
| `3dvar_cf_cycle` | `geos_cf` | Run cycling GEOS-CF 3DVAR when each composition analysis must be applied to a GEOS-CF forecast and its restarts saved for later cycles. |
| `3dfgat_atmos` | `geos_atmosphere` | Run a non-cycling atmospheric 3D-FGAT analysis when observation timing within the assimilation window matters and time-varying atmospheric backgrounds are available. |
| `3dfgat_marine_cycle` | `geos_marine` | Run cycling marine 3D-FGAT with GEOS when time-varying marine backgrounds are available and each analysis must update the coupled forecast used by a later cycle. |
| `localensembleda` | `geos_atmosphere` | Run local ensemble data assimilation, such as GETKF, when flow-dependent uncertainty is central to the experiment and a compatible atmospheric background ensemble is available. |

Here, **cycling** means that output from one analysis or forecast becomes input to a later cycle.
For example, `3dvar_atmos` can cover several cycle points, but it retrieves a background for each
analysis from an different run (e.g., geos-fp) instead of running the forecast that connects the analyses. Choose a `*_cycle` suite when Swell must run the forecast and manage that feedback loop.

Use the least complex analysis method that produces the information you need. HofX applies the
observation operator to a supplied background but does not produce an analysis increment. 3DVAR
uses one background state to represent an assimilation window. 3D-FGAT uses time-varying
background states so observations can be evaluated against a background valid near their
observation times. Local ensemble data assimilation uses a background ensemble to represent
flow-dependent uncertainty. Cycling additionally runs the forecast model and carries an analysis
or restart into later cycles, requiring more compute resources and storage.

Swell currently provides three JEDI model interfaces: `geos_atmosphere` for the GEOS atmosphere
with FV3-JEDI, `geos_marine` for the GEOS marine component with SOCA, and `geos_cf` for GEOS-CF
atmospheric composition.

For marine analysis suites, MOM6 is required; CICE6 is optional when
sea-ice variables and observations are part of the analysis. Review the
[MOM6](../configuration_reference/model_configurations/mom6.md) and
[CICE6](../configuration_reference/model_configurations/cice6.md) settings before changing
`marine_models`.



## Ingestion, conversion, and comparison suites

| Suite | Goal |
| --- | --- |
| `ingest_obs_marine` | Ingest local marine observations (in IODA format) in R2D2. |
| `ingest_obs_cf` | Download, convert, and ingest atmospheric composition observations when raw observations must be downloaded and converted to IODA before being stored in R2D2. |
| `ingest_background_cf` | Ingest local GEOS-CF background files in R2D2. |
| `convert_bufr` | Convert atmospheric observations from supported BUFR classes. |
| `convert_ncdiags` | Convert GSI diagnostic and bias-correction files to IODA. |
| `compare_variational_atmosphere` | Compare the cost functions, increments, and observations from two compatible, completed atmospheric 3DVAR experiments. |
| `compare_variational_marine` | Compare the cost functions, increments, and observations from two compatible, completed marine 3DVAR experiments. |
| `compare_variational_cf` | Compare the cost functions, increments, and observations from two compatible, completed GEOS-CF 3DVAR experiments. |
| `compare_fgat_marine` | Compare the cost functions, increments, and observations from two compatible, completed marine 3D-FGAT experiments. |

The ingestion suites can store existing IODA files or download and convert raw observations before
ingestion, or register GEOS-CF backgrounds. See
[Storing Observations and Backgrounds in R2D2](../practical_examples/r2d2/r2d2_ingest.md) for the
available pipelines and their configuration files.

The comparison suites take paths to two completed `experiment.yaml` files. The experiments must
use the same model interface and have compatible assimilation windows. If cycle bounds are
omitted, the suite finds their common cycle times. See
[Comparing Experiment Outputs](../practical_examples/generic_suites/comparison_workflows.md).

## Test and specialized suites

Names ending in `_tier1` or `_tier2` select configurations used by Swell's automated suite tests;
they are not different analysis methods. Start with the unsuffixed suite unless you are reproducing
a tier test or a workflow guide explicitly asks for a tier configuration.

Swell also exposes specialized suites such as `forecast_coupled_geos`, `geosadas`, `ufo_testing`,
`eva_capabilities`, `build_jedi`, and `build_geos`. These support forecasting, development,
compatibility tests, evaluation, or an isolated build. They are not the usual starting point for an
analysis experiment.

After selecting a suite, continue to [Understanding Configuration](understanding_configuration.md)
to decide how to supply experiment-specific values.
