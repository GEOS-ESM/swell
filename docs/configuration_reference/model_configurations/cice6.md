# CICE6 Settings for GEOS/SOCA Setup (CICE_6.4.1/GEOSv11.6)

SOCA currently only uses category aggregated CICE variables, namely:

- `cicen`: Ice are (sea-ice concentration)
- `aicen`: Ice thickness
- `hsnon`: Snow thickness


## History Outputs

>In SWELL, history outputs are utilized to obtain the aggregated variables in desired output frequencies. See more details about [history outputs](history_outputs.md).

The following setup is for using 3 hourly states. In `ice_in`, `histfreq` should have `h` and `histfreq_n`
should be 3 for 3 hourly dumps.

```nml
histfreq       = 'h','x','x','x','x'
histfreq_n     =  3 , 1 , 1 , 1 , 1
```

Then, in the ` &icefields_nml` section, activate following variables:

```nml
f_aice         = 'h'
f_hi           = 'h'
f_hs           = 'h'
```

This will produce outputs named such as `iceh_03h.2021-07-02-43200.nc`, with `03h` prefix depending on the
`histfreq` setup.