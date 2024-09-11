# Configuring `cylc`

Before you can run a swell generated workflow it's necessary to configure `cylc`. This is only done before the first run, or when the `cylc` version needs to be updated or when the behavior of `cylc` needs to be modified.

For the first step of this configuration it is necessary to ensure `cylc` is immediately visible in your path when starting a new session. This is achieved by creating a file `$HOME/bin/cylc` (which is typically in the path). This file can then add additional things to the path to start `cylc`.

Additionally `cylc` uses a file called `$HOME/.cylc/flow/global.cylc` to control common aspects of the workflow system. The `cylc` documentation describes some of the things controlled by `global.cylc`.


---
**WARNING:**
The contents of the above two files will be platform specific.
---

See `docs/platforms/configuring_cylc_discover.md` for instructions on configuring cylc for Discover.
