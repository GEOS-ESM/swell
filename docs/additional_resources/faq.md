## Frequently Asked Questions (FAQ)

- Why do we need this workflow?

    > GMAO has long produced many different data assimilation products using separate, independent workflows. The core idea behind the development of JEDI was to provide abstraction across the Earth-system components used in data assimilation. Our goal in creating SWELL for the JEDI/GEOS coupled Earth-system DA ecosystem is to simplify the execution of different data assimilation experiments while standardizing key aspects of the workflow. Going forward, this will enable GMAO to test new observations, GEOS model versions, and JEDI versions more easily as coupled modeling and coupled data assimilation become increasingly important to the mission. We need more users to identify and address a broader range of use cases. Our development team is very open to constructive criticism, new feature suggestions, and contributions from all GMAO users, so do not hesitate to reach out.

    List of developers?: Michael, Doruk, Maryam, Yonggang etc.?

- This is all too complicated; I miss using (insert a software package here, last updated 10+ years ago)

    > We do our best to allocate external dependencies only when they are absolutely needed for an application (for example, GMAO_perllib) and encourage users to utilize their own tools with experiment outputs if they prefer.

- Can I use SWELL outside of NCCS Discover?

    > We would like to support additional platforms (for example, a personal laptop) beyond Discover, but we are not there yet. We do have ambitious plans to run SWELL in the cloud, but only time will tell, and we would need more support for that.

- Why is SWELL based on Cylc?

    > Cylc is an open-source software specifically designed for NWP applications, has a decent number of active agency users around the world, and new features are added continuously. It has numerous useful features for data assimilation experiments, such as intercycle task dependencies, templating via Jinja2, retrying certain tasks, SLURM commands, environment and module control, and an interactive TUI and GUI (currently being tested on Discover JupyterHub) for monitoring. The GMAO OPS team is also switching to Cylc for some of its workflows.

- R2D2 is not working for me

    > Please see [R2D2 settings](configuration_reference/r2d2_v3_credentials.md). As of the writing of this documentation, the same shared gmao-user API key is used, but this will change soon. Alternatively, the `--skip-r2d2` or `-k` argument can be used for `geos_atmosphere` applications to bypass R2D2 and use Ricardo's x00** experiment directories.

- Can I view Cylc logs with my own editor?

    > Yes. Once we switch to Cylc version 8.5.0 and later, users will be able to use their own editors (for example, Vim or Emacs). It is installed as part of SWELL currently, but it may be pre-installed in future spack-stack versions, as JCSDA is also developing its own Cylc-based workflows.

- My task has failed; I see a red box. What am I going to do?!?

    > First, see `When a task fails` under [monitoring and experiment](running_an_experiment/monitoring_an_experiment.md) to identify the root cause via logs. Even if a task fails, Cylc will keep the batch process in the background for two hours and only then will stop the suite. If `retry task` is defined for a certain task, Cylc will try rerunning the task x times after x minutes, depending on the `flow.cylc` settings (see xx). It is possible to retrigger a failed task; sometimes the problem may be a simple edit in the experiment/run directory. Afterward, the experiment will proceed as usual. It is also possible to restart (reinstall-reload) via the Cylc user interface to "revive" a stopped suite. This will allow the user to address certain issues beyond the two-hour limit.

- Cylc TUI is showing a purple box for a certain task.

    > A purple box indicates a problem with SLURM-type tasks. Please see if you defined your [SLURM settings](configuration_reference/slurm_configuration.md) properly in terms of compute group and queue types. Another common issue with new SLURM tasks is that they need to be specified under the source code `src/swell/utilities/slurm.py`.

- How can I create my own experiment?

    > See the override section (xx)

- I actually begin to like SWELL; how can I contribute?

    > See the developer guide (xx)