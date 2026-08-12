- 1. Getting Started

  - [What Is Swell?](README.md)
  - [Core Concepts and Terminology](introduction/core_concepts_and_terminology.md) — _No documentation yet_
  - Prerequisites and Supported Platforms
    - [Prerequisites](introduction/prerequisites.md) — _No documentation yet_
    - [Supported Platforms](installation_and_setup/platforms/README.md)
    - [Project Requirements and Goals](introduction/requirements.md)
  - Installation and Setup
    - [Installing Swell](installation_and_setup/installing_swell.md)
    - [Configuring Cylc](installation_and_setup/configuring_cylc.md)
    - Discover
      - [Installing Swell on SLES15](installation_and_setup/platforms/discover/installing_swell_discover_sles15.md)
      - [Installing Swell with `uv` and `venv`](installation_and_setup/platforms/discover/installing_swell_uv_venv.md)
      - [Installing Swell Without Internet Access](installation_and_setup/platforms/discover/installing_swell_uv_offline.md)
      - [Installing Swell in an Interactive C Shell](installation_and_setup/platforms/discover/installing_swell_csh_interactive.md)
      - [Configuring Cylc on Discover](installation_and_setup/platforms/discover/configuring_cylc_discover.md)
  - [QuickStart](introduction/quickstart.md) — _No documentation yet_

- 2. Running Experiments

  - [Choosing a Workflow](running_an_experiment/choosing_a_workflow.md) — _No documentation yet_
  - Understanding Configuration
    - [Current Configuration and Experiment Overview](practical_examples/README.md)
    - [SLURM Configuration](configuration_reference/slurm_configuration.md)
  - [Creating an Experiment](running_an_experiment/creating_an_experiment.md)
  - [Modifying an Experiment with Overrides](practical_examples/README.md?id=using-defaults-with-overrides)
  - [Generated Directory Layout](practical_examples/README.md?id=experiment-directory)
  - [Launching an Experiment](running_an_experiment/launching_an_experiment.md)
  - Monitoring, Restarting, and Stopping
    - [Monitoring an Experiment](running_an_experiment/monitoring_an_experiment.md)
    - [Stopping Jobs](running_an_experiment/launching_an_experiment.md?id=stopping-jobs)
  - Logs and Output Products
    - [Finding Task Logs](running_an_experiment/monitoring_an_experiment.md?id=when-a-task-fails)
  - [Manually Running Tasks](running_an_experiment/manually_running_tasks.md)
  - [Troubleshooting](running_an_experiment/troubleshooting.md) — _No documentation yet_

- 3. Workflow Guides

  - Ocean and Sea-Ice DA
    - [3DVAR Marine](practical_examples/soca/3dvar_marine.md)
    - [3DVAR Marine Cycle Tier 2](practical_examples/soca/3dvar_marine_cycle_tier2.md)
    - [3DFGAT Marine Cycle](practical_examples/soca/3dfgat_marine_cycle.md)
  - [Atmospheric (Weather) DA](practical_examples/atmosphere/README.md) — _No documentation yet_
  - [Atmospheric Composition DA](practical_examples/geos_cf/README.md)
    - [HofX GEOS-CF](practical_examples/geos_cf/hofx_cf.md)
    - [3DVAR GEOS-CF](practical_examples/geos_cf/3dvar_cf.md)
    - [3DVAR GEOS-CF Cycle](practical_examples/geos_cf/3dvar_cf_cycle.md)
  - Background Ingestion, Observation Ingestion, and Conversion
    - [Storing Observations and Backgrounds in R2D2](practical_examples/r2d2/r2d2_ingest.md)
  - Comparison and Evaluation
    - [Comparing Experiment Outputs](practical_examples/generic_suites/comparison_workflows.md)

- 4. Data and R2D2

  - [R2D2 Concepts](introduction/r2d2_overview.md)
  - [Credentials](configuration_reference/r2d2_v3_credentials.md)
  - [Servers and Datastores](installation_and_setup/configuring_aws_server.md)
  - [How Experiments Store and Retrieve Data](introduction/r2d2_overview.md?id=how-swell-uses-r2d2)

- 5. Extending Swell

  - [Adding a Task](extending_swell/adding_a_suite.md?id=writing-tasks)
  - [Adding a Suite/Workflow](extending_swell/adding_a_suite.md)
  - [Adding Model Interfaces](extending_swell/adding_model_interfaces.md) — _No documentation yet_
  - [Adding Observations and Converters](extending_swell/adding_observations_and_converters.md) — _No documentation yet_
  - [Adding Platform Support](extending_swell/adding_platform_support.md) — _No documentation yet_

- 6. Testing and Contributing

  - [Development Setup](testing_and_contributing/development_setup.md) — _No documentation yet_
  - [Code Tests](testing_and_contributing/code_tests.md)
  - [Tier 1 and Tier 2 Suite Tests](testing_and_contributing/suite_tests.md)
  - [Documentation](testing_and_contributing/editing_docs.md)
  - [Contribution Guidelines](testing_and_contributing/contribution_guidelines.md) — _No documentation yet_

- 7. Additional Resources

  - [Useful Links](additional_resources/useful_links.md)
  - Physical Model Settings
    - [CICE6](configuration_reference/model_configurations/cice6.md)
    - [MOM6](configuration_reference/model_configurations/mom6.md)
    - [History Outputs](configuration_reference/model_configurations/history_outputs.md)
