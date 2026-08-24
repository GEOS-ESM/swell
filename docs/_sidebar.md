- 1. Getting Started

  - [What Is Swell?](/)
  - [Core Concepts and Terminology](/introduction/core_concepts_and_terminology.md)
  - [Task Glossary](/introduction/task_glossary.md)
  - Prerequisites and Supported Platforms
    - [Prerequisites](/introduction/prerequisites.md)
    - [Supported Platforms](/installation_and_setup/platforms/README.md)
  - Installation and Setup
    - [Installing Swell](/installation_and_setup/installing_swell.md)
    - [Configuring Cylc](/installation_and_setup/configuring_cylc.md)
    - Discover
      - [Installing Swell on SLES15](/installation_and_setup/platforms/discover/installing_swell_discover_sles15.md)
      - [Installing Swell with `uv` and `venv`](/installation_and_setup/platforms/discover/installing_swell_uv_venv.md)
      - [Installing Swell Without Internet Access](/installation_and_setup/platforms/discover/installing_swell_uv_offline.md)
      - [Installing Swell in an Interactive C Shell](/installation_and_setup/platforms/discover/installing_swell_csh_interactive.md)
      - [Configuring Cylc on Discover](/installation_and_setup/platforms/discover/configuring_cylc_discover.md)
  - [QuickStart](/introduction/quickstart.md)

- 2. Running Experiments

  - [Overview](/running_an_experiment/overview.md)
  - [Choosing a Workflow](/running_an_experiment/choosing_a_workflow.md)
  - [Understanding Configuration](/running_an_experiment/understanding_configuration.md)
    - [SLURM Configuration](/configuration_reference/slurm_configuration.md)
  - [Creating an Experiment](/running_an_experiment/creating_an_experiment.md)
  - [Modifying an Experiment with Overrides](/practical_examples/README.md?id=using-defaults-with-overrides)
  - [Generated Directory Layout](/running_an_experiment/experiment_directory.md)
  - [Launching an Experiment](/running_an_experiment/launching_an_experiment.md)
  - [Monitoring, Restarting, and Stopping](/running_an_experiment/monitoring_an_experiment.md)
  - [Logs and Output Products](/running_an_experiment/logs_and_output_products.md)
  - [Manually Running Tasks](/running_an_experiment/manually_running_tasks.md)

- 3. Workflow Guides

  - Ocean and Sea-Ice DA
    - [3DVAR Marine](/practical_examples/soca/3dvar_marine.md)
    - [3DVAR Marine Cycle Tier 2](/practical_examples/soca/3dvar_marine_cycle_tier2.md)
    - [3DFGAT Marine Cycle](/practical_examples/soca/3dfgat_marine_cycle.md)
  - Atmospheric (Weather) DA
    - [3DVAR Atmosphere](/practical_examples/atmosphere/3dvar_atmos.md)
    - [Ensemble Data Assimilation](/practical_examples/atmosphere/eda_atmos.md)
    - [Local Ensemble DA](/practical_examples/atmosphere/localensembleda.md)
    - [Ensemble Tools](/practical_examples/atmosphere/ensemble_tools.md)
  - Atmospheric Composition DA
    - [Overview](/practical_examples/geos_cf/README.md)
    - [HofX GEOS-CF](/practical_examples/geos_cf/hofx_cf.md)
    - [3DVAR GEOS-CF](/practical_examples/geos_cf/3dvar_cf.md)
    - [3DVAR GEOS-CF Cycle](/practical_examples/geos_cf/3dvar_cf_cycle.md)
  - Background and Observation Ingestion
    - [Storing Observations and Backgrounds in R2D2](/practical_examples/r2d2/r2d2_ingest.md)
  - Comparison and Evaluation
    - [Comparing Experiment Outputs](/practical_examples/generic_suites/comparison_workflows.md)

- 4. Data and R2D2

  - [R2D2 Concepts](/introduction/r2d2_overview.md)
  - [Fetching Observations from a Public S3 Bucket](/configuration_reference/fetch_observations_public_s3.md)
  - [R2D2 Credentials](/configuration_reference/r2d2_v3_credentials.md)
  - [Servers and Datastores](/installation_and_setup/configuring_aws_server.md)

- 5. Extending Swell

  - [Adding Tasks](/extending_swell/adding_tasks.md)
  - [Adding Questions](/extending_swell/adding_questions.md)
  - [Adding a Suite or Workflow](/extending_swell/adding_a_suite.md)
  - [Adding Model Interfaces](/extending_swell/adding_model_interfaces.md)
  - [Adding Platform Support](/extending_swell/adding_platform_support.md)

- 6. Testing and Contributing

  - [Development Setup](/testing_and_contributing/development_setup.md)
  - [Code Tests](/testing_and_contributing/code_tests.md)
  - [Tier 1 and Tier 2 Suite Tests](/testing_and_contributing/suite_tests.md)
  - [Editing the Documentation](/testing_and_contributing/editing_docs.md)
  - [Contribution Guidelines](/testing_and_contributing/contribution_guidelines.md)

- 7. Additional Resources

  - [Frequently Asked Questions](/additional_resources/faq.md)
  - [Useful Links](/additional_resources/useful_links.md)
  - Physical Model Settings
    - [CICE6](/configuration_reference/model_configurations/cice6.md)
    - [MOM6](/configuration_reference/model_configurations/mom6.md)
    - [History Outputs](/configuration_reference/model_configurations/history_outputs.md)
