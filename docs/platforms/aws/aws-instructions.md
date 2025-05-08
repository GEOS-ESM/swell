# Swell on AWS (`smce-gmao`)

## General platform description

We are running an instance of AWS ParallelCluster on AWS.
This is just a `slurm` cluster very similar to Discover, with a login node and a compute node pool.

The login node is always on and costs a fixed amount whether we use it or not.

Compute nodes only cost money when they are running jobs ($0.34/hour), and are destroyed when not in use.

There are no restrictions on network access.
Unlike Discover, both login and compute nodes can download from the open internet.
However, there is a small fee for network throughput to compute nodes --- $0.045/GB (because these nodes are on a private subnet that does internet requests through a NAT gateway) --- so avoid using compute nodes to download huge data files (>100 GB).
There is _no_ such fee for the login node (because it is on a public subnet that can talk directly to the internet gateway) so this is a perfectly fine place to do large downloads.

All storage (home and shared) should be available at the same file paths to both login and compute nodes.
The root file system (including home directories) is 100 GB total; there are no inode restrictions.
Try to avoid storing huge files on your home directory --- it's a shared resource.

Another 200 GB of storage (total) is available on the drive mounted at `/shared`.
This is a good place to put somewhat larger files that require more performant access.

Both the root volume (`/`) and `/shared` are pre-allocated storage (100 GB and 200 GB, respectively).
Whether we use 1% or 99% of that storage, the price is identical.

By contrast, `/efs` is slightly less performant pay-for-what-you-use storage.
Here, we pay $0.30/GB-month (for reference: $3600/TB-year) for storage, but that scales up or down by the hour depending on how much storage we use.
The maximum storage volume of `/efs` is theoretically ~8 EB (i.e.,8000 PB, or 8,000,000 TB; you will see this in the output of `df -h`), so this is practically unlimited storage...but again, pay-for-what-you-use, so don't go crazy.

**NOTE:** This AWS resource is here to be used; do not be intimidated by the storage or compute costs.
As long as you are reasonably prudent about storage (e.g., don't dump 100s of TB of output on EFS and leave them there for long stretches of time) and compute (e.g., don't accidentally leave compute nodes cycling a failed task for days at a time), cost shouldn't be a problem.
We also get cost alerts when we spike or drift well above an average.

Finally, remember that **labor costs money too**.
Your time is worth between $20-50/hour (depending on seniority), so if you spend an hour trying to save cloud compute costs, if you don't save at least ~$50 of compute costs (170 GB-months of storage; 150 hours of compute node runtime), _you are wasting money_.

## Cylc

The Swell AWS installation comes with a global installation of cylc.
You should be able to use it with no additional configuration (assuming `/usr/local/bin` is on your `PATH`).

The `cylc` configuration on AWS is basically identical to Discover.
Ensure the following are in your `~/.cylc/flow/global.cylc` file.

```
[scheduler]
  UTC mode = True
  process pool timeout = PT10M
  process pool size = 4

[platforms]
  [[aws]]
    job runner = slurm
    install target = localhost
    hosts = localhost
```

### (Optional) Install your own version of cylc

If you would like to install your own `cylc`, read on:

A very easy and convenient way to install `cylc` is using the [pixi package manager](https://pixi.sh/latest/):

1. Install `pixi` itself (per its instructions).
Note that this is a user-level install; you do not need sudo permissions.
Then, restart your shell (or log out and back in).

2. Install cylc with `pixi global install cylc-flow --expose cylc`.
This will make `cylc` available as a global standalone executable available everywhere (including Swell).

## Installing swell

1. Clone Swell: `git clone https://github.com/geos-esm/swell`

2. Enter the `swell` directory.

3. Activate Swell modules: `source /shared/swell-bundle`

4. Create a virtual environment:

    ```sh
    python -m venv .venv
    # ...or with uv:
    uv venv
    ```

5. Activate the virtual environment:

    ```sh
    source .venv/bin/activate
    ```

6. Install Swell dependencies:

    ```sh
    pip install -r requirements.txt -r requirements-aws.txt
    # ...or with uv:
    uv pip install -r requirements.txt -r requirements-aws.txt
    ```

7. Install Swell itself (note: `-e` means "editable" mode, so changes to the code will automatically be detected as Swell runs.):

    ```sh
    pip install -e .
    # ...or with uv
    uv pip install -e .
    ```

## Using Swell installations

1. Source swell modules: `source /shared/swell-bundle`.

2. Activate your Python virtual environment (from inside the Swell directory): `source .venv/bin/activate`
(If you are not in the Swell directory, just pass an absolute path: `source /path/to/your/swell/.venv/bin/activate`).

Note: Optionally, you can skip step 1 here by manually editing the `.venv/bin/activate` script to include the line from step 1 (`source /shared/swell-bundle`).
Then, all you have to do is run step 2.

## Known issues

### Issues with `uv` and `git-lfs` (e.g., for `eva`)

There is a known issue with `uv pip` and repositories that use git LFS (like eva).
See this for more details: https://github.com/astral-sh/uv/issues/3312

One solution is to configure LFS to force skipping smudge checks (though this may have the side effect of not downloading any LFS files at all).

```
git lfs install --force --skip-smudge
```

A better solution may be to skip smudge checks only for the uv cache:

1. Create a file called `~/.gitconfig-nolfs`.

    ```
    [filter "lfs"]
        clean = git-lfs clean -- %f
        smudge = git-lfs smudge --skip -- %f
        process = git-lfs filter-process --skip
        required = true
    ```

2. Add this to your `~/.gitconfig`.

    ```
    [includeIf "gitdir:~/.cache/uv/**"]
    path = ~/.gitconfig-nolfs.inc
    ```
