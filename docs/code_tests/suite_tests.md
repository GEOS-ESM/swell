# Suite tests

Before opening a pull request, we highly recommend running not only the Swell [Code tests](code_tests/code_tests.md) but also some more advanced tests of Swell functionality that confirm that common suites will run successfully.
These tests take significantly longer and require significantly more computational resources to run; the only reasonable place to run these is on a compute node on NCCS Discover.

Tier 1 tests are relatively faster and test more basic functionality on a small number of compute nodes.
These should be run before submitting any non-trivial pull request.

Tier 2 tests are significantly slower and more computationally intensive.
These should be run after major changes to Swell code and functionality.

## Tier 1 tests

The recommended way to run these on NCCS Discover is as follows:

1. Set up your compute SWELL environment interactively (following the [Platform specific instructions](platforms/platforms.md) for your system).
    - Confirm that you are running the correct version of Swell with `which swell`.
    - Confirm that swell itself will run by just running `swell` (and make sure the command prints out instructions but throws no errors).

2. Submit a single Swell suite on a compute node as follows:

    ```sh
    sbatch [...sbatch options here...] -- swell t1test <suite>
    # For example, to use account g0613, 40 min, milan nodes,
    # and logging to the .logs/ folder:
    mkdir .logs
    sbatch -A g0613 -t 40 -C mil -o .logs/ -- swell t1test <suite>
    ```

3. Repeat (2) for other tests you would like to run. Currently, we recommend running the following tests:
    - `3dvar`
    - `hofx`
    - `ufo_testing`

4. Check the slurm logs to make sure that all tests have completed.
Debug as necessary.

## Tier 2 tests

Coming soon!
