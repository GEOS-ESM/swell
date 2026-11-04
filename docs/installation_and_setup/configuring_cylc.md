# Configuring `cylc`


Before you can run a swell generated workflow it's necessary to configure `cylc`. Swell requires a `cylc` executable to be visible in the path, and `cylc` requires a file `$HOME/.cylc/flow/global.cylc` to set common aspects of the workflow system.

Configuring the `cylc` executable on Discover is handled automatically by Swell, so no additional steps are necessary. On other platforms, the user needs to ensure a `cylc` executable is immediately discoverable in the path. Usually this is achieved by creating a `~/bin/cylc` file which handles loading an existing `cylc` installation.

Additionally `cylc` uses a file called `$HOME/.cylc/flow/global.cylc` to control common aspects of the workflow system. The `cylc` documentation describes some of the things controlled by `global.cylc`.


---
**WARNING:**
The contents of the above two files will be platform specific.
---

See [Configuring Cylc Discover](platforms/discover/configuring_cylc_discover.md) for instructions on configuring cylc for Discover.
