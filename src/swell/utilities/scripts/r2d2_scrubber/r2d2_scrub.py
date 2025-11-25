#!/usr/bin/env python3
"""R2D2 Experiment Scrubber - Deletes experiments past their lifetime"""

import os
import yaml
from datetime import datetime, timezone
import r2d2

# Lifetimes (days)
LIFETIME_DAYS = {
    "debug": 14,
    "science": 180,      # 6 months
    "publication": 1825, # 5 years
    "release": None,     # indefinite storage
}

# Load credentials from YAML
CREDS_FILE = os.path.join(os.path.dirname(__file__), 'r2d2_credentials.yaml')
with open(CREDS_FILE) as f:
    creds = yaml.safe_load(f)

# Set environment variables (r2d2 library reads these)
os.environ['R2D2_USER'] = creds['user']
os.environ['R2D2_API_KEY'] = creds['api_key']
os.environ['R2D2_HOST'] = creds['host']
os.environ['R2D2_COMPILER'] = creds['compiler']

def main(args):
    now = datetime.now(timezone.utc)
    scrub = args.scrub

    # TODO: Add logging
    print(f"{now.isoformat()} Starting R2D2 scrubber")
    
    # Get optional filters from config
    users_to_scrub = creds.get('users_to_scrub', [])
    compute_host = creds.get('compute_host', None)
    experiments = []
    
    if users_to_scrub:
        # Search for experiments belonging to users to scrub
        print(f"Searching experiments for users: {', '.join(users_to_scrub)}")
        for user in users_to_scrub:
            user_experiments = r2d2.search(item="experiment", user=user)
            experiments.extend(user_experiments)
    
    deleted = 0
    skipped = 0
    print(experiments)
    for experiment in experiments:
        lifetime = experiment["lifetime"]
        start_date = experiment["start_date"]
        lifetime_days = LIFETIME_DAYS["lifetime"]

        if lifetime_days is None:
            continue  # skipping "release" (indefinite storage)

        age_days = (now - start_date).days
        
        if age_days >= lifetime_days:
            name = experiment["name"]
            exp_user = experiment.get("user", "unknown")
            if scrub:
                print(f"Deleting {name} (user={exp_user}, lifetime={lifetime}, age={age_days}d)")
                try:
                    # R2D2Index.delete_experiment_by_name(name=name, attributes={})
                    r2d2.deregister(item='experiment', name=name)
                    deleted += 1
                except Exception as exc:
                    print(f"  Failed to delete {name}: {exc}")
            else:
                deleted += 1
                print(f" [DRY-RUN] Would delete {name} (user={exp_user}, lifetime={lifetime}, age={age_days}d)")
        else:
            skipped += 1

    if scrub:
        print(f"\nDone: {deleted} deleted, {skipped} skipped (from {len(experiments)} experiments)")
    else:
        print(f"\n[DRY-RUN] Done: {deleted} would be deleted, {skipped} would be skipped (from {len(experiments)} experiments)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="R2D2 experiment scrubber",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--scrub",
        action="store_true",
        help="Actually delete experiments (default is dry-run mode)"
    )

    args = parser.parse_args()
    main(args)
