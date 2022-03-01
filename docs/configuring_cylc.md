# Configuring Cylc

Start by creating a file called `cylc` that is always visible in the path. A good choice is typically
something like `$HOME/bin/cylc`, where `$HOME/bin` is always in the path. In this new file copy the
below contents:


```
#!/usr/bin/env bash

source $MODULESHOME/init/bash

# Load cylc module
export DHOPT=/discover/nobackup/drholdaw/opt/
module use -a $DHOPT/modulefiles/core
module load miniconda/3.9-cylc

# Run cylc command
cylc "$@"
```

The role of this file is to redirect each issuance of `cycl` through the version of Cylc loaded by
the module. This saves you explicitly loading the module everywhere Cylc is needed, for example
within the workflow. You can test that the above works properly by issuing `cylc --version`

Cylc uses a file called `$HOME/.cylc/flow/global.cylc` to control common aspects of the workflow
system. Create this file and then fill it with the following:

```
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

The above steps only need to be completed once.
