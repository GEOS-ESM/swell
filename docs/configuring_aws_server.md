# Quick guide to test R2D2 server with Swell on Discover

[Test outside of Swell](#2-to-test-outside-of-swell)

## Data stores and AWS credentials

This R2D2 server has two registered data stores:

| Priority | Platform | Location | AWS credentials required? |
|----------|----------|----------|--------------------------|
| 1 (default) | `local` | `/discover/nobackup/projects/gmao/geos_cf_dev/r2d2-geos-cf-dev` | **No** |
| 2 (fallback) | `aws` | S3 bucket | Yes |

For operations on Discover, **only `R2D2_USER` and `R2D2_API_KEY` are needed.** `r2d2.fetch()` and `r2d2.store()` will use the local Discover filesystem by default (priority 1). AWS credentials (`aws_access_key_id`, `aws_secret_access_key`, `aws_session_token`) are only required when using the S3 data store (priority 2).

## 1. To test within Swell:

Make sure `~/.swell/r2d2_credentials.yaml` exists with your user, api_key, host, and compiler. AWS credentials are optional and only needed for S3 access.

#### a. Set ~/.swell/r2d2_credentials.yaml

```yaml
# R2D2 API credentials (required)
user: <your_username>
api_key: <your_key>
r2d2_host: discover
r2d2_compiler: intel
r2d2_server_host: "<enter_ip_address>"
r2d2_server_port: "8080"

# AWS credentials (optional - only needed for S3 data store, priority 2)
# aws_access_key_id : <access_key_id>
# aws_secret_access_key : <secret_access_key>
# aws_session_token : "<session_token>"
```

#### b. Full workflow test

Run `IngestObs` directly without launching a full workflow:

```bash
# Create the experiment
swell create ingest_obs_marine

# Edit the generated experiment.yaml:
#   - dry_run: false
#   - obs_to_ingest: ['adt_cryosat2n']

```bash
swell create ingest_obs_marine
# Edit experiment.yaml: dry_run: false
# Run the suite
swell launch /path/to/suite/swell-ingest_obs/swell-ingest_obs-suite
```

This runs `IngestObs` for every cycle time across the date range.

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

#### b. Configure AWS credentials (optional - S3 only):

AWS credentials are **not required** for the default local data store (priority 1). Only configure these if you need to access the S3 data store (priority 2).

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

The default store/fetch uses the local Discover filesystem (priority 1) — no AWS credentials needed.

```bash
python3 << 'EOF'
import r2d2

# Test metadata (API only)
print("Data hubs:")
for h in r2d2.search(item='data_hub'):
    print(f"  {h.get('name')} ({h.get('platform')})")

print("Data stores:")
for s in r2d2.search(item='data_store'):
    print(f"  {s.get('name')}")

print("Compute hosts:")
for c in r2d2.search(item='compute_host'):
    print(f"  {c.get('name')}")

# Test store — uses local Discover filesystem by default (no AWS creds needed)
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
print("Store OK (written to local Discover filesystem, priority 1)")

# Test fetch — same local path
fetch_file = os.path.join(tempfile.gettempdir(), 'r2d2_fetched.txt')
r2d2.fetch(
    item='observation',
    provider='test',
    observation_type='test_obs',
    file_extension='txt',
    window_start='20240101T120000Z',
    window_length='PT6H',
    target_file=fetch_file
)
print(f"Fetch OK: {open(fetch_file).read().strip()}")

# To use S3 (priority 2, requires AWS credentials in ~/.aws/credentials):
# r2d2.store(..., data_store='r2d2-experiments-prod-us-east-1', source_file=test_file)
# r2d2.fetch(..., data_store='r2d2-experiments-prod-us-east-1', target_file=fetch_file)
```

