# Prerequisites

Before installing Swell, make sure you have:

- **A platform.** Swell is developed and tested primarily on NASA's Discover cluster, which has dedicated instructions — see [Supported Platforms](../installation_and_setup/platforms/README.md). Other platforms are supported in principle, but you're responsible for satisfying the dependencies below yourself.
- **Python and matching dependencies.** Swell is a Python package installed with pip. It shares dependencies with the applications it drives (JEDI, GEOS), so these must be satisfied consistently. On Discover, loading the correct `spack-stack` modules before installing avoids this. See [Installing Swell](../installation_and_setup/installing_swell.md).
- **Cylc.** Swell generates `flow.cylc` workflows but does not install or manage Cylc itself. You need a `cylc` executable on your `$PATH` and a `$HOME/.cylc/flow/global.cylc` file. On Discover this is handled automatically. See [Configuring Cylc](../installation_and_setup/configuring_cylc.md).
- **R2D2 credentials.** A `~/.swell/r2d2_credentials.yaml` file is required for `swell create` to register experiments and for tasks to fetch/store data. See [R2D2 v3 Credentials](../configuration_reference/r2d2_v3_credentials.md).
- **Accounts for external data (if ingesting observations).** Some observation providers require their own authentication (e.g. an Earthdata account). See [Storing Observations and Backgrounds in R2D2](../practical_examples/r2d2/r2d2_ingest.md).

Once these are in place, continue to [Installing Swell](../installation_and_setup/installing_swell.md).

