# Installing swell

Before you start reading this you may wish to check the platforms page to see if there are [platform](platforms/platforms.md) specific instructions that might be helpful.

Before installing `swell` you need to think about the dependencies. There are a number of dependencies of `swell`, such as `netCDF` that are likely also dependencies of the applications that `swell` will drive. For maximum safety these dependencies should be satisfied equivalently. For example, if you install `swell` using pip but do not have `netCDF` in the path then pip will take care of this install but will pick its own version. In order to access `swell` this version of `netCDF` installed by pip will have to be in the path. But if `swell` goes on to run an executable that was installed pointing to a different version of `netCDF` problems (that could be hard to diagnose) will likely follow. For the JEDI software system `spack` is utilized to ensure common dependencies and backends. Once development stabilizes we will add `swell` to the same `spack` system. In any case the following directions can be used to install `swell` but some thought to the dependencies is needed so it can be used effectively.

Swell is a Python package and is most easily installed using pip. The package can be cloned using:

```
git clone https://github.com/GEOS-ESM/swell swell
```

This will clone the develop branch into a directory called swell.

---
**WARNING:**
pip has to create directories where the package will be installed. Sometimes trouble can occur if default permissions are too strict. If these issues occur try setting `umask 022`:
---

To install to the directory where all Python packages are held use:
```
cd swell
pip install --user .
```

To specify the path where swell gets installed supply the prefix argument:
```
cd swell
pip install --prefix=/path/to/install/swell/ .
```

To make the software useable ensure `/path/to/install/swell/bin` is in the `$PATH`. Also ensure that `/path/to/install/swell/lib/python<version>/site-packages` is in the `$PYTHONPATH`, where `<version>` denotes the version of Python used for the install, e.g. `3.9`.
