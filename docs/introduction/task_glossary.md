# Glossary of tasks in Swell

This is a very brief overview of the basic functions of each Swell task. The exact function of each task can be very complicated (or may not even perform any action) depending on individual experiment parameters. This list serves to provide the most basic explanation of the core functions of each task.

### BufrToIoda
Converts BUFR files present in the cycle directory to IODA format using `bufr-query`.

### BuildGeosByLinking
Creates links in the experiment directory to an existing build of GEOS.

### BuildGeos
Executes building GEOS from the source present in the experiment.

### BuildJediByLinking
Creates links to an existing build of JEDI in the experiment directory.

### BuildJedi
Executes building JEDI from the source files in the experiment directory.

### CleanCycle
Final clean-up task for intermediate files in the experiment.

### CloneGeosMksi
Clones the `GEOS_mksi` repository at a certain tag, which defines active and available instrument channels per time period.

### CloneGeos
Clones the `GEOSgcm` repository at a certain tag, which contains the source files for the GEOS model components.

### CloneGmaoPerllib
Clones the `GMAO_perllib` repository, which provides the `acquire` and `acquire_obsys` executables, used to grab BUFR files for particular observations at a certain time.

### CloneJedi
Clones selected JEDI repositories, set by the `bundles` parameter.

### ConvertObsToIoda
Downloads observations and converts them to IODA using selected ioda-converter executables.

### DownloadObs
Downloads raw observation files from remote servers. Differs from `GetObservations` since it does not use `R2D2`, instead using `https` or `cmr`.

### EvaComparisonIncrement
Generates comparison plots for JEDI increments between two experiments. Creates three-panel plots, with control, experiment, and difference panels

### EvaComparisonJediLog
Generates comparison plots of JEDI log output, using EVA.

### EvaComparisonObservations
Generates comparison plots of JEDI IODA outputs, using EVA.

### EvaIncrement
Creates increment plots using EVA, based on template yamls stored in each suite.

### EvaJediLog
Creates jedi log plots (Residual norm, log norm reduction) using EVA.

### EvaObservations
Creates observation plots from IODA, using eva. Plots are based on template yamls stored in each suite.

### EvaTimeseries
Creates time series plots of observations, using EVA.

### GenerateBClimatologyByLinking
Links to B Matrix files for background error models, from static files location.

### GenerateBClimatology
Runs JEDI executable for creating B Matrix files for background error models.

### GenerateObservingSystemRecords
Parses `GEOS_mksi` repository for active and available instrument channel information.

### GetBackgroundGeosExperiment
Gets background files from an existing GEOS-FP experiment. Primarily used by `geos_atmosphere` experiments

### GetBackground
Gets background files from `R2D2`.

### GetBufr
Uses the `GMAO_perllib` `acquire` function to copy BUFR files to the experiment.

### GetCoupledGeosRestart
Copies coupled GEOS restart files to the forecast directory.

### GetEnsembleGeosExperiment
Gets background files from an existing ensemble experiment.

### GetEnsemble
Grabs ensemble member files from an existing location.

### GetGeosAdasBackground
Gets background files from an existing `GEOSADAS` (ADAS-Atmospheric Data Assimilation System) experiment.

### GetGeovals
Get GeoVaLs (Geophysical Values at Locations) observation files from R2D2, from a particular GeoVaLs experiment.

### GetGsiBc
Gets bias correction files from an existing path to GSI bias correction coefficients.

### GetGsiNcdiag
Links GSI ncdiag (NetCDF Diagnostics) files from a local location.

### GetNcdiags
Gets ncdiag (NetCDF Diagnostics) files from a particular experiment using R2D2.

### GetObsNotInR2d2
Links observation files from a local location, instead of R2D2. Mostly used by `geos_atmosphere` experiments.

### GetObservations
Gets observations from R2D2. Core task to most swell suites.

### GetRestartCf
`geos_cf`-specific task to get restarts from R2D2.

### GsiBcToIoda
Convert bias correction files to IODA format.

### GsiNcdiagToIoda
Convert ncdiag files to IODA format.

### IngestObs
Ingests observation files into R2D2.

### JediLogComparison
Parses the JEDI log files of two variational or fgat experiment's, then compares residual norm values for equality.

### JediOopsLogParser
Parses JEDI log file for certain parameters, such as residual norm

### LinkCoupledGeosOutput
Links coupled GEOS output files for JEDI to ingest.

### LinkGeosOutput
Links GEOS output files for JEDI to ingest.

### MoveDaRestart
Moves restart files into the next cycle directory for use.

### PrepCoupledGeosRunDir
Copies coupled GEOS files to the next cycle directory for use.

### PrepForecastCf
Performs setup in the scratch `forecast` directory for running the model.

### PrepareAnalysis
Updates variables in restart files with analysis variables.

### PublishComparisons
Copies relevant comparison output to a set directory, usually to publish on dataportal.

### RenderJediObservations
Renders a file `obs.yaml`, which contains the observation-relevant portion of the JEDI config before execution.

## JEDI Executable tasks
The `RunJedi` tasks largely function under the same premise, creating the JEDI config and calling the appropriate executable.

### RunJediConvertStateSoca2CiceExecutable
Converts increments from `soca` (Sea-ice Ocean and Coupled Assimilation) interface to `cice` interface.

### RunJediEnsembleMeanVariance
Sets up and runs JEDI ensemble mean variance executable.

### RunJediFgatExecutable
Sets up and runs JEDI FGAT (First Guess at Appropriate Time) executable.

### RunJediHofxEnsembleExecutable
Sets up and runs JEDI HofX ensemble executable (H(x) simulates observations by going from model space to observation space).

### RunJediHofxExecutable
Sets up and runs JEDI HofX executable (H(x) simulates observations by going from model space to observation space).

### RunJediLocalEnsembleDaExecutable
Sets up and runs JEDI local ensemble DA executable.

### RunJediObsfiltersExecutable
Sets up and runs obs filters executable.

### RunJediUfoTestsExecutable
Sets up and runs UFO (Unified Forward Operator) tests executable

### RunJediVariationalExecutable
Sets up and runs JEDI variational executable.

### SaveBackground
Ingests background files into R2D2.

### SaveForecastCf
Ingests forecast files into R2D2

### SaveObsDiags
Ingests obs diag files into R2D2

### SaveRestartCf
`geos_cf`-specific task to ingest restart files into R2D2

### SaveRestart
Ingests restart files into R2D2

### StageJedi
Performs setup for JEDI execution by copying set files into the cycle directory.