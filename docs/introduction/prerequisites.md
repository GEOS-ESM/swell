# Prerequisites

> Documentation sprint placeholder. This topic is currently marked **Missing**.

## Planned coverage

- Required software, accounts, permissions, and external systems.
- Supported Python, Cylc, and platform requirements.
- Pre-installation checks for running Swell.

## R2D2 credentials

Most Swell experiments fetch observations and store backgrounds/analyses through
[R2D2](r2d2_overview.md), so you'll need an R2D2 username and API key before you can run one.
Set these up in `~/.swell/r2d2_credentials.yaml` as described in
[R2D2 v3 credentials](../configuration_reference/r2d2_v3_credentials.md).

If you don't have R2D2 credentials yet, you can still try Swell by passing `-k`/`--skip-r2d2` to
`swell create` — see [QuickStart](quickstart.md#skipping-r2d2-for-a-first-run).
