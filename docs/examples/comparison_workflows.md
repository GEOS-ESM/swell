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

## Comparing IODA observations
The task `CompareIodaObservations` compares IODA files between experiments by checking for equality in standard IODA fields for simulated variables, including:

```
EffectiveError0
EffectiveError1
EffectiveQC0
EffectiveQC1
ObsBias0
ObsBias1
ObsValue
PreQC
hofx
hofx0,
hofx1
oman
ombg
```

Which variables are compared depends on the parameter `ioda_fields_for_comparison`. By default, `hofx` will be compared for hofx experiments, and `hofx0` and `hofx1` for variational and fgat suites. If a mismatch in data field length or average is detected, this task will fail.

The `CleanCycle` task may clear observation files depending on the setting for `clean_patterns` in `experiment.yaml`. To use this task, ensure that `clean_patterns` is set correctly in the comparison experiments.

## Comparing Increment files
`CompareIncrement` compares increment values between experiments. By default, `geos_atmosphere` suites will compare `Salt, Temp, and ave_ssh`, `geos_atmosphere` will compare `ps, ts, ua, va, t, q`, and `geos_cf` suites compare `NO2`. Data fields will be checked to ensure they share the same size, and an average will be taken to check for equality 


The `CleanCycle` task may clear observation files depending on the setting for `clean_patterns` in `
experiment.yaml`. To use this task, ensure that `clean_patterns` is set correctly in the comparison
experiments.
