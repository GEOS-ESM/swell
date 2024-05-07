# Installing swell using Lmod

Lmod is a powerful tool for managing multiple versions of software. The process of installing is a little involved but `py_lmod_installer` software is installed on Discover that eases the process.

This tool combines cloning, installation, and module file creation for Swell develop branch under one command.

1. Pick a location that you want to install the software and navigate to that directory

```bash
cd $NOBACKUP/opt
``````

2. Load the modules that swell needs in order to be installed. Swell is designed to work with the spack-stack modules that JEDI uses so load which ever version of spack-stack you wish to use. For convenience the latest stable version can be obtained with:

```bash
source /discover/nobackup/projects/gmao/advda/swell/jedi_modules/modules-intel
```

3. Load the software that is used to perform the install.

```bash
module use -a /discover/nobackup/projects/gmao/advda/swell/dev/modulefiles/core
module load py_lmod_installer
```

4. Issue the command to install swell:
 

```bash
py_installer GEOS-ESM/swell <local_name>
```

The setting `<local_name>` should be replaced with what you want to refer to the package. After installing you will do module load `swell/<local_name>`


<details>
  <summary> <strong> Advanced Tip:</strong> </summary>

If you would like to install a particular branch, you can use the `-b` option:

```bash
py_installer GEOS-ESM/swell -b <branch_name> <local_name>
```
</details>

After the install is completed you should have directories `src`, `modulefiles` and `core` containing the things needed to use swell. In particular you should have `modulefiles/core/swell/<local_name>.lua`.
