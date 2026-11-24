import swell.utilities.r2d2_utils as r2d2_utils
from datetime import datetime, timedelta


'''
The `delete` function deletes a data file from `data_store`.
'''


def deregister_observations_in_range(
    observation_type: str,
    provider: str,
    window_length: str,
    file_extension: str,
    data_store: str,
    start_date: str,      # e.g., '2021-07-01T00:00:00Z'
    end_date: str,        # e.g., '2021-07-31T00:00:00Z'
    cycle_hours: list = [0, 6, 12, 18],  # Which hours to check
    dry_run: bool = True
):
    """Delete observations between start_date and end_date."""

    start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
    end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")

    current = start
    deleted = 0

    while current <= end:
        for hour in cycle_hours:
            window_start = current.replace(hour=hour).strftime("%Y-%m-%dT%H:%M:%SZ")

            if dry_run:
                print(f"[DRY RUN] Would delete: {observation_type} at {window_start}")
            else:
                try:
                    r2d2_utils.delete(
                        item='observation',
                        observation_type=observation_type,
                        provider=provider,
                        window_length=window_length,
                        window_start=window_start,
                        file_extension=file_extension,
                        data_store=data_store,
                    )
                    print(f"Deleted: {observation_type} at {window_start}")
                    deleted += 1
                except Exception as e:
                    print(f"Skip (not found or error): {window_start} - {e}")

        current += timedelta(days=1)

    print(f"Total deleted: {deleted}")

# In this below example, adt_cryosat2n observations from 2021-07-01 to 2021-07-31
# will be deleted from R2D2 data store `r2d2-experiments-nccs-gmao`.


deregister_observations_in_range(
    observation_type='adt_cryosat2n',
    provider='odas',
    window_length='PT6H',
    file_extension='nc',
    data_store='r2d2-experiments-nccs-gmao',
    start_date='2021-07-01T00:00:00Z',
    end_date='2021-07-31T00:00:00Z',
    dry_run=True  # Set to False to actually delete
)
