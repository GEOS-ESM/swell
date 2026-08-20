# Running a Swell Experiment

Running a Swell experiment includes several steps:
- Choosing a workflow that matches your scientific goal
- Configure and create the experiment
- Launch the experiment
- Monitor its tasks and inspect its logs and outputs

**Creating** and **launching** are separate operations. `swell create` resolves the configuration and
generates an experiment directory, but it does not run the workflow. `swell launch` starts the experiment.

This section covers all the steps for running and monitoring a Swell experiment.
Read the pages in the following order:

1. [Choosing a Workflow](choosing_a_workflow.md) explains which suite to use based on your goal i.e., for analysis,
   observation evaluation, ingestion, conversion, or comparison.
2. [Understanding Configuration](understanding_configuration.md) explains defaults, interactive
   configuration, override files, platform selection, and SLURM settings.
3. [Creating an Experiment](creating_an_experiment.md) shows how to run `swell create` and describes
   what Swell generates.
4. [Generated Directory Layout](experiment_directory.md) identifies the files to review before
   launch and the directories produced while the workflow runs.
5. [Launching an Experiment](launching_an_experiment.md) starts the generated workflow with Cylc.
6. [Monitoring, Restarting, and Stopping](monitoring_an_experiment.md) covers routine workflow
   control and recovery from a failed or interrupted run.
7. [Logs and Output Products](logs_and_output_products.md) explains where to find Cylc task logs,
   JEDI application logs, generated configuration, and scientific results.
8. [Manually Running Tasks](manually_running_tasks.md) describes an advanced development and
   debugging workflow outside Cylc.
Workflow-specific inputs and expected results belong in the
[practical examples](../practical_examples/README.md) (TODO:update this link). This section describes the common lifecycle
shared by Swell workflows.

Start by [choosing a workflow](choosing_a_workflow.md).
