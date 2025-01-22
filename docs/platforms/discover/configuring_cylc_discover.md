# Configuring `cylc` on Discover.

 Spack modules for SLES12 and SLES15 are different and the following script handles this switch and loads proper `cylc` installation automatically. Create a file called `$HOME/bin/cylc` for running `cylc` on Discover and fill it with the following :

```bash
#!/usr/bin/env bash

# Initialize modules
source $MODULESHOME/init/bash

# Look for the OS version and set the module path accordingly
OS_VERSION=$(grep VERSION_ID /etc/os-release | cut -d= -f2 | cut -d. -f1 | sed 's/"//g')

# Two different options according to the OS version:

if [ $OS_VERSION -eq 12 ]; then

    # Load python dependencies
    echo "Using SLES12 modules"
    module use /discover/swdev/jcsda/spack-stack/scu16/modulefiles
    module load miniconda/3.9.7

    # Load the cylc module
    module use -a /discover/nobackup/projects/gmao/advda/swell/dev/modulefiles/core/
    module load cylc

elif [ $OS_VERSION -eq 15 ]; then

    # Load python dependencies
    echo "Using SLES15 modules"
    module use /discover/swdev/jcsda/spack-stack/scu17/modulefiles
    module use /gpfsm/dswdev/jcsda/spack-stack/scu17/spack-stack-1.7.0/envs/ue-intel-2021.10.0/install/modulefiles/Core
    module load stack-intel/2021.10.0
    module load stack-intel-oneapi-mpi/2021.10.0
    module load stack-python/3.10.13
    module load py-pip/23.1.2

    # Load the cylc module
    module use -a /discover/nobackup/projects/gmao/advda/swell/dev/modulefiles/core/
    module load cylc/sles15_8.2.4
else
    echo "OS version not supported"
    exit 1
fi

# Run cylc command
cylc "$@"
```

Afterwards, make sure that the `$HOME/bin/cylc` file has executable permission:

```bash
chmod +x $HOME/bin/cylc
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
  [[nccs_discover_cascade]]
    job runner = slurm
    install target = localhost
    hosts = localhost
  [[nccs_discover_sles15]]
    job runner = slurm
    install target = localhost
    hosts = localhost
```




