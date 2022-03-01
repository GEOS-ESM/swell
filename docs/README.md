# Swell Workflow Ecosystem, Layout and Launcher

The swell system is developed by NASA's [Global Modeling and Assimilation Office](https://gmao.gsfc.nasa.gov/).
It is used to generate experiments using the [JEDI](https://www.jcsda.org/jcsda-project-jedi) data
assimilation system and NASA's [Goddard Earth Observing System (GEOS)](https://gmao.gsfc.nasa.gov/GEOS_systems/)
numerical weather forecast model. Specifically, swell is designed with coupled data assimilation
applications in mind and can be used to deploy cycled experiments for a coupled system.

Swell is written entirely using Python with configuration files written using YAML.

Swell has several responsibilities:

- To provide the tasks that make up the workflow. For example moving around observation files.
- To generate the suite files that describe the workflow order and that can be read by the workflow manager.
- To provide example configuration files that can be used to generate experiments.
- To provide the scripts that create, modify and launch experiments.
- To provide configuration for the individual components of the Earth system and the observing system.
- To provide platform/machine specific files that can be used to run experiments.

### Cylc

Swell uses the [Cylc](https://cylc.github.io/) workflow manager to launch and then monitor
experimentation. While the suite files are specific to Cylc the tasking and general configuration
files are not and it would be fairly straightforward to write suite files that direct swell tasks
through an alternative workflow manager.
