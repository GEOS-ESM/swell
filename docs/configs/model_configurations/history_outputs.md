History outputs, as opposed to model restarts containing full diagnostic fields, provides a subset of variables in preset frequencies. They are typically used for providing more frequent outputs of reduced dimension variables for plotting or analysis (i.e., vertically averaged or surface-only, such as SST).

GEOSgcm provides a mechanism for dumping restarts (aka `_checkpoint`) more frequently via `Restart Record Parameters` section in `AGCM.rc`. However, this causes model to stop and create these large files with full model fields which is undesirable for long simulation times.

In SWELL context, history outputs are particularly useful for 4D window setups when multiple states and/or backgrounds are required as an input for JEDI. For instance, for a 3DFGAT setup with a 6h window and 3h background frequency, one background (at the beginning of the window) and two state inputs (one at the 3h mark one at the end) are required. This can be handled by using `diag_table` for [MOM6](mom6.md) or adjusting `ice_in` for [CICE6](cice6.md).

For example, with MOM6/CICE6, employing a 6h DA window and 3h background frequency via 3DFGAT, ocean and sea-ice backgrounds are defined by:

```yaml
background:
  basename: ./
  date: '2021-07-02T03:00:00Z'
  ice_filename: cice.res.20210702T030000Z.nc
  ocn_filename: MOM6.res.20210702T030000Z.nc
  read_from_file: 1
  state variables:
  - cicen
  - hicen
  - hsnon
  - socn
  - tocn
  - ssh
  - hocn
  - mld
  - layer_depth
```

and ocean and sea-ice states:

```yaml
model:
  name: PseudoModel
  states:
  - basename: ./
    date: '2021-07-02T06:00:00Z'
    ice_filename: ice.fc.2021-07-02T03:00:00Z.PT3H.nc
    ocn_filename: ocn.fc.2021-07-02T03:00:00Z.PT3H.nc
    read_from_file: 1
  - basename: ./
    date: '2021-07-02T09:00:00Z'
    ice_filename: ice.fc.2021-07-02T03:00:00Z.PT6H.nc
    ocn_filename: ocn.fc.2021-07-02T03:00:00Z.PT6H.nc
    read_from_file: 1
  tstep: PT3H
```

More details can be found in [JEDI/SOCA documentation](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/inside/jedi-components/soca/index.html).