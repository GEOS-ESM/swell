# R2D2 v3 credentials and server selection

Swell loads R2D2 credentials from `~/.swell/r2d2_credentials.yaml`. The file can contain
multiple named profiles, allowing an experiment to select a different R2D2 server without
changing exported environment variables.

## Create the credentials file

```bash
mkdir -p ~/.swell
touch ~/.swell/r2d2_credentials.yaml
chmod 600 ~/.swell/r2d2_credentials.yaml
```

Add one named block for each R2D2 server:

```yaml
jcsda_server:
  user: <jcsda-user>
  api_key: <jcsda-api-key>
  r2d2_host: discover-gmao
  r2d2_compiler: intel

gmao_server:
  user: <gmao-user>
  api_key: <gmao-api-key>
  r2d2_host: discover
  r2d2_compiler: intel
  r2d2_server_host: "http://<ec2-hostname-or-ip>"
  r2d2_server_port: "8080"
```

`r2d2_server_host` and `r2d2_server_port` are not needed for the JCSDA profile because the
R2D2 client uses the production JCSDA API by default.

AWS credentials may be added to a profile when that server exposes an S3 datastore:

```yaml
  aws_access_key_id: <access-key-id>
  aws_secret_access_key: <secret-access-key>
  aws_session_token: <session-token>  # only when temporary credentials are used
```

## Select a different server for an experiment

Set the profile name in an override file:

```yaml
r2d2_server: gmao_server
```

Then create the experiment with that override:

```bash
swell create <suite-name> --override override.yaml
```

Every Swell task that communicates with R2D2 uses the selected profile, including observation,
background, forecast, diagnostic, and restart fetch/store tasks.

The profile is selected in this order:

1. `r2d2_server` in the experiment configuration
2. The `R2D2_SERVER` environment variable
3. The first named profile in `~/.swell/r2d2_credentials.yaml`

Setting `r2d2_server` explicitly is recommended because relying on the order of YAML entries can
select the wrong server after the file is reorganized.

## Configuration precedence

For values inside the selected profile, Swell uses this precedence:

1. An existing environment variable
2. The selected YAML profile
3. The detected platform default, for `R2D2_HOST` and `R2D2_COMPILER`

The relevant environment variables are:

| Environment variable | Profile key | Purpose |
|---|---|---|
| `R2D2_USER` | `user` | R2D2 username |
| `R2D2_API_KEY` | `api_key` | API authentication key |
| `R2D2_HOST` | `r2d2_host` | Compute-host identity sent to R2D2 |
| `R2D2_COMPILER` | `r2d2_compiler` | Compiler identity sent to R2D2 |
| `R2D2_SERVER_HOST` | `r2d2_server_host` | R2D2 API URL |
| `R2D2_SERVER_PORT` | `r2d2_server_port` | R2D2 API port |

Existing environment variables are deliberately not overwritten. Before selecting a different
profile, unset any conflicting values that should come from the profile:

```bash
unset R2D2_USER R2D2_API_KEY R2D2_HOST R2D2_COMPILER
unset R2D2_SERVER_HOST R2D2_SERVER_PORT
```

On Discover, the platform defaults for `R2D2_HOST` and `R2D2_COMPILER` are
`discover-gmao` and `intel`. A profile can override these defaults, as `gmao_server` does above.

## Datastore selection

Normally, leave `r2d2_datastore` unset. R2D2 selects a datastore registered to the compute host
on the selected server according to its data-hub and priority configuration. This keeps datastore
placement in R2D2 rather than embedding storage policy in a Swell experiment.

`r2d2_datastore` remains available as an advanced override for testing or administrative work:

```yaml
r2d2_datastore: <registered-datastore-name>
```

Only use an explicit datastore after confirming that it exists on the selected server and is
available to the configured compute host.

## Legacy single-profile files

Swell still accepts the original root-level format:

```yaml
user: <user>
api_key: <api-key>
r2d2_host: discover-gmao
r2d2_compiler: intel
```

This format cannot switch between named servers. Use named profiles for new configurations.
