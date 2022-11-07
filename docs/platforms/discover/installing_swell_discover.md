# Installing swell using Lmod

Swell is a Python package and is typically installed using pip. Often these kinds of packages are installed in a general space for Python packages. However, sometimes it's useful to maintain different versions of the software for different experiments. The following outlines how `Lmod` (Lua-based module system) can be used to safely set and unset the correct `PATH` and `PYTHONPATH` variables with little overhead as additional versions of the software are installed. The following assumes `Lmod` is available on the system.

### Cloning the swell code

The benefits of `Lmod` are realized only when abiding by a fairly strict directory naming convention for the installation and module files. The first step is to choose the base directory for the installation. This directory will contain the source code as well as the installation and the module files. Sub directories will follow `Lmod` standards.

As an example you might choose the base directory as being `$HOME/opt`, though it can be any location. Next you can make the directory where the code will be cloned to and then move to that directory:

```
mkdir –p $HOME/opt/src/swell/
cd $HOME/opt/src/swell/
```

Before cloning the code it's helpful to name the development that is being done so when it's loaded as a module (and especially if you have more than one module) you can keep track of it. For demonstration purposes we'll give this installation the generic name of **development**.  The code is then cloned with:

```
git clone https://github.com/GEOS-ESM/swell development
```

When working with swell you should start your development from a specific release tag rather than the develop branch, this ensures that swell works with a particular version of JEDI. It might not always be possible to use the develop version of swell with the develop versions of the JEDI code. Sometimes the two systems get out of sync and some work is required to re-sync. The latest release of swell can be found [here](https://github.com/GEOS-ESM/swell/releases). Once settled on a release tag you can switch to that tag with

```
cd development        # Change to directory where the code was cloned
git checkout x.x.x    # Replace x.x.x with the desired tag
```

### Installing the swell code

Now we are ready to install swell. Swell requires Python3 and depends on several third-party dependencies. It is critical to align the `swell` installation with the dependencies that the application executables will be run with. For JEDI and GEOS this is achieved using `spack`. To load the most recent `spack` Intel-based modules use:

```
module purge
source /discover/nobackup/drholdaw/JediDev/modules/modules-intel
```

Since we are using `Lmod` we'll follow the standard module package paths and install to the `core` directory:

```
umask 022  # Ensure pip has permission to create directories
pip install --prefix=$HOME/opt/core/swell/development .
```

---
**WARNING:**
When pip finds an existing Python package with the same name as the one being installed it will try to overwrite it. The `module purge` step helps ensure that swell doesn't already exist in the path. It is generally not a good idea to use swell and install swell in the same window as it can be easy to run an install command when having an improper module loaded.
---

### Deploying the module

Now that the code is installed we can deploy the `Lmod` module to make for ease of access. First we make the directory where the module file will reside, again following `Lmod`-recommended path naming:

```
mkdir -p $HOME/opt/modulefiles/core/swell
```

Now we create an empty module file with a name corresponding to the above:

```
touch $HOME/opt/modulefiles/core/swell/development.lua
```

The contents of the `development.lua` file should should contain the following:

```
help([[]])

local pkgName    = myModuleName()
local pkgVersion = myModuleVersion()
local pkgNameVer = myModuleFullName()

conflict(pkgName)

local home = os.getenv("HOME")
local opt = pathJoin(home,"opt")
local pythondir = "python3.9"
local base = pathJoin(opt,"core",pkgNameVer)

prepend_path("PATH", pathJoin(base,"bin"))
prepend_path("PYTHONPATH", pathJoin(base,"lib",pythondir,"site-packages"))

whatis("Name: ".. pkgName)
whatis("Version: " .. pkgVersion)
whatis("Category: Software")
whatis("Description: Swell Workflow Ecosystem, Layout and Launcher")
```

The line `local pythondir = "python3.9"` needs to be adjusted to reflect the local version of Python.

---
**NOTE:**
Note that the `development.lua` file does not refer to the name `developement`. This demonstrates the power of using `Lmod` and why such specific paths were required for the install and location of the module files. `Lmod` using this directory structure to locate code and reference itself.
---

Now you can deploy the module with:

```
module use -a $HOME/opt/modulefiles/core
module load swell/development
```

To ensure that the software was properly installed and is available you can issue:

```
which swell_create_experiment
```

If the above does not return the expected path to swell it is likely something went wrong with the installation. If you do not have directories like `$HOME/opt/core/swell/development/bin` and `$HOME/opt/core/swell/development/lib` then swell did not install properly.

### Additional swell installs

The advantage of using a module approach is that it makes it straightforward to install further versions of swell that you can easily switch between. The following demonstrates the process that would be taken to install another version of swell where you can make parallel developments.

```
cd $HOME/opt/src/swell/
git clone https://github.com//GEOS-ESM/swell development2
cd development2
git checkout <tag>

pip install --prefix=$HOME/opt/core/swell/development2 .

cd $HOME/opt/modulefiles/core/swell
cp development.lua development2.lua

module load swell/development2
```

Note that in the above `development` is changed to `development2` but there is no restriction on the name you choose.
