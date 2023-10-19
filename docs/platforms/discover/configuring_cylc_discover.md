# Configuring `cylc` on Discover.

 Create a file called `$HOME/bin/cylc` for running `cylc` on Discover. Fill it with the following :

```bash
#!/usr/bin/env bash

# Initialize modules
source $MODULESHOME/init/bash

# Load python module
module use /discover/swdev/jcsda/spack-stack/modulefiles
module load miniconda/3.9.7

# Load cylc module
module use -a /discover/nobackup/drholdaw/opt/modulefiles/core/
module load cylc

# Run cylc command
cylc "$@"
```

Create a file called `$HOME/.cylc/flow/global.cylc` and fill it with the following:

```bash
[scheduler]
  UTC mode = True
  process pool timeout = PT10M
  process pool size = 4

[platforms]
  [[nccs_discover]]
    job runner = slurm
    install target = localhost
    hosts = localhost
```




