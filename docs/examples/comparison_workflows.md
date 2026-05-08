# Running comparison experiments within Swell

Swell currently supports comparing variational experiments.

Creating a comparison experiment within swell requires an override yaml with two experiments to be compared (default paths are not set automatically). These filepaths should point to the experiment.yaml for each suite.

```yaml
comparison_experiment_paths:
  - /path/to/experiment1/experiment.yaml
  - /path/to/experiment2/experiment.yaml
```

Filepaths are assigned tags depending on order, which will be used to distinguish them in the task output plots and text. By default, the filepath in the first position will be referred to as `CTL` for control, and the path in the second position will be `EXP` for experiment. Users can select their own tags by specifying `comparison_experiment_paths` as a dictionary, for example:

```yaml
comparison_experiment_paths:
  test1: /path/to/experiment1/experiment.yaml
  test2: /path/to/experiment2/experiment.yaml
```

These experiments should have matching assimilation window parameters. By default in this suite, start and end cycle points are not specified, in which case Swell will parse the two experiments to find the matching cycle times between the two. Alternatively, start and end cycle points can be set manually.

The experiment can then be created using `swell create compare_variational_marine -o override.yaml` or `swell create compare_variational_atmosphere -o override`, depending on the type of experiments being compared. Launching the experiment will run tasks analyzing the jedi log and generating plots using Eva for increments. Comparison of the log analysis will be placed under the comparison suite's directory in a file named `jedi_log_comparison.txt`, while the eva plots will be located under the cycle directory for each cycle.

## Comparing JEDI builds

This section describes how to run `ctests` on JEDI builds. The task `RunJediCtests` can be run in `build_jedi` experiments run by swell to output the results to a text file. `ctests` will be run for bundles specified in `bundles_to_run_ctests`. This field defaults to `fv3-jedi`, but any bundle with ctests can be run by this task. The output of the `ctest` execution is sent to `<experiment_path>/ctests/ctest_results-<bundle>.txt`


The `compare_jedi` suite checks the ctest results to ensure the two `build_jedi` experiments listed under `comparison_experiment_paths` pass the same ctests. The `bundles_to_run_ctests` key is also used by the `compare_jedi` suite to specify which bundles should be compared. The `compare_jedi` suite assumes that the task `RunJediCtests` has been run in the `build_jedi` experiments listed under `comparison_experiment_paths`. The task `CompareJediCtests` parses the output to figure out which tests fail for both experiments (the assumption is that some tests will always fail for most bundles, so the condition for zero-diff is ensuring the same tasks fail for both builds). If a mismatch in passed tests is detected, this task generates an error. The log output of this task lists the failed tasks for the two suites, and displays if any pass for one that is not passed for the other. For example, the output for comparing `fv3-jedi`:

```
fv3-jedi                               CTL   EXP
fv3jedi_staticb_nicas_gfs              Fail  Fail
fv3jedi_hofx_nomodel_abi_radii         Fail  Fail
fv3jedi_staticb_split_nicas_gfs        Fail  Fail
fv3jedi_hyb                            Fail  Fail
fv3jedi_staticb_dirac_local_gfs_12pe   Fail  Fail
fv3jedi_staticb_cor_geos               Fail  Fail
fv3jedi_staticb_dirac_local_gfs_6pe    Fail  Fail
fv3jedi_staticb_nicas_geos             Fail  Fail
fv3jedi_staticb_dirac_global_gfs_6pe   Fail  Fail
fv3jedi_staticb_dirac_global_gfs_12pe  Fail  Fail
```
