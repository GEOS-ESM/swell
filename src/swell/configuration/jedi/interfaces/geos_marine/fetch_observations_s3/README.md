# `fetch_observations_s3/` - fetch observations from a public S3 bucket

Dropping a `<obs>.yaml` here makes `GetObservations` fetch that observation
**directly from a public S3 bucket** (e.g. NOAA's `noaa-reanalyses-pds`) into the
cycle directory instead of from R2D2. Files are pulled anonymously (no AWS
credentials) and **nothing is copied into any R2D2 datastore**.

Requires `fetch_obs_from_public_s3: true` in the `experiment.yaml`. The filename must
match the obs operator name in the experiment's `observations` list. Obs without a
matching file are fetched from R2D2 exactly as before.

## Example

```yaml
s3_bucket: noaa-reanalyses-pds

# Full object key with date placeholders YYYY / MM / DD / HH (JJJ = day of year),
# resolved per subwindow time. Exact key mode: one GET, no listing.
s3_key_template: observations/reanalysis/adt/GLORe/jason3/YYYY/MM/iodav2/adt.j3.YYYYMMDD.iodav2.nc

# Below is optional. Override the default subwindow grid (T03/T09/T15/T21, PT6H) to match
# the times the files are actually stored at (here, every 6 hours from 00Z).
obs_timesteps: ['T00']
obs_window_length: P1D
```

### Multiple files per obs (merged)

Sometimes one observation is stored as more than one file. For example, WOD CTD
keeps temperature and salinity in two separate files, even though they cover the
same locations and depths. JEDI expects a single file with both. List each file
under `s3_key_templates`; the task downloads them all and combines them into the
one file JEDI reads:

```yaml
s3_bucket: noaa-reanalyses-pds
s3_key_templates:
  - observations/reanalysis/insitu/wod/ctd/YYYY/MM/iodav3/wod_ctd_t.YYYYMMDD.THHz_iodav3.nc
  - observations/reanalysis/insitu/wod/ctd/YYYY/MM/iodav3/wod_ctd_s.YYYYMMDD.THHz_iodav3.nc
obs_timesteps: ['T00', 'T06', 'T12', 'T18']
obs_window_length: PT6H
```

A missing file for a sub-window falls back to empty obs without stopping the run.

### When the filename can't be built from the date

Sometimes part of a filename isn't set by the date. For example, a processing
timestamp added when the file was made so you can't write the exact key. In that
case add `filename_pattern`: the template becomes a folder prefix that is listed,
and the first file whose name matches the pattern is used. Leave it out for the
normal case above, where the date gives you the whole key.

```yaml
s3_key_template: observations/reanalysis/<inst>/YYYY/MM/DD/
filename_pattern: '*.YYYYMMDD.*.nc'
```
