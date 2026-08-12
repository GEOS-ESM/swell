# QuickStart

> Documentation sprint placeholder. This topic is currently marked **Missing**.

## Planned coverage

- Verify the Swell and Cylc installations.
- Create a maintained example experiment.
- Launch and monitor the workflow.
- Locate logs and verify the expected result.

## Skipping R2D2 registration and storage

Pass `-k`/`--skip-r2d2` to `swell create` to skip registering the experiment and skip R2D2
store tasks (e.g. `SaveObsDiags`):

```bash
swell create <suite> --skip-r2d2
```

**Note:** this does not remove the need for R2D2 credentials — tasks that *fetch* data
(e.g. `GetObservations`) still run and still require
[R2D2 credentials](../configuration_reference/r2d2_v3_credentials.md) to be configured. Use
`--skip-r2d2` to avoid registering/storing to R2D2, not as a way to run without any R2D2 access
at all.
