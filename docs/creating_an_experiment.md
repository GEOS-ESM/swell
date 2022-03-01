# Creating an experiment using Swell

Once you have [configured Cylc](configuring_cylc) you should be able to create and run an
experiment.

First you need to load swell so it's available in your path. Modules for supported tags of Swell are
available on Discover by issuing:

```
export DHJEDIOPT=/discover/nobackup/drholdaw/JediOpt/
module use -a $DHJEDIOPT/modulefiles/core
module load swell/1.0.1
```
Alternatively you can load your own version of Swell, for example if you followed the instructions
[to install Swell as a module](installing_swell_as_a_module).

In order to create an experiment Swell uses a YAML configuration file that describes the setup. To
create an experiment that runs a data assimilation *h(x)* experiment you can issue:

```
swell_create_experiment $SUITEPATH/hofx/experiment.yaml
```

Note that `$SUITEPATH` is set by loading the Swell module. It points to the library part of the
Swell install.

The location that the experiment is installed to is set in the `experiment.yaml` with the key
`experiment_dir`. The default is `$NOBACKUP/JediExperiments/$(experiement_id)`

### Clean and create

Optionally you can remove any existing experiment that is described in `experiment.yaml` by issuing

```
swell_create_experiment $SUITEPATH/hofx/experiment.yaml --clean
```

The code will prompt you with the full path before actually removing the directory.
