# Swell configuration in AWS (`smce-gmao`)

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
