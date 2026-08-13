The diagnostic tools:

We have designed handy codelets to compute mean/variance and diffstate (for increment, e.g.) in Swell.


## Compute ensemble mean and variance using `RunJediEnsembleMeanVariance`


To compute the mean and variance from the provided ensemble forecast (including bkg and analysis), 
user can define a dictionary list containing multiple entries, where each entry can contain
its own input file, output file, and grid_type.


There are two ways to create the configure file.

Method-1. modify the `eda-atmos` suite config file:

```bash
swell/src/swell/suites/eda/suite_config.py

Lines 108 to 119 in 35e846c
 qd.ensmeanvariance_spec([ 
     {"state": "bkg", 
      "fn_input": "ebkg/mem%mem%/geos.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4", 
      "fn_output_mean": "geos.prior.mean", 
      "fn_output_variance": "geos.prior.variance", 
      "grid_type": ['cs', 'latlon']}, 
     {"state": "analysis", 
      "fn_input": "analysis/mem%mem%/eda.ana.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4", 
      "fn_output_mean": "eda.ana.mean", 
      "fn_output_variance": "eda.ana.variance", 
      "grid_type": ['cs', 'latlon']}, 
     ]), 
```

Method-2. create a section in `override.yaml`

```yaml
models:
  geos_atmosphere:
    ensmeanvariance_spec:
    - state: bkg
      fn_input: ebkg/mem%mem%/geos.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4
      fn_output_mean: geos.prior.mean
      fn_output_variance: geos.prior.variance
      grid_type: [ 'latlon', 'cs' ]
    - state: analysis
      fn_input: analysis/mem%mem%/eda.ana.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4
      fn_output_mean: eda.ana.mean
      fn_output_variance: eda.ana.variance
      grid_type: [ 'latlon', 'cs' ]
```

then run: `swell create eda_atmos -o override.yaml` to override the config default.

Finally to compute the mean and variance, run
`swell task RunJediEnsembleMeanVariance  PATHTO/experiment.yaml -d $date -m geos_atmosphere`. 



## Compute the difference between two states

Method-1. modify the EDA suite config file:

```bash
swell/src/swell/suites/eda/suite_config.py

Lines 120 to 128 in 35e846c
 qd.diffstates_spec({ 
     "state1": 
     {"fn_input": "geos.prior.mean.%yyyy%mm%dd_%hh%MM%ssz.nc4"}, 
     "state2": 
     {"fn_input": "eda.ana.mean.%yyyy%mm%dd_%hh%MM%ssz.nc4"}, 
     "state_diff": 
     {"fn_output": "eda.mean-inc", "grid_type": ['cs', 'latlon']}, 
     "state_type": "ensemble" 
     }), 
```

Method-2. create an override section in override.yaml

```yaml
models:
  geos_atmosphere:
    ensmeanvariance_spec:
    diffstates_spec:
      state1:
        fn_input: geos.prior.mean.%yyyy%mm%dd_%hh%MM%ssz.nc4
      state2:
        fn_input: eda.ana.mean.%yyyy%mm%dd_%hh%MM%ssz.nc4
      state_diff:
        fn_output: eda.mean-inc
        grid_type: [ 'cs', 'latlon' ]  
      state_type: ensemble
```

then run: `swell create eda_atmos -o override.yaml` to override the default config.

Finally to compute the diff states, run
`swell task RunJediDiffstates PATHTO/experiment.yaml -d $date -m geos_atmosphere`

