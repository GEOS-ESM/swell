# Creating an experiment using Swell

Once you have installed `swell` and configured `cylc` you should be able to create and run an experiment.

A useful command when using swell is `swell --help`. This will take you through all the options within swell. The help traverses through the applications so you can similarly issue `swell create --help`

The first step is to create an experiment which is done with

```bash
swell create <suite> <options>
```

This will create a directory with your experiment ID in the experiment root.

- If you specify no options the resulting experiment will be configured the way that suite is run in the tier 1 testing.

- If you want to be taken through all the questions for configuring the experiment you would specify `swell create <suite> -m cli`

# Creating a Swell experiment using pinned Jedi Bundle
Due to frequent updates on JEDI's repositories, Swell users may want to develop against a pinned version of the JEDI ecosystem. A pinned version means that every repository required for the JEDI build is pinned to a commit hash from a specific date. These pinned hashes will be continually updated as the Swell team validates them.

There are two options for creating an experiment with a pinned JEDI bundle, and both require using the Questionary command line tool since they are currently not default options.

## Building using pinned versions
When you run `swell create <suite> -m cli`, it will take you to the Questionary command line tool. At some point, you will see the following question: 

```bash
Do you want to use an existing JEDI build or create a new build?
```
To create a new build, there are two options: `create` and `pinned_create`. Using `pinned_create` will tell the `CloneJedi` task to clone the JEDI repository commit hashes specified in `utilities/pinned_versions/pinned_versions.yaml`. Then, the experiment will run the `BuildJedi` task as normal.

## Linking to pinned versions build
There are two options to link to a JEDI build when the aforementioned question is asked: `use_existing` and `use_pinned_existing`. Using the `use_pinned_existing` option will ask for a build and source directory to link to. There are default directories provided for the user that the Swell team maintains. However, users are welcome to build pinned JEDI bundles themselves (see [here](https://geos-esm.github.io/jedi_bundle/#/building_jedi_code) for more information). Note that the build must use the hashes found in `utilities/pinned_versions/pinned_versions.yaml` or the Swell experiment will abort. 
