# Configuring `cylc` on Discover.

## Setting Cylc global defaults

Cylc consults a file in the user's home directory for default attributes.

Create a file called `$HOME/.cylc/flow/global.cylc` and fill it with the following:

```bash
[scheduler]
  UTC mode = True
  process pool timeout = PT10M
  process pool size = 4

[platforms]
  [[nccs_discover_cascade]]
    job runner = slurm
    install target = localhost
    hosts = localhost
  [[nccs_discover_sles15]]
    job runner = slurm
    install target = localhost
    hosts = localhost
```

## Configuring the executable
<u>Note:</u> As of PR 537, configuration of the Cylc executable on Discover is handled automatically by Swell. The following instructions are for earlier versions, and will be removed in a future PR. Removing/renaming the existing `~/bin/cylc` is recommended.

 The following script loads spack-modules and the latest `cylc` installation. To run `cylc` locally, create a file called `$HOME/bin/cylc` for running `cylc` on Discover and fill it with the following :

```bash
#!/usr/bin/env bash

# Initialize modules
source $MODULESHOME/init/bash

# Load python dependencies
echo "Using SLES15 modules"
module use /discover/swdev/jcsda/spack-stack/scu17/modulefiles
module use /gpfsm/dswdev/jcsda/spack-stack/scu17/spack-stack-1.9.0/envs/ue-intel-2021.10.0/install/modulefiles/Core
module load stack-intel/2021.10.0
module load stack-intel-oneapi-mpi/2021.10.0
module load stack-python/3.11.7
module load py-pip/23.1.2

# Load the cylc module
module use -a /discover/nobackup/projects/gmao/advda/swell/dev/modulefiles/core/
module load cylc/sles15_8.4.0

# Run cylc command
cylc "$@"
```

Afterwards, make sure that the `$HOME/bin/cylc` file has executable permission:

```bash
chmod +x $HOME/bin/cylc
```

