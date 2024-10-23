# Installing SWELL using `uv` and `venv`

This is an alternative approach to using `LMOD` and `py_lmod_installer` tool. This is more geared towards Swell Developers but users might find this approach easier to work with.

#### Preliminary steps:
1) Install `uv` using instructions [here](https://github.com/astral-sh/uv?tab=readme-ov-file#installation). This will install a single executable to `$HOME` directory and needs to be done once; no modules required. Note that `uv` aggressively performs caching of packages it installs to `~/.cache/uv`. To avoid quickly exhausting your home directory, move your `.cache` to your `$NOBACKUP` via:

```bash
mv ~/.cache $NOBACKUP/.cache
```
and then create a symlink in your `$HOME`:
```bash
ln -s $NOBACKUP/.cache ~/.cache
```

2) Create a `bash` function called `mod_swell` that detects which OS the user is on (SLES12 or SLES15) and loads JEDI modules accordingly:
```bash
mod_swell() {
  module purge
  KERNEL_VERSION=$(uname -r)
  if [[ $KERNEL_VERSION =~ "4.12" ]]; then
    source /discover/nobackup/projects/gmao/advda/swell/jedi_modules/modules-intel
  elif [[ $KERNEL_VERSION =~ "5.14" ]]; then
    source /discover/nobackup/projects/gmao/advda/swell/jedi_modules/modules-intel-sles15
  else
    echo "No matching platform for kernel version: $KERNEL_VERSION"
  fi
}
```

This can be put in `~/.bashrc` to ensure it is always active every time the user logins to Discover or in an alternate location, such as `~/.bash_functions` but the user needs to activate these functions via `source ~/.bash_functions`.

3) Now clone Swell to wherever you want to live, for example:

```bash
cd $NOBACKUP
mkdir swell-project
git clone git@github.com:geos-esm/swell swell-develop
```

####  First time installing SWELL:
1) Switch to your folder where SWELL is cloned: `cd $NOBACKUP/swell-project/swell-develop`.
2) (Optional) Checkout a new branch in a new git worktree: e.g., `git worktree add ../mybranch -b mybranch` will create a folder specifically for the `mybranch` branch.
3) (Optional) `cd ../mybranch`
4) Load all the modules that SWELL needs: `mod_swell` (this is the `bash` function created in the preliminary steps)
5) Create a Python virtual environment: `uv venv`
6) Install SWELL dependencies `uv pip install -r requirements.txt`
7) Activate the virtual environment: `source .venv/bin/activate`
8) Install SWELL in editable mode: `python -m pip install -e`. (note: make sure you run this while the `venv` is active)
9) Now, work on SWELL. Any changes you make to the SWELL source code will be automatically applied to the install (because it's an editable install); no need to manually reinstall.

#### Resuming work from a previous SWELL installation:
1) Switch to your folder where SWELL is installed: `cd $NOBACKUP/swell-project/mybranch`.
2) Load all the modules that SWELL needs: `mod_swell`
3) Activate the virtual environment: `source .venv/bin/activate`. You may also use the full path: `source $NOBACKUP/swell-project/mybranch/.venv/bin/activate`
4) SWELL is ready! See [examples here](../../examples/description.md) on how to run SWELL.
