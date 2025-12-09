# (Advanced) Setting up AWS for Swell

## Build spack-stack

Building spack-stack (at least, the unified-dev environment --- we may be able to get away with a subset of what's in there) takes a long time (~6 hours) and produces ~11 GB of binaries.
Before doing this, check if an existing spack-stack install for the relevant operating system exists.
For example, for the install below, a pre-existing spack-stack installation is stored in `/fast1/spack-envs/`.

### Install spack-stack dependencies

For this cluster, these dependencies are installed as part of the AMI (virtual machine image) used by the cluster.
For the latest version of that configuration, see scripts in https://github.com/ashiklom/smce-gmao-tf/tree/main/deployments/pcluster/image (note: this is a private repository, for security reasons).

An excerpt of the dependencies (for Ubuntu 24.04) is listed below for reference:

```sh
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y \
  build-essential \
  g++-11 \
  g++-12 \
  g++-13 \
  gcc-11 \
  gcc-12 \
  gcc-13 \
  gfortran-11 \
  gfortran-12 \
  gfortran-13 \
  make \
  apt-utils \
  autoconf \
  automake \
  autopoint \
  bc \
  bzip2 \
  cmake \
  cpp-11 \
  curl \
  file \
  flex \
  gettext \
  gh \
  git \
  git-lfs \
  golang \
  gnupg2 \
  iproute2 \
  less \
  libcurl4-openssl-dev \
  libgomp1 \
  liblua5.3-dev \
  liblua5.3.0 \
  libmysqlclient-dev \
  libqt5svg5-dev \
  libtcl8.6 \
  libtool \
  libtree \
  locales \
  lua-bit32 \
  lua-posix \
  lua-posix-dev \
  lua5.3 \
  make \
  mysql-server \
  pkg-config \
  python3 \
  python3-pip \
  python3-setuptools \
  qt5-qmake \
  qt5dxcb-plugin \
  qtbase5-dev \
  tcl \
  tcl-dev \
  tcl8.6 \
  tcl8.6-dev\
  unzip \
  wget

# Install lmod manually
(
  LMOD_TMP=$(mktemp -d)
  cd "$LMOD_TMP"
  wget https://github.com/TACC/Lmod/archive/refs/tags/8.7.60.tar.gz
  tar -xf 8.7.60.tar.gz
  cd Lmod-8.7.60
  sudo mkdir -p /opt
  ./configure --prefix=/opt/ --with-lmodConfigDir=/opt/lmod/8.7/config
  sudo make install
)
sudo ln -sf /opt/lmod/lmod/init/profile /etc/profile.d/z00_lmod.sh
sudo ln -sf /opt/lmod/lmod/init/cshrc /etc/profile.d/z00_lmod.csh
sudo ln -sf /opt/lmod/lmod/init/profile.fish /etc/profile.d/z00_lmod.fish
```

### Install spack-stack

NOTE: This uses the `unified-dev` environment, which installs _everything_ --- GEOS, Skylab, NEPTUNE, GSI.
Therefore, it is very large (final install is ~12 GB) and takes a long time (~4 hours on a `c7i.xlarge`).

```sh
#!/usr/bin/env bash

set -uo pipefail
# set -euxo pipefail

umask 022

if [[ -z $SPACK_STACK_VERSION ]]; then
  echo "SPACK_STACK_VERSION is unset"
  exit 1
fi

if [[ -z $COMPILER ]]; then
  echo "COMPILER is unset"
  exit 1
fi

if [[ -z $ENVNAME ]]; then
  echo "ENVNAME is unset"
  exit 1
fi

ROOTDIR="/opt/spack/"
SRCDIR="$ROOTDIR/spack-stack"
ENVDIR="$ROOTDIR/envs"

SCRIPT_USER=$(whoami)

sudo mkdir -p "$ROOTDIR"
sudo chown "$SCRIPT_USER:$SCRIPT_USER" "$ROOTDIR"
chmod 755 "$ROOTDIR"

git clone --recurse-submodules "https://github.com/jcsda/spack-stack" $SRCDIR

cd "$SRCDIR"
git checkout "$SPACK_STACK_VERSION"
git submodule update

source setup.sh

# Change tcl to lmod
sed -i 's/tcl/lmod/g' configs/sites/tier2/linux.default/modules.yaml

spack stack create env \
  --site linux.default \
  --template unified-dev \
	--dir "$ENVDIR" \
	--name "$ENVNAME" \
	--compiler "$COMPILER"

cd "$ENVDIR/$ENVNAME"
spack env activate -p .

export SPACK_SYSTEM_CONFIG_PATH="$PWD/site"

spack external find --scope system \
  --exclude python \
  --exclude openssl \
  --exclude cmake

spack external find --scope system wget
spack external find --scope system mysql
spack external find --scope system grep
spack external find --scope system go

# Manually add gh
if [[ ! -f site/packages.yaml.bak ]]; then
  cp site/packages.yaml{,.bak}
fi
cat <<-EOF >> site/packages.yaml
  gh:
    externals:
    - spec: gh@2.45
      prefix: /usr
EOF

# spack compiler find --scope system "$COMPILER"

GCC13_VERSION=$("$COMPILER-13" --version | head -n1 | grep -oP ' \d+\.\d+\.\d+ *$' | xargs)

QT_VERSION=$(apt-cache show qtbase5-dev | grep 'Version: ' | grep -oP '\d+\.\d+\.\d+')

unset SPACK_SYSTEM_CONFIG_PATH

spack config add "packages:all:compiler:[gcc@$GCC13_VERSION]"
spack config add "packages:all:providers:mpi:[openmpi@5.0.5]"
spack config add "packages:fontconfig:variants:+pic"
spack config add "packages:pixman:variants:+pic"
spack config add "packages:cairo:variants:+pic"
spack config add "packages:ewok-env:variants:+mysql"

# Concretize and install
spack concretize 2>&1 | tee log.concretize
# cat log.concretize | ${SPACK_STACK_DIR}/util/show_duplicate_packages.py
spack install --fail-fast 2>&1 | tee log.install

# Install lmod modules
spack module lmod refresh
spack stack setup-meta-modules
```

### (Optional, but recommended) Set up shortcuts for swell modules

To avoid asking all users to remember what modules need to be loaded for Swell, create a file with the following contents that can be `source`-d to quickly load everything needed for Swell.

Be sure to adjust the path in the first `module use` statement to wherever you installed spack-stack in the previous step.

```sh
# Adapted from:
# /discover/nobackup/projects/gmao/advda/swell/jedi_modules/spackstack_1.9_intel

module purge

# NOTE: Change this path to match the spack-stack installation above.
module use /fast1/spack-envs/unified-env-gcc/install/modulefiles/Core

module load stack-gcc/13.3.0
module load stack-openmpi/5.0.5
module load stack-python/3.11.7

# JEDI
module load jedi-fv3-env
module load soca-env
module load gmao-swell-env

# Extras
module load git-lfs/3.4.1
module load py-pip/23.1.2

# vim: set filetype=sh :
```

## Building JEDI

Swell uses [`jedi_bundle`](https://github.com/geos-esm/jedi_bundle) to build JEDI.
This will clone, configure, and build specific versions of all JEDI components needed for Swell.
Note that some of these components are in private repositories, so you will need to follow the [instructions in the `jedi_bundle` documentation](https://geos-esm.github.io/jedi_bundle/#/git_credentials) to set up your Git credentials.

An install script like the following should work.

**NOTE**: The `cat <<EOF > ...` step below creates a new file in the `jedi_bundle` _source_ repository to create an AWS configuration. In the future, this will be included in the main `jedi_bundle` repo and will not be necessary here.

```sh
#!/usr/bin/env bash
#SBATCH --partition demand-16cpu

# ^^ SBATCH directive here is for building this directly on the cluster.

JEDI_ROOT="/efs/jedi/"
JEDI_BUNDLE_SRC="$JEDI_ROOT/jedi_bundle"
SPACK_ROOT="/fast1/spack-envs/unified-env-gcc/"
S3DIR="/s3"

VERSION="latest"
GCCVER="13.3.0"
SKYLAB_VERSION="2.4.1_skylab_4.0"

N_AVAILABLE_CORES=$(nproc)

mkdir -p "$JEDI_ROOT"

if [[ ! -f "$SPACK_ROOT/spack.lock" ]]; then
  echo "$SPACK_ROOT not found or improperly configured"
  exit 1
fi

if [[ ! -d "$S3DIR/SwellStaticFiles" ]]; then
  echo "Couldn't find $S3DIR/SwellStaticFiles"
  exit 1
fi

JEDI_BUILD="$JEDI_ROOT/builds/jedi-build-gcc_$GCCVER"
if [[ -d "$JEDI_BUILD" ]]; then
  echo "Existing JEDI build found in this directory. Exiting..."
  exit 1
fi

if [[ ! -d "$JEDI_BUNDLE_SRC" ]]; then
  git clone https://github.com/geos-esm/jedi_bundle $JEDI_BUNDLE_SRC
fi

cd "$JEDI_BUNDLE_SRC"

## Using geos-esm/jedi_bundle
module use -a $SPACK_ROOT/install/modulefiles/Core

module purge
module load stack-gcc/13.3.0
module load stack-openmpi/5.0.5
module load stack-python/3.11.7
module load git-lfs/3.4.1
module load py-pip/23.1.2

mkdir -p $JEDI_BUILD
cd $JEDI_BUILD
python -m venv ".venv"
source .venv/bin/activate

# Before we install JEDI, need to add an AWS configuration
cat <<EOF > $JEDI_BUNDLE_SRC/src/jedi_bundle/config/platforms/aws.yaml
platform_name: aws

is_it_me:
  - command: 'echo \$SLURM_CLUSTER_NAME'
    contains: 'gmao-pcluster'
crtm_coeffs_path: "$S3DIR/SwellStaticFiles/jedi/crtm_coefficients/"
crtm_coeffs_version: "$SKYLAB_VERSION"
modules:
  default_modules: gnu
  gnu:
    init:
      - source /opt/lmod/lmod/init/bash
    load:
      - module purge
      - module use $SPACK_ROOT/install/modulefiles/Core
      - module load stack-gcc/13.3.0
      - module load stack-openmpi/5.0.5
      - module load stack-python/3.11.7
      - module load jedi-fv3-env
      - module load soca-env
      - module load gmao-swell-env
    configure: '-DCMAKE_Fortran_FLAGS="-ffree-line-length-none"'
    # configure: -DMPIEXEC_EXECUTABLE="/usr/bin/srun" -DMPIEXEC_NUMPROC_FLAG="-n"
  gnu-geos:
    init:
      - source /opt/lmod/lmod/init/bash
    load:
      - module purge
      - module use $SPACK_ROOT/install/modulefiles/Core
      - module load stack-gcc/13.3.0
      - module load stack-openmpi/5.0.5
      - module load stack-python/3.11.7
      - module load jedi-fv3-env
      - module load soca-env
      - module load gmao-swell-env
      - module load esmf python py-pyyaml py-numpy pflogger fargparse zlib-ng cmake
    configure: '-DCMAKE_Fortran_FLAGS="-ffree-line-length-none"'
    # configure: -DMPIEXEC_EXECUTABLE="/usr/bin/srun" -DMPIEXEC_NUMPROC_FLAG="-n"
EOF

pip install "$JEDI_BUNDLE_SRC"

echo "JEDI bundle path:"
which jedi_bundle

# Generate config file
jedi_bundle --pinned_versions

# Tweak config file
sed -i "/ *cores_to_use_for_make/s/6/$N_AVAILABLE_CORES/" build.yaml

# Run
jedi_bundle all build.yaml

```

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
module load stack-gcc/13.3.0
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

The resulting GEOS installation lives is in `/efs/GEOSgcm/v11.6.0/install`.

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
