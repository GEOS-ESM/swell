# Fetching observations from a public S3 bucket

`GetObservations` can fetch an observation **directly from a public S3 bucket**
(e.g. NOAA's `noaa-reanalyses-pds`) into the cycle directory instead of from R2D2.
Files are pulled anonymously (no AWS credentials) and **nothing is copied into any
R2D2 datastore**.

To register an observation for this, drop a `<obs>.yaml` into the model's
`configuration/jedi/interfaces/<model>/fetch_observations_s3/` directory. The file
name must match the observation name in the experiment's `observations` list.

Requires `fetch_obs_from_public_s3: true` in the `experiment.yaml`. Observations
without a matching registry file are fetched from R2D2 exactly as before.

## Example

```yaml
s3_bucket: noaa-reanalyses-pds

# Full object key with date placeholders YYYY / MM / DD / HH (JJJ = day of year),
# resolved per sub-window time. Exact-key mode: one GET, no listing.
s3_key_template: observations/reanalysis/insitu/wod/ctd/YYYY/MM/iodav3/wod_ctd_t.YYYYMMDD.THHz_iodav3.nc

# Optional: override the default sub-window grid (T03/T09/T15/T21, PT6H) to match the
# times the files are actually stored at (WOD sits on 00/06/12/18).
obs_timesteps: ['T00', 'T06', 'T12', 'T18']
obs_window_length: PT6H
```

Each registry file fetches one file per sub-window. When a source splits an
observation across several files (WOD keeps CTD temperature and salinity in
separate files), give each its own registry file — e.g.
`insitu_temp_profile_wod_ctd.yaml` and `insitu_salt_profile_wod_ctd.yaml`.

A missing file for a sub-window falls back to empty obs without stopping the run.

## When the filename can't be built from the date

Sometimes part of a filename isn't set by the date — for example, a processing
timestamp added when the file was made — so you can't write the exact key. In that
case add `filename_pattern`: the template becomes a folder prefix that is listed,
and the first file whose name matches the pattern is used. Leave it out for the
normal case above, where the date gives you the whole key.

```yaml
s3_key_template: observations/reanalysis/<inst>/YYYY/MM/DD/
filename_pattern: '*.YYYYMMDD.*.nc'
```

## Notes

- Marine/in-situ (`adt`, `sst`, WOD) are already IODA and usable as-is. BUFR
  sources (`airs`, `amsua`, `iasi`, `conv`) would still need a BUFR→IODA step first.
- `noaa-reanalyses-pds` is not a GMAO-vetted repository; it is not intended for
  atmospheric (NWP / atmospheric reanalysis) assimilation.