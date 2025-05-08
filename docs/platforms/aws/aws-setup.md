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
