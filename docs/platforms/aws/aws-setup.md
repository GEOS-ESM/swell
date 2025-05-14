# (Advanced) Setting up AWS for Swell

## Build spack-stack

Building spack-stack (at least, the unified-dev environment --- we may be able to get away with a subset of what's in there) takes forever (~6 hours) and produces ~76 GB of binaries.
Before doing this, check if an existing spack-stack install for the relevant operating system exists.
For example, for the install below, a pre-existing spack-stack installation is stored in `s3://gmao-spack-stack`.

### Install spack-stack dependencies

This assumes Ubuntu 22.04.

```sh
#!/usr/bin/env bash

set -euo pipefail

################################################################################
# Spack-stack dependencies
# https://spack-stack.readthedocs.io/en/1.9.1/NewSiteConfigs.html#prerequisites-ubuntu-one-off
################################################################################

sudo apt-get update -y
sudo apt-get upgrade -y

# Dependencies
sudo apt-get install -y \
	gcc \
	g++ \
	gfortran \
	gdb \
	environment-modules \
	build-essential \
	libkrb5-dev \
	m4 \
	git \
	git-lfs \
	bzip2 \
	unzip \
	automake \
	autopoint \
	gettext \
	texlive \
	libcurl4-openssl-dev \
	libssl-dev \
	wget
```

### Install spack-stack

NOTE: This uses the `unified-dev` environment, which installs _everything_ --- GEOS, Skylab, NEPTUNE, GSI.
Therefore, it is **huge** (final install is ~76 GB) and takes **forever** (6-8 hours on a `t3.medium`).

```sh
#!/usr/bin/env bash

set -euo pipefail

################################################################################
# Creating a new environment
# https://spack-stack.readthedocs.io/en/1.9.1/NewSiteConfigs.html#prerequisites-red-hat-centos-8-one-off
################################################################################

cd /shared

git clone --recurse-submodules https://github.com/jcsda/spack-stack.git
cd spack-stack
# NOTE: This sets $SPACK_STACK_DIR to PWD
source setup.sh

# Create preconfigured environment
# NOTE: Add --template unified-dev to install *everything*.
ENVNAME="swell.my_aws"
TEMPLATE="unified-dev"
spack stack create env --site linux.default --name $ENVNAME --template $TEMPLATE --compiler=gcc
cd envs/$ENVNAME

# Activate the environment (-p sets the prompt)
spack env activate -p .

export SPACK_SYSTEM_CONFIG_PATH="$PWD/site"

# Find all external tools except the ones listed here
# NOTE: Dropping --scope system because it doesn't work ("invaid choice: 'system'")
spack external find --exclude cmake --exclude curl --exclude openssl --exclude openssh --exclude python
spack external find grep
spack external find sed
spack external find perl
spack external find wget

spack compiler find
unset SPACK_SYSTEM_CONFIG_PATH

spack config add "packages:all:compiler:[gcc@$(gcc -dumpfullversion)]"
spack config add "packages:all:compiler:[openmpi@5.0.3]"

spack config add "packages:fontconfig:variants:+pic"
spack config add "packages:pixman:variants:+pic"
spack config add "packages:cairo:variants:+pic"

# Process and install
spack concretize 2>&1 | tee log.concretize

# nohup spack install --yes-to-all --source --verbose --jobs 8 &> log.install &
spack install --source --verbose
spack module lmod refresh
spack stack setup-meta-modules
${SPACK_STACK_DIR}/util/check_permissions.sh

# Confirm that this works
module use ${SPACK_STACK_DIR}/envs/$ENVNAME/install/modulefiles/Core
module avail
module load stack-gcc/11.4.0
```

### (Optional, but recommended) Set up shortcuts for swell modules

To avoid asking all users to remember what modules need to be loaded for Swell, create a file with the following contents that can be `source`-d to quickly load everything needed for Swell.

Be sure to adjust the path in the first `module use` statement to wherever you installed spack-stack in the previous step.

```sh
# Adapted from:
# /discover/nobackup/projects/gmao/advda/swell/jedi_modules/spackstack_1.9_intel

module purge

# NOTE: Change this path to match the spack-stack installation above.
module use /shared/spack-stack/envs/swell.my_aws/install/modulefiles/Core

module load stack-gcc/11.4.0
module load stack-openmpi/5.0.5
module load stack-python/3.11.7

# JEDI
module load jedi-fv3-env/1.0.0
module load soca-env/1.0.0
module load gmao-swell-env/1.0.0

# Extras
module load git-lfs/3.0.2
module load py-pip/23.1.2

# vim: set filetype=sh :
```

## Building JEDI

NOTE: This builds skylab-v8 and assumes the instructions above were followed for building spack-stack.
This also builds JEDI to `/shared/build-jedi/build` --- you may want to give this a more informative path.

```sh
#!/usr/bin/env bash

set -euo pipefail

module purge
module use /shared/spack-stack/envs/swell.my_aws/install/modulefiles/Core

module load stack-gcc/11.4.0
module load stack-openmpi/5.0.5
module load ecbuild/3.7.2

if [[ ! -d jedi-bundle ]]; then
  git clone https://github.com/jcsda/jedi-bundle
fi

cd jedi-bundle
git switch release/skylab-v8

################################################################################

export JEDI_ROOT=/shared/build-jedi
export JEDI_SRC="$JEDI_ROOT/jedi-bundle"

cd "$JEDI_ROOT"
mkdir build
export JEDI_BUILD="$JEDI_ROOT/build"

# NOTE: Depends on stack-openmpi
module load jedi-fv3-env/1.0.0
module load ewok-env/1.0.0
module load soca-env/1.0.0

# NOTE: Depends on stack-gcc
module load sp/2.5.0

cd "$JEDI_BUILD"
ecbuild "$JEDI_SRC"
```

## Internal JCSDA dependencies

You will also need the following JCSDA dependencies that are not (currently) in public repositories:

- `r2d2`
- `solo`

Sources for these may be available in `/discover/nobackup/projects/gmao/advda/JediOpt/src`.

On Discover, these are available as environment modules.
On AWS, these are just open source code folders and are installed in Swell via `pip` (see `requirements-aws.txt`).

## Building GEOS

Follow the instructions on the GEOS-ESM repo (https://github.com/geos-esm/geosgcm).
The instructions below are abbreviated and opinionated and are meant only to document the configuration used for the current AWS Swell deployment.

Clone GEOS and checkout the relevant tag.

```sh
mkdir -p /shared/GEOSgcm
git clone https://github.com/geos-esm/geosgcm /shared/GEOSgcm/main

cd /shared/GEOSgcm/main
git worktree add ../v11.6.0 v11.6.0
```

Load required modules.
(NOTE: This includes a `mepo` installation).

```sh
module use /shared/spack-stack/envs/swell.my_aws/install/modulefiles/Core/
module load stack-gcc/11.4.0
module load stack-openmpi/5.0.5
module load geos-gcm-env/1.0.0
```

Clone stuff that GEOS needs.

```sh
cd /shared/GEOSgcm/v11.6.0
mepo clone
```

Build using cmake.
(NOTE: This assumes build directory `./build` and install directory `./install`).

```sh
# Configure the build
cmake -B build -S . --install-prefix=install
# ...and actually do the build
cmake --build build --target install
```

The resulting GEOS installation lives is in `/shared/GEOSgcm/v11.6.0/install`.

## Essential data for Swell

NOTE: These instructions are current as of **May 5, 2025**.
Data used by Swell change frequently as Swell evolves, so these instructions may quickly become outdated.
Hopefully, they give you a sense of how Swell looks for files.

### `SwellStaticFiles`

On Discover, these are stored in `/discover/nobackup/projects/gmao/advda/SwellStaticFiles`.
The relevant `task_question`s are:
- `swell_static_files` --- root directory
- `geos_experiment_directory` --- expands to: `<swell_static_files>/geos/run_dirs/<geos_experiment_directory>`
- `geos_restarts_directory` --- expands to `<swell_static_files>/geos/restarts/<geos_restarts_directory>`

The complete `SwellStaticFiles` directory on Discover is several hundred GB, but not all of the data are needed for basic Swell tier 1 tests.
You may be able to get away with copying over only the following:

- `/discover/nobackup/projects/gmao/advda/SwellStaticFiles/`
    - `/jedi/`
        - `interfaces/`
            - `/geos_ocean/model/`
            - `/geos_atmosphere/`
        - `/crtm_coefficients/`
    - `/geos/`
        - `/run_dirs/5deg_0701/`
        - `/restarts/restarts_20210701_210000_5deg/`

### `R2D2DataStore`

On Discover, this is stored in `/discover/nobackup/projects/gmao/advda/R2D2DataStore/Shared`.
As above, the full directory is quite large, but you may be able to get away with just the following:

- `/discover/nobackup/projects/gmao/advda/R2D2DataStore/Shared`
    - `mom6_cice6_UFS/fc/s2s/`
    - `geos/fc/x0048/`

### Local ensemble DA inputs

NOTE: These are only needed for the `localensembleda` suite, which is not a part of the core Swell tests (yet).
So, you may not need these...which is good, because these are massive (10s of TB). Be judicious about what you copy over!
In both cases, note also the `background_experiment` and background experiment start and end dates, as these will determine exactly which folders and files you need.
- Backgrounds:
    - See the `geos_x_background_directory` variable and the `GetEnsembleGeosExperiment` task.
    - By default, on Discover, these are in `/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x`.
    - On AWS, these are in `/efs/shared/restarts/jedi/541x/`.
    - An rsync command like the following may be useful:

    ```sh
    nohup rsync -avz --copy-unsafe-links --progress \
        --dry-run \
        --filter '+ 13/**' \
        --filter '+ 19/**' \
        --filter '+ 181/' \
        --filter '+ 181/x0050/' \
        --filter '+ 181/x0050/atmens' \
        --filter '+ 181/x0050/atmens/Y2023/' \
        --filter '+ 181/x0050/atmens/Y2023/M10/' \
        --filter '+ 181/x0050/atmens/Y2023/M10/*.20231009*' \
        --filter '+ 181/x0050/atmens/Y2023/M10/*.20231010*' \
        --filter '- 181/**'\
        --filter '- *'\
        /discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x/ \
        swelldev:/efs/shared/restarts/jedi/541x/ \
        &> ~/geos_bkg.log &
    ```

- Ensembles:
    - NOTE: These are needed only for the `localensembleda` suite, which is not a part of the core tests.
    - See the `geos_x_ensemble_directory` variable, the `GetEnsembleGeosExperiment` task, and the file `src/swell/configuration/jedi/interfaces/geos_atmosphere/task_questions.yaml`
        - Background experiment: `x0050`
    - By default, on Discover, these are in `/discover/nobackup/projects/gmao/dadev/rtodling/archive/541/Milan`.
