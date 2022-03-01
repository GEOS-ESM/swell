# Installing swell

Swell is a Python package and is most easily installed using pip. The package can be cloned using:

```
git clone https://github.com//GEOS-ESM/swell
```

This will clone the develop branch into a directory called swell.

---
**WARNING**

pip has to create directories where the package will be installed. Sometimes trouble can occur if
default permissions are too strict. If these issues occur try setting:

```
umask 022
```

---

On systems where sudo access is not permitted swell can be installed using:
```
cd swell
pip install --user .
```

To specify the path where swell gets installed you can do:
```
cd swell
pip install --prefix=/path/to/install .
```
