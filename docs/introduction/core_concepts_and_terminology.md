# Core Concepts and Terminology

## What Is Swell?

The swell system is developed by NASA's Global Modeling and Assimilation Office. It is used to generate experiments using the JEDI data assimilation system and NASA's Goddard Earth Observing System (GEOS) numerical weather forecast model. 

Before diving into installation and configuration, it helps to understand the concepts that Swell is built around: such as **workflow**,  **suite**,  **task**, **question**, and **experiment**.

1. The swell **suite** is the blueprint for the kind of application wanted with very configurable options for various cases.
2. Each suite exposes a set of **questions** which are the configurable parameters that need an answer before the application can run.
3. Swell can then generate an **experiment** containing a set of interdependent **tasks** defined in a `cylc` graph.
4. The **workflow** `cylc` reads `flow.cylc` and executes the **tasks** in the order and the dependencies the suite defines, running the actual application **experiment**.


## Suites: An Organized Succession of Tasks

A **suite** is the definition of *what an application is made of* and *in what order it runs*. Concretely, a suite is a directory under `src/swell/suites/` that provides:

- A template describing the tasks and the dependency graph between them (what must finish before what can start, what can run in parallel, what can retry or fall back to another task on failure).
- A set of suite-level questions describing the parameters needed to configure the application (models involved, cycle times, resolution, etc.). Such parameters can be overriden with a yaml at the suite execution. See section on overrides.

Because the suite defines an ordered (and sometimes conditional/parallel) graph of steps, it is useful to think of a suite as **a succession of organized tasks that, run together, execute an application**. The suite itself never runs anything directly; it is the plan that Cylc follows once it's been turned into an experiment.

In software enginnering terms: a **suite is a class** and an **experiment is an instance (object) of that class**. The suite defines the *structure* in which tasks exist, how they depend on each other. Just as many objects can be created from one class, many experiments (different resolutions, cycle windows, models, platforms) can be created from the same suite, each with its own state and results, without changing the suite definition itself.

## Questions: Turning a Suite Into an Experiment

A **question** is a single configurable parameter that turn the suite into a runnable experiment: for example the model components to run, the start and final cycle points, the resolution, or the background error method, etc.

Both suites and individual tasks declare the questions they need. At suite creation, Swell collects the full set of questions that can come form from defaults, or from command-line input, or from an override file the user can supply. Swell uses the resulting answers to fill in the suite's templates and produce a concrete `experiment.yaml`.

## Tasks: The Single Operations That Compose a Suite

A **task** is the smallest unit of work in Swell. Ideally it is a single, well-defined operation, implemented as a Python class under `swell/src/swell/tasks/` (for example `CloneJedi`, `BuildJedi`, `GetBackground`, `RunJediVariationalExecutable`, `SaveRestart`). Each task should do only one job: clone a repository, stage some files, run a JEDI executable, save an output back to R2D2, and so on. 

Tasks come in two flavors:

- **Generic tasks** — operations that behave the same no matter which model is being run, taking the model as a parameter (via `self.get_model()`) rather than hard-coding one. Examples include `CloneJedi`, `BuildJedi`, `GetBackground`, `SaveRestart`, `RunJediVariationalExecutable`, `GetObservations`. All tasks live together, flat, under `swell/src/swell/tasks/` — there is no separate subdirectory per model.
- **Model-specific (non-generic) tasks** — tasks whose name and implementation are tied to one particular model component, because that model needs a distinct file format, restart handling, or run-directory layout. For example, `PrepForecastCf`, `SaveForecastCf`, `GetRestartCf`, and `SaveRestartCf` are specific to `geos_cf`, while `GetCoupledGeosRestart`, `LinkCoupledGeosOutput`, and `PrepCoupledGeosRunDir` are specific to the `coupled/marine` configuration. These tasks are only ever used by the suites that need that particular model.

This split is what lets Swell add support for a new model or a new suite mostly by writing a handful of new tasks and a `flow.cylc`, while reusing the large catalog of generic tasks that already exist.

## Cylc workflow: Schedules and Execute the Tasks

[Cylc](https://cylc.github.io/cylc-doc/latest/html/index.html) is a third-party workflow engine/scheduler used to actually run the experiments. Swell itself does not execute tasks, it hands that job off to Cylc.

The interaction between Swell and Cylc works like this:

- Each suite contains a `flow.cylc` template describing the tasks and their dependency graph as well as how each task is actually invoked.
- When a suite is created, Swell fills in that template with user parameters and writes a concrete `flow.cylc` into the experiment directory.
- With the experiment launch, Cylc reads the generated `flow.cylc`, resolves the dependency graph, and submits each task to run, sequentially, in parallel, and/or repeating over successive cycle points.

**Swell defines and generates the workflow; Cylc schedules and executes it.**

