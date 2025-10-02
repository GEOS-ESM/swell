# Running comparison experiments within Swell

Swell currently supports comparing variational experiments.

Creating a comparison experiment within swell requires an override yaml with two experiments to be compared (default paths are not set automatically). These filepaths should point to the experiment.yaml for each suite.

```yaml
comparison_experiment_paths:
  - /path/to/experiment1/experiment.yaml
  - /path/to/experiment2/experiment.yaml
```
These experiments should have matching assimilation window parameters. By default in this suite, start and end cycle points are not specified, in which case Swell will parse the two experiments to find the matching cycle times between the two. Alternatively, start and end cycle points can be set manually.

The experiment can then be created using `swell create compare_variational_marine -o override.yaml` or `swell create compare_variational_atmosphere -o override`, depending on the type of experiments being compared. Launching the experiment will run tasks analyzing the jedi log and generating plots using Eva for increments. Comparison of the log analysis will be placed under the comparison suite's directory in a file named `jedi_log_comparison.txt`, while the eva plots will be located under the cycle directory for each cycle.
