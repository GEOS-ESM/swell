# Configuring the GEOS-CF R2D2 server on Discover

This page contains the settings specific to the GEOS-CF R2D2 server. For the credentials-file
format, profile-selection order, environment precedence, and datastore overrides, see
[R2D2 v3 credentials and server selection](../configuration_reference/r2d2_v3_credentials.md).

## 1. Configure the server profile

Add the `gmao_server` profile shown in the credentials reference to
`~/.swell/r2d2_credentials.yaml`, using the GEOS-CF server's API URL, port, username, and API
key. Add AWS credentials to that profile only when access to its S3 datastore is required.

## 2. Select the server

Add the profile name to the override passed to `swell create`:

```yaml
r2d2_server: gmao_server
```

For example:

```bash
swell create ingest_background_cf --override ingest_background.yaml
```

The generated experiment configuration carries this selection to all R2D2 tasks, including
background, forecast, observation, diagnostic, and restart operations.

## 3. Check the available datastores

Known datastores on this server include:

| Name | Basedir or storage | AWS credentials required? |
|---|---|---|
| `r2d2-geos-cf` | `/discover/nobackup/projects/gmao/geos_cf_dev` | No |
| `r2d2-experiments-prod-us-east-1` | S3, `us-east-1` | Yes |

List the datastores currently visible to the Discover compute host:

```bash
python src/swell/utilities/scripts/discover_r2d2_datastores.py \
    --platform nccs_discover_sles15 \
    --server gmao_server
```

Normally, leave `r2d2_datastore` unset and let R2D2 apply the server's data-hub and compute-host
priority configuration.

## 4. Verify the selection

Experiment creation and each R2D2 task should log the selected profile:

```text
Loading R2D2 credentials from /home/<user>/.swell/r2d2_credentials.yaml
Using R2D2 credentials for server: 'gmao_server'
YAML r2d2_host ('discover') overrides platform default ('discover-gmao')
```

The datastore-listing command above also verifies the connection: it loads `gmao_server` through
Swell and should return `r2d2-geos-cf` with the expected basedir.
