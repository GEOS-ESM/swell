# Installing swell using Lmod

Lmod is a powerful tool for managing multiple versions of software. The process of installing is a little involved but software is installed on Discover that eases the process.

1. Pick a location that you want to install the software and navigate to that directory

```bash
cd $NOBACKUP/opt
``````

2. Load the modules that swell needs in order to be installed. Swell is designed to work with the spack-stack modules that JEDI uses so load which ever version of spack-stack you wish to use. For convenience the latest stable version can be obtained with:

```bash
source /home/drholdaw/jedi_modules/modules-intel
```

3. Load the software that is used to perform the install.

```bash
module use -a /discover/nobackup/drholdaw/opt/modulefiles/core
module load py_lmod_installer
```

4. Issue the command to install swell:

```bash
py_installer GEOS-ESM/swell <local_name>
```

The setting `<local_name>` should be replaced with what you want to refer to the package. After installing you will do module load `swell/<local_name>`

After the install is completed you should have directories `src`, `modulefiles` and `core` containing the things needed to use swell. In particular you should have `modulefiles/core/swell/<local_name>.lua`.
