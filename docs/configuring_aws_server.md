# Quick guide to test R2D2 server with Swell on Discover

[Test outside of Swell](#2-to-test-outside-of-swell)

## 1. To test within Swell:

Make sure `~/.swell/r2d2_credentials.yaml` exists with your user/api_key/host/compiler and AWS credentials for S3 access.

#### a. Set ~/.swell/r2d2_credentials.yaml

```bash
# R2D2 API credentials
user: <your_username>
api_key: <your_key>
r2d2_host: discover
r2d2_compiler: intel
r2d2_server_host: "<enter_ip_address>"
r2d2_server_port: "8080"

# For S3 access
aws_access_key_id : <access_key_id>
aws_secret_access_key : <secret_access_key>
aws_session_token : "<session_token>"

```

#### b. Quick test

Run `IngestObs` directly without launching a full workflow:

```bash
# Create the experiment
swell create ingest_obs_marine

# Edit the generated experiment.yaml:
#   - dry_run: false
#   - obs_to_ingest: ['adt_cryosat2n']

# Run the task
swell task IngestObs /discover/nobackup/fgoktas/SwellExperiments/swell-ingest_obs/swell-ingest_obs-suite/experiment.yaml \
  -d 2021-07-02T06:00:00Z \
  -m geos_marine
```

## 3. Verify it stored

```python
python3 -c "
import r2d2
results = r2d2.search(
    item='observation',
    observation_type='adt_cryosat2n'
)
print(f'Found {len(results)} records')
for r in results:
    print(r)
"
```

## 4. Test fetch

```python
python3 -c "
import r2d2
r2d2.fetch(
    item='observation',
    provider='odas',
    observation_type='adt_cryosat2n',
    file_extension='nc',
    window_start='20210702T090000Z',
    window_length='PT6H',
    target_file='./test_fetch.nc'
)
print('Fetch OK')
"
```

## 5. Full workflow test

```bash
swell create ingest_obs_marine
# Edit experiment.yaml: dry_run: false
# Run the suite
swell launch /path/to/suite/swell-ingest_obs/swell-ingest_obs-suite
```

This runs `IngestObs` for every cycle time across the date range.

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

#### b. Configure AWS credentials:

Set up AWS credentials for S3 access.

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

# Test store (API + S3)
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

# Test fetch (API + S3)
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
EOF
```

