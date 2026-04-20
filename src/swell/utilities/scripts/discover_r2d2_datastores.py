#!/usr/bin/env python3
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..', 'src'))

from swell.utilities.r2d2 import load_r2d2_module, load_r2d2_credentials
from swell.utilities.logger import Logger

"""
Discover R2D2 datastores available from your compute host.

Run this on the target platform (e.g. Discover) to understand which
datastores exist, which are writable, and which one R2D2 would pick
by default when r2d2_datastore is not set in experiment.yaml.

Usage:
    python scripts/discover_r2d2_datastores.py [--platform PLATFORM] [--server SERVER]

Examples:
    python discover_r2d2_datastores.py
    python discover_r2d2_datastores.py --platform nccs_discover_sles15
    python discover_r2d2_datastores.py --platform nccs_discover_sles15 --server gmao_server
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--platform', default=None,
                        help='Platform name (e.g. nccs_discover_sles15). '
                             'Used to load the R2D2 module and set default host/compiler.')
    parser.add_argument('--server', default=None,
                        help='Server/profile name in ~/.swell/r2d2_credentials.yaml '
                             '(e.g. gmao, jcsda). Leave unset to use root-level credentials.')
    args = parser.parse_args()

    logger = Logger('r2d2-discover')

    # Load R2D2 module (platform-specific lmod)
    if args.platform:
        load_r2d2_module(logger, args.platform)

    # Load credentials
    load_r2d2_credentials(logger, platform=args.platform, r2d2_server=args.server)

    try:
        import r2d2
    except ImportError:
        print('\nERROR: r2d2 module not found. Make sure the R2D2 module is loaded.')
        sys.exit(1)

    # Client context — this is how R2D2 identifies you
    print('\n=== Your R2D2 client context ===')
    print(f'  user     : {r2d2.get_client_user()}')
    print(f'  host     : {r2d2.get_client_host()}')
    print(f'  compiler : {r2d2.get_client_compiler()}')

    # All compute hosts registered in R2D2
    print('\n=== Registered compute hosts ===')
    hosts = r2d2.search(item='compute_host')
    if hosts:
        for h in hosts:
            print(f'  {h}')
    else:
        print('  (none found)')

    # All datastores — these are physical storage locations (Discover directories or S3 buckets)
    print('\n=== All datastores (Discover directories / S3 buckets) ===')
    datastores = r2d2.search(item='data_store')
    if datastores:
        for ds in datastores:
            print(f'  {ds}')
    else:
        print('  (none found)')

    # Writable datastores — the only valid targets for ingest
    print('\n=== Writable datastores (valid ingest targets) ===')
    writable = r2d2.search(item='data_store', read_only=False)
    if writable:
        for ds in writable:
            print(f'  {ds}')
    else:
        print('  (none found)')

    print('\nNote: To target a specific datastore, set in experiment.yaml:')
    print('  r2d2_datastore: <datastore_name>')
    print('\nLeave r2d2_datastore empty to let R2D2 pick the highest-priority')
    print('writable datastore for your compute host automatically.')


if __name__ == '__main__':
    main()
