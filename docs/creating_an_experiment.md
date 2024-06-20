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

