# Adding Platform Support

Platforms have certain defaults that are selected when the experiment is created using `swell create ... -p <platform>`.

Adding support for platforms includes setting individual platform keys for experiment.yaml, slurm settings, compute information, and adding a template file for modules.
Per-platform configurations live under `src/swell/deployment/platforms/<platform>/`

### Questions
Any questions that default to `defer_to_platform` need to have associated settings in `src/swell/deployment/platforms/<platform>/<suite or task>_questions.yaml`

### Modules
The `modules` file is a jinja2 template for a shell source file that sets paths to important modules. `experiment.yaml` can be used to template this file, which is mostly used for setting the path to the experiment's JEDI build, for example:
```bash
# JEDI Python Path
# ----------------
PYTHONPATH={{experiment_root}}/{{experiment_id}}/jedi_bundle/build/lib/python{{python_majmin}}:$PYTHONPATH
```

This file should be `bash`-compliant. A separate process then translates this file into a `csh` version, `modules-csh`.

### Slurm and node properties
`properties.yaml` defines hostnames for login and compute nodes, used to determine which of these the process is running on. For Discover, this is:
```
hostname:
  login: discover
  compute: borg
```

`slurm.yaml` is used to set any platform-specific requirements for `sbatch` commands, such as:
```
qos: allnccs
nodes: 1
ntasks-per-node: 64
constraint: mil
no-requeue: ''
```
