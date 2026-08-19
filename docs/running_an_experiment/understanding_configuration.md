# Understanding Configuration

Swell builds an experiment by asking a series of "questions" and resolving each one to a value. Every question is resolved through a layered hierarchy of defaults and overrides, so there are several places a user can intervene depending on how permanent and how targeted the change needs to be. A simple `swell create <suite>` will start an experiment and use all the default values plus the values specified in `suite_config.py` (more about this in section 4). The list below includes different ways a user can configure a Swell experiment:


## 1. The interactive CLI (`-m cli`)

The quickest way to configure a single experiment is to run `swell create <suite> -m cli`. This launches the Questionary command-line client (`GetAnswerCli`), which walks you through every model-independent and model-dependent question in order, pre-populating each prompt with the suite's default and letting you accept or change it. With no `-m` option (i.e., `swell create <suite>`), Swell instead uses `-m defaults`, meaning it silently takes the baked-in tier-1 defaults without asking anything.

This method is recommended only for quick testing of the system as it makes the reproducibility of an experiment almost imposible.


## 2. An override file (`-o override.yaml`)

For a repeatable, non-interactive tweak, pass `swell create <suite> -o my_override.yaml`. The override file is a YAML that looks like the final experiment dictionary: any top-level key you list replaces that question's `default_value` and for all the other keys not listed in this yaml the default values will be selected. The *model-dependent* settings go under a nested `models:` block keyed by model component, e.g.:

```
start_cycle_point: 2023-10-10T00:00:00Z
models:
  geos_atmosphere:
    horizontal_resolution: "91"
    npx_proc: 4
```
This is the preferred way to customize a run without editing source code.

## 3. Command-line flags for cross-cutting settings

Several flags configure whole categories of behavior rather than individual questions.
* `-p/--platform` selects which platform's `suite_questions.yaml` / `task_questions.yaml` defaults fill in any value marked `defer_to_platform` (paths, accounts, resources).
* `-s/--slurm` injects [SLURM directives](../configuration_reference/slurm_configuration.md) globally, per-task, or per task/model combination.
* `-k/--skip-r2d2` disables R2D2 registration and storage for the experiment. [TODO add link to skip-r2d2]

These behave as overrides layered on top of the suite and platform defaults.

## 4. The suite's suite_config.py

To change the default values themselves edit the relevant `QuestionList` in `src/swell/suites/<suite>/suite_config.py`. Each entry (e.g. `ingest_obs_cf`) defines the model-independent questions plus per-model blocks (`geos_cf=[...]`) using the `QuestionDefaults` (`qd`) and `SuiteQuestions` (`sq`) helpers.


## 5. The shared question and defaults hierarchy

Underneath the individual suites is a stack of shared definitions that determine what a
question *is* and what it falls back to:

- [`suite_questions.py`](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/suites/suite_questions.py) groups reusable question sets (like `common`). In common keys such as `cycle_times`, `start_cycle_points`, `final_cycle_points`, etc. are listed. These keys are shared between any suites that use `common` in their `suite_config.py`. See `hofx_cf` as [an example](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/suites/hofx_cf/suite_config.py#L27).

- [`question_defaults.py`](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/utilities/question_defaults.py) defines each question's prompt, type, and base default. The `default_value` of some questions are set to `defer_to_platform`, `defer_to_model`, or `defer_to_code`.

  The **per-platform** and **per-model** default values are defined under `src/swell/deployment/platforms/generic/suite_questions.yaml` and `src/swell/configuration/jedi/interfaces/<model>/suite_questions.yaml`.

  Editing these affects behavior across many suites at once, so it's the right layer only
for global changes (adding a new question, changing a default resolution for
every model, etc.).

### More about `defer_to_*`:

Many questions don't have a single sensible default, because the right value depends on
*which model component* the experiment uses (e.g. `geos_atmosphere` vs. `marine` model)
or *which platform* it runs on. Rather than hard-code a value, `question_defaults.py`
sets these questions to a **sentinel string** that means "I don't know yet — go look it
up later":

- **defer_to_model** — resolve this from the model component in `src/swell/configuration/jedi/interfaces/<model>/suite_questions.yaml` and `src/swell/configuration/jedi/interfaces/<model>/task_questions.yaml`
- **defer_to_platform** — resolve this from the platform in `src/swell/deployment/platforms/generic/suite_questions.yaml`
- **defer_to_code** — resolve this in [`prepare_config_and_suit.py`](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/deployment/prepare_config_and_suite/prepare_config_and_suite.py) (e.g. `r2d2_experiment_id` or `experiment_id`).


## 6. Editing the generated experiment directly (Modifying an experiment)
Finally, once `swell create` has produced the experiment directory, the resulting `experiment.yaml` and `flow.cylc` are plain text files. For a one-off manual adjustment before launching, you can edit these directly — though for anything you'll want to reproduce, capturing the change as an `override` file or in `suite_config.py` is preferable.



## An example -- Using pinned JEDI build vs. building JEDI

Due to frequent updates on JEDI's repositories, Swell users may want to develop against a pinned version of the JEDI ecosystem. The Swell team builds, supports, and continually ypdates a JEDI build that is pinned to [specific commit hashes](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/utilities/pinned_versions/pinned_versions.yaml). Users can use the JEDI executables from this JEDI build.


By default, Swell builds JEDI using either the `develop` branch of JEDI-bundle repositories, or use commit hashes specified in `utilities/pinned_versions/pinned_versions.yaml`. These can be set by using `jedi_build_method: create` for building with `develop` branches, and `jedi_build_method: pinned_create` for building with specific commit hashes.

Most experiment suites, however, use `use_existing` key to link the JEDI build maintained by the Swell team. This is set in `src/swell/suites/<your_suite>/suite_config.py` and also `src/swell/deployment/platforms/<your_platform>/task_questions.yaml`. To use a different pre-built JEDI, you can add this to your `override.yaml` use:

```YAML
jedi_build_method: use_existing
existing_jedi_source_directory: /path/to/jedi_bundle
existing_jedi_build_directory: /path/to/jedi_bundle/build
```

If you like to build your own JEDI-bundle you can follow the instructions [here](https://geos-esm.github.io/jedi_bundle/#/building_jedi_code).

After selecting the appropriate configuration method, continue to
[Creating an Experiment](creating_an_experiment.md). The generated configuration and workflow
files are described later in [Generated Directory Layout](experiment_directory.md).
