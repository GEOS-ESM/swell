# Quick guide to test R2D2 server with Swell on Discover

[Test outside of Swell](#2-to-test-outside-of-swell)

## Data stores and servers

Swell supports multiple R2D2 servers and datastores. Each server has its own credentials block in `~/.swell/r2d2_credentials.yaml`, and each server can expose multiple datastores.

### GMAO R2D2 server datastores

| Priority | Name | Location | AWS credentials required? |
|----------|------|----------|--------------------------|
| 1 (default) | `r2d2-geos-cf-dev` | `/discover/nobackup/projects/gmao/geos_cf_dev/r2d2-geos-cf-dev` | No |
| 2 | `r2d2-experiments-prod-us-east-1` | S3 bucket | Yes |

For operations on Discover, `r2d2.fetch()` and `r2d2.store()` will use the highest-priority accessible datastore by default. Pass `data_store=` explicitly to target a specific one.

### JCSDA R2D2 server

Uses the public JCSDA R2D2 API (`r2d2-api.jcsda.org`). No custom server host/port needed.

## 1. To test within Swell:

#### a. Set ~/.swell/r2d2_credentials.yaml

The credentials file supports named server profiles. Each profile is a named block:

```yaml
# JCSDA R2D2 server (public API)
jcsda_server:
  user: <your_username>
  api_key: <your_jcsda_api_key>
  r2d2_host: discover-gmao
  r2d2_compiler: intel

# GMAO R2D2 server (custom server with S3 support)
gmao_server:
  user: <your_username>
  api_key: <your_gmao_api_key>
  r2d2_host: discover-gmao
  r2d2_compiler: intel
  r2d2_server_host: "<server_ip_address>"
  r2d2_server_port: "8080"
  # AWS credentials (only needed to access the S3 datastore)
  # aws_access_key_id: <access_key_id>
  # aws_secret_access_key: <secret_access_key>
  # aws_session_token: <session_token>
```

If no `r2d2_server` is set in `experiment.yaml`, Swell auto-selects the first profile. To use a specific server, set `r2d2_server: gmao_server` in `experiment.yaml`.

#### b. Select server and datastore in experiment.yaml

```yaml
# Selects which credentials block to load from ~/.swell/r2d2_credentials.yaml
# Defaults to 'gmao_server' if not set
r2d2_server: gmao_server

# Datastore to use for fetch/store operations.
# Defaults to 'r2d2-experiments-prod-us-east-1' if not set.
# Leave empty to let R2D2 pick the highest-priority accessible datastore.
# Run src/swell/utilities/scripts/discover_r2d2_datastores.py to list available datastores.
r2d2_datastore: r2d2-experiments-prod-us-east-1
```

#### c. Full workflow test — ingest marine obs to S3

```bash
# Create the experiment
swell create ingest_obs_marine

# Edit experiment.yaml:
#   r2d2_server: gmao_server
#   r2d2_datastore: r2d2-experiments-prod-us-east-1
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

### Test fetch

```python
python3 -c "
import r2d2
r2d2.fetch(
    item='observation',
    provider='odas',
    observation_type='adt_cryosat2n',
    file_extension='nc',
    window_start='20230702T090000Z',
    window_length='PT6H',
    target_file='./test_fetch.nc'
)
print('Fetch OK')
"
```


## 2. To test outside of Swell:

#### a. Set up your environment

Copy or create the required scripts into your working directory:
- [load_r2d2.sh](../src/swell/utilities/scripts/load_r2d2.sh)
- [prod_setup_env.sh](../src/swell/utilities/scripts/prod_setup_env.sh)

Then source them to load R2D2 and set environment variables:

```bash
source load_r2d2.sh
source prod_setup_env.sh
```

#### b. Configure AWS credentials (optional - S3 datastore only):

AWS credentials are only required to access the S3 datastore (`r2d2-experiments-prod-us-east-1`). The local Discover filesystem datastore works without them.

```bash
mkdir -p ~/.aws

cat >> ~/.aws/credentials << 'EOF'
[aws-us-east-1]
aws_access_key_id = ACCESS_KEY
aws_secret_access_key = SECRET_KEY
EOF

cat >> ~/.aws/config << 'EOF'
[profile aws-us-east-1]
region = us-east-1
EOF
```

#### c. Test R2D2 store/fetch from Discover

```bash
python3 << 'EOF'
import r2d2

# List available datastores
print("Data stores:")
for s in r2d2.search(item='data_store'):
    print(f"  {s.get('name')}")

# Test store — uses highest-priority accessible datastore by default
import tempfile, os
test_file = os.path.join(tempfile.gettempdir(), 'r2d2_test.txt')
with open(test_file, 'w') as f:
    f.write("test from Discover\n")

r2d2.store(
    item='observation',
    provider='test',
    observation_type='test_obs',
    file_extension='txt',
    window_start='20240101T120000Z',
    window_length='PT6H',
    source_file=test_file
)
print("Store OK")

# To target the S3 datastore explicitly (requires AWS credentials):
# r2d2.store(..., data_store='r2d2-experiments-prod-us-east-1', source_file=test_file)
# r2d2.fetch(..., data_store='r2d2-experiments-prod-us-east-1', target_file=fetch_file)
EOF
```
