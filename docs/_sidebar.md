- Introduction

  - [What Is Swell?](README.md)
  - Concepts and Architecture
  - [R2D2 Overview](introduction/r2d2_overview.md)
  - [Requirements](introduction/requirements.md)

- Installation and Setup

  - [Installing Swell](installation_and_setup/installing_swell.md)
  - [Configuring Cylc](installation_and_setup/configuring_cylc.md)
  - [Platform-Specific Setup](installation_and_setup/platforms/README.md)
    - **Discover**
      - [Installing Swell on SLES15](installation_and_setup/platforms/discover/installing_swell_discover_sles15.md)
      - [Installing Swell with `uv` and `venv`](installation_and_setup/platforms/discover/installing_swell_uv_venv.md)
      - [Installing Swell Without Internet Access](installation_and_setup/platforms/discover/installing_swell_uv_offline.md)
      - [Installing Swell in an Interactive C Shell](installation_and_setup/platforms/discover/installing_swell_csh_interactive.md)
      - [Configuring Cylc on Discover](installation_and_setup/platforms/discover/configuring_cylc_discover.md)
    - [Configuring an AWS Server](installation_and_setup/configuring_aws_server.md)

- Running an Experiment

  - [Creating an Experiment](running_an_experiment/creating_an_experiment.md)
  - [Launching an Experiment](running_an_experiment/launching_an_experiment.md)
  - [Monitoring an Experiment](running_an_experiment/monitoring_an_experiment.md)
  - [Manually Running Tasks](running_an_experiment/manually_running_tasks.md)

- Practical Examples

  - [Examples Overview](practical_examples/README.md)
  - **SOCA Workflows**
    - [3DVAR Marine](practical_examples/soca/3dvar_marine.md)
    - [3DVAR Marine Cycle Tier 2](practical_examples/soca/3dvar_marine_cycle_tier2.md)
    - [3DFGAT Marine Cycle](practical_examples/soca/3dfgat_marine_cycle.md)
  - **R2D2 Workflows**
    - [Storing Observations in R2D2](practical_examples/r2d2/r2d2_ingest.md)
  - **Generic Swell Suites**
    - [Comparing Experiment Outputs](practical_examples/generic_suites/comparison_workflows.md)

- Configuration Reference

  - **Model Configurations**
    - [CICE6](configuration_reference/model_configurations/cice6.md)
    - [MOM6](configuration_reference/model_configurations/mom6.md)
    - [History Outputs](configuration_reference/model_configurations/history_outputs.md)
  - [Observation Configuration](configuration_reference/observation_configuration.md)
  - [R2D2 Credentials](configuration_reference/r2d2_v3_credentials.md)
  - [SLURM Configuration](configuration_reference/slurm_configuration.md)

- Extending Swell

  - [Adding a Suite](extending_swell/adding_a_suite.md)
  - Adding Tasks
  - Developing New Workflows

- Testing and Contributing

  - [Code Tests](testing_and_contributing/code_tests.md)
  - [Suite Tests](testing_and_contributing/suite_tests.md)
  - [Editing the Documentation](testing_and_contributing/editing_docs.md)
  - Contribution Guidelines

- Additional Resources

  - [Useful Links](additional_resources/useful_links.md)
