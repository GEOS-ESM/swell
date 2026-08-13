
## Create a Swell 3dvar_atmos experiment:

To create a `3dvar_atmos` suite in swell, run the following command:

```bash
swell create 3dvar_atmos 
```

If you want to customize the run directory of the suite, use the override option (`-o` or `--override`):

```bash
swell create 3dvar_atmos -o override.yaml
```

where the `override.yaml` file may look like 
```yaml
experiment_root: ${NOBACKUP}/your_swell_experiment_path
experiment_id: test001
```


## The configuration file for 3dvar-atmos (`experiment.yaml`):


The command `swell create suite -o override.yaml` will generate `experiment.yaml` (the final configure file) and `flow.cylc` (the final cylc file) in
the `${experiment_id}/${experiment_id}-suite` directory under your_swell_experiment_path.  Inside `experiment.yaml`, you will find

```yaml
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
    ioda_locations_not_in_r2d2: /discover/nobackup/projects/gmao/dadev/rtodling/archive/542/prePP/ioda

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
    geos_x_background_directory: /discover/nobackup/projects/gmao/dadev/rtodling/archive/Restarts/JEDI/541x

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

A few important keywords from this file include

`cycle_times`: define the 6-hour cycle point. 

`cycling_varbc`: specifies if varbc file is updated every cycle.

`analysis_variables`: here please be aware that both `air_pressure_at_surface` and `air_pressure_levels` are specified which may need to be adjusted in certain circumstances

`gradient_norm_reduction` and `number_of_iterations` are used to determine the cost function minization stop point

`observations`:  the list of observations; you can override this observation list using override.yaml


For example, for test purposes the simple override.yaml file below can be used to replace the full list of observations by a single obs type
```yaml
models:
  geos_atmosphere:
    observations: [ "atms_n20" ]
```



## Launch the `3dvar-atmos` experiment

If the `swell create 3dvar-atmos` command runs successfully, you will be provided with a printout to launch the cylc job for the 3dvar-atmos suite, which looks like:

```bash
swell launch /discover/nobackup/.../${experiment_id}/${experiment_id}-suite
```


## While the suite is running

Initially you will find a few directories under your swell experiment path,

```bash
test001/
├── configuration
├── test001-suite/
|    ├── eva
|    │   ├── increment-geos_atmosphere.yaml
|    │   ├── jedi_log-geos_atmosphere.yaml
|    │   └── observations-geos_atmosphere.yaml
|    ├── experiment.yaml
|    ├── flow.cylc
|    ├── modules
|    └── modules-csh
|
├── jedi_bundle
|    ├── build -> /discover/nobackup/projects/gmao/advda/swell/JediBundles/fv3_soca_SLES15_06242026/build-intel-release
|    └── source -> /discover/nobackup/projects/gmao/advda/swell/JediBundles/fv3_soca_SLES15_06242026
|── run
```


Note the the `jedi_bundle` directory contains soft links to JEDI source code and JEDI build.
The `test001-suite` contains the `modules` file which can be used to load the environment, the `flow.cylc` to launch the cylc workflow, and
the `experiment.yaml` file which is global configuration generated from the `swell create` step. 



## After the run is complete

The output from a single cyle point (`20231010T000000Z`) for a single model (`geos_atmosphere`) contains the following directory,

```bash
run/
└── 20231010T000000Z
    └── geos_atmosphere
        ├── test001.analysis.20231010_000000z.nc4
        ├── test001.increment-iter1.20231010_000000z.nc4
        ├── jedi_variational_config.yaml
        ├── jedi_variational_log.log
        ├── eva/        
```

`eva/` directory contains the graphics output for analysis increment, the variational gradient convergence figure, etc.
