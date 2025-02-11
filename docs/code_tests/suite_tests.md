# Suite tests

Before opening a pull request, we highly recommend running not only the Swell [Code tests](code_tests/code_tests.md) but also some more advanced tests of Swell functionality that confirm that common suites will run successfully.
These tests take significantly longer and require significantly more computational resources to run; the only reasonable place to run these is on a compute node on NCCS Discover.

Tier 1 tests are relatively faster and test more basic functionality on a small number of compute nodes.
These should be run before submitting any non-trivial pull request.

Tier 2 tests are significantly slower and more computationally intensive.
These should be run after major changes to Swell code and functionality.

## Tier 1 tests

The recommended way to run these on NCCS Discover is as follows:

1. (Optional, but recommended) Create a file called `~/.swell/swell-test.yaml`.
Inside this file, add a line like (replacing with a real file path):
    ```yaml
    test_root: /path/to/tier1/test/outputs
    ```
This sets the root directory where tier1 test outputs will be stored.
(If unset, the test function will create a temporary directory that is deleted by the operating system when the `sbatch` job concludes.
You can still run the tests without this, but you won't be able to study the outputs.)
Optionally, you can also add additional test overrides to this script; these will be used as overrides to the Swell configuration.
One recommended override, per the example below, is to request a local copy of `GEOS_mksi`, since compute nodes will not be able to clone the repo from GitHub (per the default Swell behavior)
    ```yaml
    test_root: ~/projects/SwellExperiments/tier1
    override:
      models:
        geos_atmosphere:
          observing_system_records_mksi_path: "~/projects/GEOS_mksi"
    ```

2. Set up your compute SWELL environment interactively (following the [Platform specific instructions](platforms/platforms.md) for your system).
    - Confirm that you are running the correct version of Swell with `which swell`.
    - Confirm that swell itself will run by just running `swell` (and make sure the command prints out instructions but throws no errors).

3. Submit a single Swell suite on a compute node as follows.
    ```sh
    sbatch [...sbatch options here...] -- swell t1test <suite>
    # For example, to use account g0613, 40 min, milan nodes,
    # and logging to the .logs/ folder:
    mkdir .logs
    sbatch -A g0613 -t 40 -C mil -o .logs/%j -- swell t1test <suite>
    ```
This works because, unless otherwise specified, `sbatch` automatically inherits all current environment variables, which you have already configured in step 2 above.
If you prefer, you can create a dedicated `sbatch` script to wrap the `swell t1test ...` command, to be extra sure that the environment is exactly as it should be.
By default, tier tests will be run on the `nccs_discover_sles15` platform, alternative platforms can be specified with the `-p` flag, similar to other swell commands.

4. Repeat (2) for other tests you would like to run. Currently, we recommend running the following tests:
    - `3dvar`
    - `hofx`
    - `ufo_testing`

5. Check the slurm logs to make sure that all tests have completed.
Debug as necessary.

## Tier 2 tests

Swell tier2 tests are run in a similar way to tier1 tests. Overrides from ~/.swell/swell-test.yaml are read and used in the test. Tier 2 tests generally involve building JEDI before running each test suite, a time and computationally expensive process. This involves cloning the Git repositories for JEDI, which must be done on a Discover login node, as compute nodes do not have internet access. In addition, access to private  Git repositories necessary to build JEDI requires the user to be part of the JDSCA-internal organization on Github. A `~/.git-credentials` must be created containing Github access token information (see [jedi bundle documentation](https://github.com/GEOS-ESM/jedi_bundle/blob/develop/docs/git_credentials.md))

The recommended way to run tier 2 tests on NCCS Discover is as follows:

1. (Optional but recommended), create a file called `~/.swell/swell-test.yaml`.
Like tier 1 tests, setting the root directory controls where test outputs will be stored (replacing with a real file path):

    ```yaml
    test_root: /path/to/tier1/test/outputs
    ```
(If unset, the test function will create a temporary directory that is deleted by the operating system when the `sbatch` job concludes. 
You can still run the tests without this, but you won't be able to study the outputs.) Other overrides will be passed to the test.
By default, tier 2 tests will build JEDI at the beginning of the job, unless a path to an existing JEDI build is specified in the user's `~/.swell/swell-test.yaml`, using the lines
    ```yaml
    jedi_build_method: use_existing
    existing_jedi_build_directory: /path/to/jedi/build/directory
    exising_jedi_source_directory: /path/to/jedi/source/directory
    ```
2. Ensure your SWELL interactive enviroment is set up correctly (see step 2 under tier 2 tests)

3. To start a tier 2 test on a login node (This is needed for internet access for cloning jedi repositories, please do this sparingly to conserve NCCS resources. If you have a sucessful JEDI build and want to test it further, use the overrides in the `~/.swell/swell-test.yaml` to avoid having to build JEDI and use login nodes)
    ```sh
    swell t2test <suite> -p <platform>
    # The platform is specified with -p, this will default to nccs_discover_sles15.
    ```
This works because, unless otherwise specified, `sbatch` automatically inherits all current environment variables, which you have already configured in step 2 above.

4. Repeat (2) for other tests you would like to run. Currently, we recommend running the following tests:
    - `3dvar`
    - `hofx`
    - `ufo_testing`
    - `convert_ncdiags`
    - `3dfgat_atmos`
    - `build_jedi`
