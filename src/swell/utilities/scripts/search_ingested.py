import r2d2
from datetime import datetime

# providers = ['gdas']
# Search for all observations
results = r2d2.search(
    item='observation',
    provider='odas',  # gdas # or None to see all providers
    observation_type='adt_cryosat2n'  # comment out to search only based on provider
)

obs_summary = {}
for result in results:
    obs_type = result.get('observation_type')
    window_start = result.get('window_start')

    if obs_type not in obs_summary:
        obs_summary[obs_type] = []

    obs_summary[obs_type].append(window_start)

print("=" * 50)
print("Available Observations")
print("=" * 50)
for obs_type, dates in sorted(obs_summary.items()):
    dates_sorted = sorted(dates)
    if dates_sorted:
        print(f"\n{obs_type}:")
        print(f"  First: {dates_sorted[0]}")
        print(f"  Last:  {dates_sorted[-1]}")
        print(f"  Total: {len(dates_sorted)} files")
