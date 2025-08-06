# Swell on AWS (`smce-gmao`)

## General platform description

### Compute

We are running an instance of AWS ParallelCluster on AWS.
This is just a `slurm` cluster very similar to Discover, with a login node and a compute node pool.

The login node pool (3 nodes, assigned randomly; similar to Discover) is always on and costs a fixed amount whether we use it or not.
Each login node has 2 CPUs and 8 GB of RAM.

Compute nodes only cost money when they are running jobs and are destroyed when not in use.
We have several compute queues available, which can be viewed via `sinfo`.
Example output might look like this:

```
PARTITION    AVAIL  TIMELIMIT  NODES  STATE NODELIST
demand-8cpu*    up   infinite     19  idle~ demand-8cpu-dy-demand-8cpu-nodes-[2-20]
demand-8cpu*    up   infinite      1    mix demand-8cpu-dy-demand-8cpu-nodes-1
demand-16cpu    up   infinite     20  idle~ demand-16cpu-dy-demand-16cpu-nodes-[1-20]
spot-8cpu       up   infinite     20  idle~ spot-8cpu-dy-spot-8cpu-nodes-[1-20]
spot-16cpu      up   infinite     20  idle~ spot-16cpu-dy-spot-16cpu-nodes-[1-20]
```

The `demand` nodes are reserved and guaranteed to be available for the entire length of the job, but are also somewhat more expensive.
The `spot` nodes are 3-4x cheaper per CPU-hour, but may fail unexpectedly (when other AWS users outbid us for them).
For smaller, lower-priority, and failure-tolerant jobs, I recommend using the spot partitions (e.g., `sbatch -p spot-8cpu`) to save some costs...but if you need the `demand` nodes, use them!

All nodes are in the [`c7i-flex` class](https://aws.amazon.com/ec2/instance-types/c7i/) --- x86_64, custom 4th Generation Intel Xeon Scalable processors ("Sapphire Rapids")

Nodes take around 7 minutes to launch from idle (shut down) state to active.
After a job completes or fails, nodes will persist for 10 minutes before shutting down.
Jobs submitted within that 10 minute window should start almost instantly.
This should make it _much_ easier to run multi-job workflows (like Swell) and to debug issues.

### Networking

There are **no restrictions on network access**.
Unlike Discover, both login and compute nodes can download from the open internet at no cost.
Some network instability may be possible due to cost-saving network configurations.

### Storage

All storage locations should be available at the same file paths to both login and compute nodes.
None of the storage locations have inode limits, but some storage types do have (small) costs per read/write operation, so pay some attention to this.

* Home directories are mounted on AWS Elastic File System (EFS). This is a pay-for-what-you-use storage device with no practical upper limit. The price is $0.30/GB-month ($300/TB-month), plus a $0.03/GB charge for reads and a $0.06/GB charge for writes. Performance characteristics are average; decent, but not amazing and possibly inconsistent, throughput and latency.
* There is also a shared `/efs` folder with the same pricing and performance characteristics.
* `/fast1` is pre-allocated SSD storage, fixed (for now) to 200 GB. We pay for 200 GB whether this is 0% or 100% full. Note that although this is SSD, it is mounted to compute nodes via NFS (over the network), so the performance will likely be worse than advertised. There is no cost to read or write operations.
* `/slow1` is pre-allocated HDD (spinning disk) storage, fixed to 1 TB (as above, but much cheaper and with worse performance). Since it's pre-allocated, this is a great place to store infrequently accessed data. Again, no cost to read or write operations.
* `/s3` is a mounted S3 bucket. Like EFS, this is pay-for-what-you-use and infinitely expandable, but significantly cheaper -- $0.023/GB-month ($23/TB-month). However, this is not quite a true POSIX file system. It should work great for reading and writing files, but not very well for editing files. There is also a small fee for each read, write, and delete operation (~$0.005 per 1000 ops...but it can add up for certain access patterns).

### Final thoughts

This AWS resource is here to be used; do not be intimidated by the storage or compute costs.
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
