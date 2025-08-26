# Running comparison workflows in Swell

Comparison workflows are run on two experiments to compare their output. Current experiments available for comparison include `3dvar` and `3dvar_atmos`

### Example workflow: 3dvar

With two completed experiments, create a comparison workflow suite using an override yaml. This should contain the paths to the two experiments to be compared:

```yaml
comparison_experiment_paths:
  - /path/to/experiment1/experiment.yaml
  - /path/to/experiment2/experiment.yaml
```

This will create a workflow properly configured to run tests on the two experiments. Launching the comparison experiment will run three tasks. One will generate plots using eva consisting of plots of the jedi output, and all increments avalailable for that suite. Each plot will contain the output from experiment 1, experiment 2, and the relative difference between the two. The other two tasks parse the jedi log output and retrieve information such as the residual norms.

The output from these tasks are placed the the directory of the comparison suite. For the jedi log comparison, the information will be placed under `experiment_root/comparison_tests/`

Comparison increment and jedi output plots are place under the cycle directory:
`experiment_root/run/<cycle_time>/<model>/eva`

