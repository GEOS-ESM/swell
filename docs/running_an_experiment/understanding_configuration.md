# Understanding Configuration

Swell builds an experiment by resolving a series of configuration questions. Each answer comes
from a layered hierarchy of suite, model, and platform defaults, with optional user overrides.
Choose a configuration method based on whether the experiment is exploratory or must be reproduced.

## 1. Using the defaults

The simplest command uses the selected suite's resolved defaults without asking questions:

```bash
swell create <suite>
```

This is equivalent to using `-m defaults`. It is useful for running a suite's standard
configuration or creating an initial `experiment.yaml` to inspect.

## 2. Using an override file (`-o override.yaml`)

An override file is the preferred way to customize a reproducible experiment. Pass it to
`swell create` with `-o` or `--override`:

```bash
swell create <suite> -o my_override.yaml
```

The override file follows the structure of the final experiment configuration. A top-level key
replaces the resolved value for that question. Settings that belong to a model component go under
a `models` block keyed by component, for example:

```yaml
start_cycle_point: 2023-10-10T00:00:00Z
models:
  geos_atmosphere:
    horizontal_resolution: "91"
    npx_proc: 4
```

Keys not included in the override continue to use their resolved defaults. Keeping experiment
changes in an override file makes them easier to review, reuse, and version-control.

## 3. Command-line options for cross-cutting settings

Several options configure broad categories of behavior:

- `-p/--platform` selects which platform defaults provide paths, accounts, and resources.
- `-s/--slurm` applies [SLURM directives](../configuration_reference/slurm_configuration.md)
  globally, per task, or per task and model combination.
- `-k/--skip-store-r2d2` disables R2D2 registration and storage for the experiment.

These options are useful for settings that apply across the workflow. Experiment-specific values
should normally remain in an override file.

## 4. Interactive configuration for exploratory runs (`-m cli`)

Run the Questionary command-line client with:

```bash
swell create <suite> -m cli
```

The client walks through the model-independent and model-dependent questions in order. Each prompt
is pre-populated with its resolved default, which you can accept or replace.

Interactive configuration is useful for exploring available settings and quick tests. Because the
answers are entered during creation rather than maintained in a separate input file, use an
override file for experiments that need to be reproduced or reviewed later.

## 5. Editing a generated experiment

After `swell create` finishes, `experiment.yaml` and `flow.cylc` are plain-text files. You can edit
them directly for a one-off test before launch. For changes that need to be reproduced, update an
override file and create the experiment again instead.

The [Generated Directory Layout](experiment_directory.md) explains where these files are located
and how Swell uses them.

## 6. Advanced: how defaults are resolved

The following configuration layers are primarily relevant to developers changing the behavior of
Swell itself rather than configuring a single experiment.

### Suite defaults

Each suite defines a `QuestionList` in `src/swell/suites/<suite>/suite_config.py`. It combines
model-independent questions with per-model blocks using the `QuestionDefaults` (`qd`) and
`SuiteQuestions` (`sq`) helpers. Editing this file changes the defaults for every experiment
created from that suite.

### Shared questions and defaults

- [`suite_questions.py`](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/suites/suite_questions.py)
  groups reusable question sets, such as cycle bounds shared by several suites.
- [`question_defaults.py`](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/utilities/question_defaults.py)
  defines each question's prompt, type, and base default.
- Model-specific defaults are defined under
  `src/swell/configuration/jedi/interfaces/<model>/suite_questions.yaml` and
  `task_questions.yaml`.
- Platform-specific defaults are defined under `src/swell/deployment/platforms/<platform>/`.

Changing these shared definitions affects multiple suites. Use this layer for changes to Swell's
global behavior, such as adding a question or changing a default for every experiment using a
particular model or platform.

### Deferred values

Some questions do not have one sensible default. Their initial value is a sentinel that directs
Swell to resolve the answer from another layer:

- `defer_to_model` resolves the value from the selected model component.
- `defer_to_platform` resolves the value from the selected platform.
- `defer_to_code` resolves the value in
  [`prepare_config_and_suite.py`](https://github.com/GEOS-ESM/swell/blob/develop/src/swell/deployment/prepare_config_and_suite/prepare_config_and_suite.py),
  as with `r2d2_experiment_id` or `experiment_id`.

## 7. Example: selecting a JEDI build

Swell can build JEDI from source or use an existing build. `jedi_build_method: create` builds from
the configured development branches, while `jedi_build_method: pinned_create` uses the commit
hashes in `src/swell/utilities/pinned_versions/pinned_versions.yaml`.

Most experiment suites use an existing build maintained by the Swell team. To select another
pre-built JEDI installation, add the following values to an override file:

```yaml
jedi_build_method: use_existing
existing_jedi_source_directory: /path/to/jedi_bundle
existing_jedi_build_directory: /path/to/jedi_bundle/build
```

See the [JEDI bundle documentation](https://geos-esm.github.io/jedi_bundle/#/building_jedi_code)
for instructions on building a bundle.

After selecting the appropriate configuration method, continue to
[Creating an Experiment](creating_an_experiment.md).
