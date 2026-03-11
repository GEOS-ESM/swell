# Installing SWELL with `uv` without internet access
This page is only for the users **who have no outranet on Discover**. We show here:
- How to install uv and SWELL using offline packages;
- How to synchronize your code between Discover and GitHub.

#### Install uv
1. get the installer `wget -c https://astral.sh/uv/install.sh`
2. From `install.sh`, check the version `APP_VERSION`, and download the file `uv-x86_64-unknown-linux-gnu.tar.gz` with the corresponding `APP_VERSION` from `https://github.com/astral-sh/uv/releases`
3. Upload both `install.sh` and `uv-x86_64-unknown-linux-gnu.tar.gz` to a directory under discover, `[discover_path]`
4. Revise the installer script: under function `downloader`, replace the line `curl -sSfL "$1" -o "$2"` with `cp "$1" "$2"`.
5. Now install the uv. Assume that you default shell is `bash`, run the following
```bash
    INSTALLER_DOWNLOAD_URL=[discover_path] ./install.sh
```
This will finish the uv installation. Then follow the SWELL documentation to finish other uv settings

#### Install SWELL
We will download all the required packages on local with the corresponding python version `[python_version]`, and then install those packages on Discover.
1. Find the python version used by the JEDI module. On Discover, Load the `mod_swell` (see instructions [here](platforms/discover/installing_swell_uv_venv.md)). Then get the python version `[python_version]` by running `python --version`.
2. On a `x86_64` Linux machine (e.g., an AWS ec2 instance with Intel or AMD CPU, and with os=`sles15`), get all the required offline installation packages. 
```bash
    #install uv first

    git clone https://github.com/GEOS-ESM/swell
    cd swell    # your SWELL repo

    #assume you now have installed uv 
    uv venv --python=python[python3_version]  # e.g., uv venv --python=python3.11.11
    source .venv/bin/activate
    python --version # check if this gives the same [python_version] as on Discover

    uv pip install pip
    which pip3  # make sure that the path of pip3 is the one under your venv

    mkdir ../downloaded  # where offline packages will be saved to
    pip3 download "setuptools>=68.0.0" -d ../downloaded
    pip3 download "wheel>=0.46.3" -d ../downloaded
    pip3 download . -d ../downloaded
```
3. Upload the packages under `downloaded` to a Discover directory, `[discover_offline_pkg_path]`
4. On a milan node from Discover, install the packages by
```bash
    # get into the swell directory

    mod_swell
    uv venv
    source .venv/bin/activate
    which python  # ensure python points to the python under your venv
    ml purge
    python -m ensurepip --upgrade  # this installed pip & setuptools
    which pip3    # ensure pip3 points to the same dir as python under your venv
    # (optional_start) run these if pip3 does not points to the one under your venv
    deactivate
    source .venv/bin/activate
    which pip3    # ensure pip3 points to the same dir as python under your venv
    # (optional_end)
```
5. Install SWELL in editable mode 
```
    deactivate 
    mod_swell
    source .venv/bin/activate
    python -m pip install --no-index --find-links=[discover_offline_pkg_path] -e .
```
#### Reuse SWELL and launch SWELL jobs
Log into a **Milan** node on Discover, run 
```
mod_swell
cd swell  # your SWELL repo
source .venv/bin/activate
```
Then use `swell create/launch [...]` to create/launch your SWELL jobs.

#### Code synchronization when outranet is disabled on Discover
The idea is to use the repo at local as a middle man, so that you can 
`Discover ----> local ----> Github`, or `Github ----> local ---->  Discover`

1. `git clone` the repo from the Github, and then tar the directory and transfer it to Discover under directory `[discover_path]` 
2. On your local, do the following in a new directory
```bash
    git init
    git remote add discover USER_NAME@discover.nccs.nasa.gov:[discover_path]
    git pull discover [branch_name]
    # or create local branches remapped to your desired remote branch
```
3. **Push codes from Discover to Github**
	1. on local, create a local branch mapped to your remote branch
	2. on local, at the mapped local branch: `git pull discover [branch_name]`
	3. on local, at the mapped local branch: `git push [github_remote] [branch_name]`
4. **Fetch codes from Github to Discover**
	1. on local, at the mapped local branch: `git pull [github_remote] [branch_name]`
	2. on Discover, **ensure you are at a branch other than `[branch_name]`**
	3. on local, at the mapped local branch: `git push discover [branch_name]`
	4. Check: on Discover, branch `[branch_name]` should now be synchronized as the local `[branch_name]`

**In the worst scenario**, you can always do the dumb way: tar your repo from Discover, download to local, and then untar and sync. This approach with the opposite direction also works.
