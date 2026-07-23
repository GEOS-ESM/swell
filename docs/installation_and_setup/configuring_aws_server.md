# Configuring different R2D2 servers and datastores with Swell on Discover

Swell reads R2D2 credentials from `~/.swell/r2d2_credentials.yaml` and connects to the server
specified by `r2d2_server` in `experiment.yaml`. The target datastore is set via `r2d2_datastore`.

| Field | Default | Description |
|-------|---------|-------------|
| `r2d2_server` | *(empty)* | Named entry in `~/.swell/r2d2_credentials.yaml`. If left empty, the first entry in the file is used automatically. |
| `r2d2_datastore` | *(empty)* | Datastore for all fetch/store operations. If left empty, R2D2 picks the highest-priority datastore available on your compute host. |

## 1. Set up ~/.swell/r2d2_credentials.yaml

The credentials file supports named server profiles. Each profile is a named block:

```yaml
# JCSDA R2D2 — public API, no custom server needed
jcsda_server:
  user: <your_username>
  api_key: <your_jcsda_api_key>
  r2d2_host: discover-gmao
  r2d2_compiler: intel

# GMAO R2D2 — custom server with local and S3 datastores
gmao_server:
  user: <your_username>
  api_key: <your_gmao_api_key>
  r2d2_host: discover
  r2d2_compiler: intel
  r2d2_server_host: "http://13.217.72.149"
  r2d2_server_port: "8080"
  # AWS credentials — required only for the S3 datastore
  # aws_access_key_id: <access_key_id>
  # aws_secret_access_key: <secret_access_key>
  # aws_session_token: <session_token>
```

If `r2d2_server` is not set in `experiment.yaml`, Swell automatically selects the first entry in the file.
If `r2d2_datastore` is not set, R2D2 picks the highest-priority datastore available on your compute host for the selected server.

## 2. GMAO R2D2 datastores

| Name | Location | AWS credentials required? |
|------|----------|--------------------------|
| `r2d2-geos-cf-dev` | `/discover/nobackup/projects/gmao/geos_cf_dev/r2d2-geos-cf-dev` | No |
| `r2d2-experiments-prod-us-east-1` | S3 bucket (us-east-1) | Yes |

Use `r2d2-geos-cf-dev` for the Discover-local store (no AWS keys needed). Use `r2d2-experiments-prod-us-east-1` for the S3 datastore - this requires AWS credentials in your credentials file.

To list all datastores accessible from your compute host:

```bash
python src/swell/utilities/scripts/discover_r2d2_datastores.py \
    --platform nccs_discover_sles15 \
    --server gmao_server
```

## 3. Ingest observations

```bash
# Create the experiment
swell create ingest_obs_marine

# Edit experiment.yaml to pick a specific server or datastore (both are optional):
#   r2d2_server: gmao_server          # leave empty to use the first entry in r2d2_credentials.yaml
#   r2d2_datastore: r2d2-geos-cf-dev  # leave empty to let R2D2 pick automatically
#   dry_run: false

# Run the suite
swell launch /path/to/suite/swell-ingest_obs/swell-ingest_obs-suite
```

This runs `IngestObs` for `adt_cryosat2n` across the date range.

### Verify it is stored

```python
python3 -c "
import r2d2
results = r2d2.search(
    item='observation',
    observation_type='adt_cryosat2n',
    window_start='20230702T060000Z',
    window_length='PT6H'
)
print(f'Found {len(results)} records')
for r in results:
    print(r)
"
```
