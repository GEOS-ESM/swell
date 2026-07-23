# Installing swell in pip interactive mode on csh

This is an alternative method to installing swell using `pip`, without requiring `uv`. This method is more likely to work for users who have `csh` as their shell.

### Preliminary steps (need only be done once)

1) Link cache directory to nobackup (Recommended):

```csh
mv ~/.cache $NOBACKUP/.cache
```

and then create a symlink to your home:

```csh
ln -s $NOBACKUP/.cache ~/.cache
```

2) Create an alias to load spack-stack modules in `~/.cshrc`:

```csh
alias mod_swell 'module purge; source /discover/nobackup/projects/gmao/advda/swell/jedi_modules/spackstack_1.9_intel'
```

After creating this alias, reload your shell or run `source ~/.cshrc` for it to be available.

### First time installing swell
Clone Swell to wherever you want it to live, for example:
```csh
cd $NOBACKUP
mkdir swell-project
cd swell-project
git clone https://github.com/GEOS-ESM/swell.git swell-develop
```

1) Switch to your folder where Swell is cloned: `cd $NOBACKUP/swell-project/swell-develop`.
2) (Optional) Checkout a new branch in a new git worktree: e.g., `git worktree add ../mybranch -b mybranch` will create a folder specifically for the `mybranch` branch (to create a workspace for an existing branch, leave out the `-b` flag).
3) (Optional) `cd ../mybranch'
4) Load all the modules that Swell needs: `mod_swell` (this is the `csh` alias function created in the preliminary steps)
5) Create a Python virtual environment: `python3 -m venv .venv`
6) Activate the virtual environment: `source .venv/bin/activate.csh`
7) Install swell in editable mode: `pip install -e .` (note: make sure you run this while the `venv` is active)

9) Now, work on SWELL. Any changes you make to the SWELL source code will be automatically applied to the install (because it's an editable install); no need to manually reinstall.

#### Resuming work from a previous SWELL installation:
1) Switch to your folder where SWELL is installed: `cd $NOBACKUP/swell-project/mybranch`.
2) Load all the modules that SWELL needs: `mod_swell`
3) Activate the virtual environment: `source .venv/bin/activate.csh`. You may also use the full path: `source $NOBACKUP/swell-project/mybranch/.venv/bin/activate.csh`. You may consider adding this command to your `mod_swell` alias for future use.
4) SWELL is ready! See [examples here](../../../practical_examples/README.md) on how to run SWELL.
