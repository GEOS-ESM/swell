# Installing swell using Lua modules

Swell is a Python package and is typically installed using pip. The following outlines how
swell can be installed and deployed as a Lua module. This requires Lua modules being available on
the target system.

### Cloning the swell code

The first step is to choose the base directory for the installation. This directory will contain the source
code as well as the installation and the module files. Sub directories will follow Lua standards.

As an example you might choose the base directory as being `$NOBACKUP/opt`, though it can be any
location. Next you can make the directory where the code will be cloned to and then move to that directory:

```
mkdir –p $NOBACKUP/opt/src/swell/
cd $NOBACKUP/opt/src/swell/
```

Before cloning the code it's helpful to name the development that is being done so when it's loaded
as a module (and if you have more than one module) you can keep track of it. For demonstration
purposes we'll give this installation the generic name of **development**.  The code is then cloned
with:

```
git clone https://github.com/GEOS-ESM/swell development
```

When working with swell you should start your development from a specific tag rather than the
develop branch, this ensures that swell works with a particular version of JEDI. It might not always
be possible to use the develop version of swell with the develop versions of the JEDI code.
Sometimes the two systems get out of sync and some work is required to re-sync. The latest stable tag of
swell can be found [here](release_notes.md). Once settled on a tag you can switch to that tag with

```
cd development        # Change to directory where the code was cloned
git checkout 1.0.1    # Replace 1.0.1 with the desired tag
```

### Installing the swell code

Now we are ready to install swell. Swell requires Python 3 and depends on several third-party dependencies. If using
your own Python install and these packages dependencies are not already met they will be installed by pip in the
same location as swell. For convenience a Miniconda install is provided on Discover with all the
dependencies required by swell. This can be made available to load with:

```
export DHOPT=/discover/nobackup/drholdaw/opt/
module use -a $DHOPT/modulefiles/core
```

---
**WARNING**
It might seem like the setting of `$DHOPT` in the above is not necessary but it is used within the
module file so has to be explicitly set.
---

Since we are using Lua modules we'll follow the standard module package paths and install to the
`core` directory:

```
module purge
module load miniconda/3.9
umask 022  # Ensure pip has permission to create directories
pip install --prefix=$NOBACKUP/opt/core/swell/development .
```

---
**WARNING**
When pip finds an existing Python package with the same name as the one being installed it will try
to overwrite it. The `module purge` step helps ensure that swell doesn't already exist in the path.
---

### Deploying the module

Now that the code is installed we can deploy the Lua module to make for ease of access. First we
make the directory where the module file will reside, again following Lua-recommended path naming:

```
mkdir -p $NOBACKUP/opt/modulefiles/core/swell
```

Now we create an empty module file:

```
cd $NOBACKUP/opt/modulefiles/core/swell
touch development.lua
```

The contents of the `development.lua` file should should contain the following:

```
help([[
]])

local pkgName    = myModuleName()
local pkgVersion = myModuleVersion()
local pkgNameVer = myModuleFullName()

conflict(pkgName)

local opt = os.getenv("FLOPT")
local pythondir = "python3.9"

local base = pathJoin(opt,"core",pkgNameVer)

prepend_path("PATH", pathJoin(base,"bin"))
prepend_path("PYTHONPATH", pathJoin(base,"lib",pythondir,"site-packages"))
prepend_path("SUITEPATH", pathJoin(base,"lib",pythondir,"site-packages","swell","suites"))
prepend_path("SUITESPATH", pathJoin(base,"lib",pythondir,"site-packages","swell","suites"))

whatis("Name: ".. pkgName)
whatis("Version: " .. pkgVersion)
whatis("Category: Software")
whatis("Description: Swell Workflow Ecosystem, Layout and Launcher")
```

In the above the line `local opt = os.getenv("FLOPT")` needs to be changed to use an environment
variable that is unique to you. For example replace `FLOPT` with your own **F**irst and **L**ast
initial. You may also need to change the line `local pythondir = "python3.9"` if the version of
Python is different from 3.9.

Now you can deploy the module with:

```
export FLOPT=$NOBACKUP/opt                  # Replace FLOPT with the choice made above
module use -a $FLOPT/modulefiles/core
module load swell/development
```

To ensure that the software was properly installed and is available you can issue:

```
which swell_create_experiment
```

If the above does not return the expected path to swell it is likely something went wrong with the
installation. If you do not have directories like `$NOBACKUP/opt/core/swell/development/bin` and
`$NOBACKUP/opt/core/swell/development/lib` then swell did not install properly.

### Additional swell installs

The advantage of using a module approach is that it makes it straightforward to install further
versions of swell that you can easily switch between. The following demonstrates the process that
would be taken to install another version of swell where you can make parallel developments.

```
cd $NOBACKUP/opt/src/swell/
git clone https://github.com//GEOS-ESM/swell development2
cd development2
git checkout <tag>

pip install --prefix=$NOBACKUP/opt/core/swell/development2 .

cd $NOBACKUP/opt/modulefiles/core/swell
cp development.lua development2.lua

module load swell/development2
```

Note that in the above `development` is changed to `development2` but there is no restriction on the
name you choose.
