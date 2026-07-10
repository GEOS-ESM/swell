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
