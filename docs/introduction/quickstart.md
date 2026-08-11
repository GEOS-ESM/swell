# QuickStart

> Documentation sprint placeholder. This topic is currently marked **Missing**.

## Planned coverage

- Verify the Swell and Cylc installations.
- Create a maintained example experiment.
- Launch and monitor the workflow.
- Locate logs and verify the expected result.

## Skipping R2D2 for a first run

Are you new to Swell and don't have R2D2 credentials set up yet? Pass `-k`/`--skip-r2d2` to
`swell create` to skip registering the experiment and storing products in R2D2:

```bash
swell create <suite> --skip-r2d2
```

This lets you complete a full create -> launch -> monitor cycle to see Swell working end to end
before setting up your [R2D2 credentials](../configuration_reference/r2d2_v3_credentials.md). Tasks that use R2D2 (fetching observations, storing backgrounds/analyses) will be skipped rather
than run.
