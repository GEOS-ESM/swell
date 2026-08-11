# Swell Documentation Outline

This outline is the planning and assignment checklist for the documentation code sprint. It follows
the organization in `_sidebar.md`.

Status definitions:

- **Existing**: A dedicated page or substantial documentation already exists.
- **Partial**: Related material exists, but it does not fully cover the proposed section.
- **Missing**: No corresponding documentation currently exists.

## 1. Getting Started

Owner: __________

- [ ] **1.a. What Is Swell?** — **Existing**
  - Current documentation: [What Is Swell?](README.md)
- [ ] **1.b. [Core Concepts and Terminology](introduction/core_concepts_and_terminology.md)** — **Missing**
- [ ] **1.c. Prerequisites and Supported Platforms** — **Partial**
  - [Prerequisites](introduction/prerequisites.md): **Missing**
  - Current documentation: [Supported Platforms](installation_and_setup/platforms/README.md)
  - Related documentation: [Project Requirements and Goals](introduction/requirements.md)
- [ ] **1.d. Installation and Setup** — **Existing**
  - [Installing Swell](installation_and_setup/installing_swell.md)
  - [Configuring Cylc](installation_and_setup/configuring_cylc.md)
  - Discover
    - [Installing Swell on SLES15](installation_and_setup/platforms/discover/installing_swell_discover_sles15.md)
    - [Installing Swell with `uv` and `venv`](installation_and_setup/platforms/discover/installing_swell_uv_venv.md)
    - [Installing Swell Without Internet Access](installation_and_setup/platforms/discover/installing_swell_uv_offline.md)
    - [Installing Swell in an Interactive C Shell](installation_and_setup/platforms/discover/installing_swell_csh_interactive.md)
    - [Configuring Cylc on Discover](installation_and_setup/platforms/discover/configuring_cylc_discover.md)
- [ ] **1.e. [QuickStart](introduction/quickstart.md)** — **Missing**
  - Scope: Summarize the steps required to create, launch, monitor, and verify an experiment.

## 2. Running Experiments

Owner: __________

- [ ] **2.a. [Choosing a Workflow](running_an_experiment/choosing_a_workflow.md)** — **Missing**
  - Scope: Help users choose among HofX, 3DVAR, ensemble DA, ingestion, comparison, cycling and
    non-cycling workflows, and supported model components. A selection table or workflow catalog
    would be useful.
- [ ] **2.b. Understanding Configuration** — **Partial**
  - Scope: Explain how `experiment.yaml` is assembled and all the ways a user can configure an
    experiment.
  - Current related documentation:
    [Configuration and Experiment Overview](practical_examples/README.md)
  - External starting point:
    [How to configure a Swell experiment](https://github.com/mer-a-o/howtojedi/blob/4d076aed6f160f0ab4d99cfad1d8acdcaaafdd4e/jedi_trainings/swell/2.configure.md)
  - Current documentation: [SLURM Configuration](configuration_reference/slurm_configuration.md)
- [ ] **2.c. Creating an Experiment** — **Existing**
  - Current documentation: [Creating an Experiment](running_an_experiment/creating_an_experiment.md)
- [ ] **2.d. Modifying an Experiment** — **Partial**
  - Current related documentation:
    [Modifying an Experiment with Overrides](practical_examples/README.md?id=using-defaults-with-overrides)
- [ ] **2.e. Generated Directory Layout** — **Existing**
  - Current documentation:
    [Experiment Directory](practical_examples/README.md?id=experiment-directory)
- [ ] **2.f. Launching an Experiment** — **Existing**
  - Current documentation: [Launching an Experiment](running_an_experiment/launching_an_experiment.md)
- [ ] **2.g. Monitoring, Restarting, and Stopping** — **Partial**
  - [Monitoring an Experiment](running_an_experiment/monitoring_an_experiment.md)
  - [Stopping Jobs](running_an_experiment/launching_an_experiment.md?id=stopping-jobs)
  - Restarting and recovery guidance: **Missing**
- [ ] **2.h. Logs and Output Products** — **Partial**
  - Current related documentation:
    [Finding Task Logs](running_an_experiment/monitoring_an_experiment.md?id=when-a-task-fails)
  - General output-product guidance: **Missing**
- [ ] **2.i. Manually Running Tasks** — **Existing**
  - Current documentation:
    [Manually Running Tasks](running_an_experiment/manually_running_tasks.md)
- [ ] **2.j. [Troubleshooting](running_an_experiment/troubleshooting.md)** — **Missing**

## 3. Workflow Guides

- [ ] **3.a. Ocean and Sea-Ice DA** — **Existing** — Owner: __________
  - [3DVAR Marine](practical_examples/soca/3dvar_marine.md)
  - [3DVAR Marine Cycle Tier 2](practical_examples/soca/3dvar_marine_cycle_tier2.md)
  - [3DFGAT Marine Cycle](practical_examples/soca/3dfgat_marine_cycle.md)
- [ ] **3.b. [Atmospheric (Weather) DA](practical_examples/atmosphere/README.md)** — **Missing** — Owner: __________
- [ ] **3.c. [GEOS-CF (Composition) DA](practical_examples/geos_cf/README.md)** — **Missing** — Owner: __________
- [ ] **3.d. Background Ingestion, Observation Ingestion, and Conversion** — **Existing** — Owner: __________
  - Current documentation:
    [Storing Observations and Backgrounds in R2D2](practical_examples/r2d2/r2d2_ingest.md)
- [ ] **3.e. Comparison and Evaluation** — **Existing** — Owner: __________
  - Current documentation:
    [Comparing Experiment Outputs](practical_examples/generic_suites/comparison_workflows.md)

## 4. Data and R2D2

Owner: __________

- [ ] **4.a. R2D2 Concepts** — **Existing**
  - Current documentation: [R2D2 Concepts](introduction/r2d2_overview.md)
- [ ] **4.b. Credentials** — **Existing**
  - Current documentation: [R2D2 Credentials](configuration_reference/r2d2_v3_credentials.md)
- [ ] **4.c. Servers and Datastores** — **Existing**
  - Current documentation:
    [Configuring R2D2 Servers and Datastores](installation_and_setup/configuring_aws_server.md)
- [ ] **4.d. How Experiments Store and Retrieve Data** — **Existing**
  - Current documentation:
    [How Swell Uses R2D2](introduction/r2d2_overview.md?id=how-swell-uses-r2d2)

## 5. Extending Swell

Owner: __________

- [ ] **5.a. Adding a Task** — **Partial**
  - Current documentation: [Writing Tasks](extending_swell/adding_a_suite.md?id=writing-tasks)
- [ ] **5.b. Adding a Suite/Workflow** — **Existing**
  - Current documentation: [Adding a Suite](extending_swell/adding_a_suite.md)
- [ ] **5.c. [Adding Model Interfaces](extending_swell/adding_model_interfaces.md)** — **Missing**
- [ ] **5.d. [Adding Observations and Converters](extending_swell/adding_observations_and_converters.md)** — **Missing**
- [ ] **5.e. [Adding Platform Support](extending_swell/adding_platform_support.md)** — **Missing**

## 6. Testing and Contributing

Owner: __________

- [ ] **6.a. [Development Setup](testing_and_contributing/development_setup.md)** — **Missing**
- [ ] **6.b. Code Tests** — **Existing**
  - Current documentation: [Code Tests](testing_and_contributing/code_tests.md)
- [ ] **6.c. Tier 1 and Tier 2 Suite Tests** — **Existing**
  - Current documentation: [Suite Tests](testing_and_contributing/suite_tests.md)
- [ ] **6.d. Documentation** — **Existing**
  - Current documentation: [Editing the Documentation](testing_and_contributing/editing_docs.md)
- [ ] **6.e. [Contribution Guidelines](testing_and_contributing/contribution_guidelines.md)** — **Missing**

## 7. Additional Resources

Owner: __________

- [ ] **7.a. Useful Links and Additional Resources** — **Existing**
  - Current documentation: [Useful Links](additional_resources/useful_links.md)
- [ ] **7.b. Physical Model Settings** — **Existing**
  - [CICE6](configuration_reference/model_configurations/cice6.md)
  - [MOM6](configuration_reference/model_configurations/mom6.md)
  - [History Outputs](configuration_reference/model_configurations/history_outputs.md)
