
## Create a Swell 3dvar_atmos experiment:

To create a `3dvar_atmos` suite in swell, run the following command:

```bash
swell create 3dvar_atmos 
```

If you want to customize the run directory of the suite, use the override option (`-o` or `--override`).

```bash
swell create 3dvar_atmos -o override.yaml
```

where the `override.yaml` file may look like 
```bash
experiment_root: ${NOBACKUP}/your_swell_experiment_path
experiment_id: 3dvar_test
```


## The configuration file for 3dvar-atmos (`experiment.yaml`):


The command `swell create suite -o override.yaml` will generate `experiment.yaml` (the final configure file) and `flow.cylc` (the final cylc file) in
the `experiment_id/${experiment_id}-suite` directory under your specified swell experiment path.  Inside `experiment.yaml`, you will find

```bash

# List of models in this experiment
model_components:
- geos_atmosphere

# Configurations for the model components.
models:

  # Configuration for the geos_atmosphere model component.
  geos_atmosphere:

    # Enter the cycle times for this model.
    cycle_times:
    - T00
    - T06
    - T12
    - T18

    # Do you want to use cycling VarBC option?
    cycling_varbc: false

    # Provide a path that contains observation files not in r2d2.
    ioda_locations_not_in_r2d2: /media/yonggang/T9/yonggang/discover/nobackup/projects/gmao/dadev/rtodling/archive/542/prePP/ioda

    # What number of processors do you wish to use in the x-direction?
    npx_proc: 1

    # What number of processors do you wish to use in the y-direction?
    npy_proc: 1

    # Which GSIBEC climatological or hybrid?
    gsibec_configuration: cli_gsibec_configuration

    # How many number of latutides in GSIBEC grid?
    gsibec_nlats: '91'

    # How many number of longitudes in GSIBEC grid?
    gsibec_nlons: '144'

    # What is the horizontal resolution for the forecast model and backgrounds?
    horizontal_resolution: '13'

    # Which saber central block do you want to use?
    saber_central_block: defer_to_model

    # What is the vertical resolution for the forecast model and background?
    vertical_resolution: '72'

    # What is the name of the name of the experiment providing the backgrounds?
    background_experiment: x0050

    # How long before the middle of the analysis window did the background providing forecast begin?
    background_time_offset: PT9H

    # What is the path to the GEOS X-backgrounds directory?
    geos_x_background_directory: /media/yonggang/T9/yonggang/discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x

    # Provide a list of patterns that you wish to remove from the cycle directory.
    clean_patterns:
    - '*.txt'
    - '*.csv'

    # Which observations do you want to include?
    observations:
    - abi_g16
    - abi_g18
    - aircraft_temperature
    - aircraft_wind
    - airs_aqua
    - amsr2_gcom-w1
    - amsua_aqua
    - amsua_metop-b
    - amsua_metop-c
    - amsua_n15
    - amsua_n18
    - amsua_n19
    - atms_n20
    - atms_n21
    - atms_npp
    - avhrr3_metop-b
    - avhrr3_metop-c
    - avhrr3_n18
    - avhrr3_n19
    - cris-fsr_n20
    - cris-fsr_n21
    - cris-fsr_npp
    - gmi_gpm
    - gps
    - iasi_metop-b
    - iasi_metop-c
    - mhs_metop-b
    - mhs_metop-c
    - mhs_n19
    - mls55_aura
    - omieff_aura
    - ompslpnc_n21
    - ompslpnc_npp
    - ompsnm_npp
    - pibal
    - satwind
    - scatwind
    - sfcship
    - sfc
    - sondes
    - ssmis_f17

    # What is the path to the GSI formatted observing system records?
    observing_system_records_mksi_path: None

    # What is the path to the Swell formatted observing system records?
    observing_system_records_path: None

    # What is the path to the CRTM coefficient files?
    crtm_coeff_dir: /discover/nobackup/projects/gmao/advda/SwellStaticFiles/jedi/crtm_coefficients/2.4.1-1/

    # What is the duration for the data assimilation window?
    window_length: PT6H

    # Do you want to use a 3D or 4D (including FGAT) window?
    window_type: 3D

    # What are the analysis variables?
    analysis_variables:
    - eastward_wind
    - northward_wind
    - air_temperature
    - water_vapor_mixing_ratio_wrt_moist_air
    - air_pressure_at_surface
    - air_pressure_levels
    - cloud_liquid_ice
    - cloud_liquid_water
    - rain_water
    - snow_water
    - mole_fraction_of_ozone_in_air
    - geopotential_height_times_gravity_at_surface
    - fraction_of_ocean
    - fraction_of_lake
    - fraction_of_ice
    - skin_temperature_at_surface

    # What value of gradient norm reduction for convergence?
    gradient_norm_reduction: 1e-10

    # Which data assimilation minimizer do you wish to use?
    minimizer: DRPCG

    # What number of iterations do you wish to use for each outer loop? Provide a list of integers the same length as the number of outer loops.
    number_of_iterations:
    - 30

    # Which saber outer blocks do you want to use?
    saber_outer_block: defer_to_model

    # What is the number of processors per host?
    perhost:

    # Provide the log naming convention (e.g. 'variational', 'fgat').
    comparison_log_type: variational

    # What is the database providing the observations?
    obs_experiment: x0050

    # Perform check for observations? Set to false for debugging purposes.
    check_for_obs: true

    # What is the GSI formatted observing system records tag?
    observing_system_records_mksi_path_tag: v5.42.7

...

```

A few important keywords include

- 



























## Launch the `3dvar-atmos` experiment

If `swell create 3dvar-atmos` is successful, you will be provided with a print out to launch the cylc job for the 3dvar-atmos suite, which typically looks like:

```
swell launch /discover/nobackup/.../`experiment_id`/`experiment_id`-suite
```








## The overall workflow

A conventional 3D-Var minimization is invoked for each member state and the resulting ensemble anlysis states are the final products from 3D-EDA.


1. The driver for this mechanism is defined in `flow.cylc`

```cylc
   {% for i in range( 1, models[model_component]['ensemble_num_members'] + 1 ) %}
   EDA_start-{{model_component}} => RunJediEdaExecutable_mem{{i}}-{{model_component}} => EDA_end-{{model_component}}
   ...

   [[RunJediEdaExecutable_mem{{i}}-{{model_component}}]] 
     script = "swell task RunJediEdaExecutable $config -d $datetime -m {{model_component}} -imem {{i}}"
   ...
```

The independent SWELL tasks `RunJediEdaExecutable -imem i` are submitted to the queue for 3D-Var type computation, where its yaml input files are customized for observation perturbations.



2. Observation thinning:

   EDA calculations demands a significant amount of computational resources. For test runs, users can thin the observartion data by setting `obs_thinning_rej_fraction` from zero (no thinning) to 1 (reject all). Example override file contains:

```cylc
  geos_atmosphere:
    horizontal_resolution: "91"
    obs_thinning_rej_fraction: 0.98
    ensemble_num_members: 3
    observations: [ "sondes" ]
```

   The underlying obs thinning function is performed by
```Bash
   swell task RunJediObsfiltersExecutable $config -d $datetime -m geos_atmosphere
```



As time elapes, your output directory will look like

```
geos_atmosphere
├── amsua_metop-b.20231009T210000Z_orig.nc4
├── amsua_metop-b.20231009T210000Z.nc4
├── jedi_obsfilters_config.yaml
├── jedi_eda3D_config_mem001.yaml
├── jedi_eda3D_config_mem002.yaml
├── analysis
│   ├── mem001
│   │   ├── eda.amsua_metop-b.20231009T210000Z.nc4
│   │   ├── eda.ana.mem001.20231010_000000z.nc4
│   │   ├── eda.iasi_metop-b.20231009T210000Z.nc4
│   │   ├── eda.inc_iter1.mem001.20231010_000000z.nc4
│   │   ├── eda.sfcship.20231009T210000Z.nc4
│   │   └── eda.sondes.20231009T210000Z.nc4
│   └── mem002
│       ├── eda.amsua_metop-b.20231009T210000Z.nc4
│       ├── eda.ana.mem002.20231010_000000z.nc4
│       ├── eda.iasi_metop-b.20231009T210000Z.nc4
│       ├── eda.inc_iter1.mem002.20231010_000000z.nc4
│       ├── eda.sfcship.20231009T210000Z.nc4
│       └── eda.sondes.20231009T210000Z.nc4

```

These files indicate your `obs thinning` process is successful and the analysis and increment files for each member have been created.


4. Postprocessing tasks (ensemble mean and variance)

Once analysis of each member is obtained, the flow.cylc starts to generate the mean and variance for visualization using tasks below

```
swell task RunJediEnsembleMeanVariance  PATHTO/experiment.yaml -d $date -m geos_atmosphere
swell task RunJediDiffstates PATHTO/experiment.yaml -d $date -m geos_atmosphere
```

The output files look like:
```
geos.prior.mean.20231010_000000z.nc4        [mean of ebkg in CS grid]
geos.prior.mean.ll.20231010_000000z.nc4     [... in LL grid]
geos.prior.variance.20231010_000000z.nc4    [variance of ebkg in CS grid]
geos.prior.variance.ll.20231010_000000z.nc4 [... in LL grid]
...
eda.ana.mean.20231010_000000z.nc4           [mean of analysis in CS grid]
eda.ana.mean.ll.20231010_000000z.nc4        [... in LL grid]
eda.ana.variance.20231010_000000z.nc4       [variance of anlaysis in CS grid]
eda.ana.variance.ll.20231010_000000z.nc4    [... in LL grid]
...
eda.mean-inc.20231010_000000z.nc4           [mean increment in LL grid]
eda.mean-inc.cs.20231010_000000z.nc4        [... in CS grid]
```


5. EVA plots and EDA clean up

The eda-atmos workflow will trigger EVA plot for ensemble mean increment. 
An example of mean T increment at 500 hPa is shown below.

To save disk space on discover, the HofX outputs for individual ensemble members are purged at the end of the flow.
The output directory will look like

```
analysis/
├── mem001
│   ├── eda.ana.mem001.20231010_000000z.nc4
│   ├── eda.inc_iter1.mem001.20231010_000000z.nc4
└── mem002
    ├── eda.ana.mem002.20231010_000000z.nc4
    ├── eda.inc_iter1.mem002.20231010_000000z.nc4
```








