# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Helpers for anonymous (unsigned) access to publicly readable S3 buckets such as
``noaa-reanalyses-pds``.

These are used to fetch observation files directly from a public bucket into the
experiment cycle directory, without any AWS credentials and without copying the
files into an R2D2 datastore.

Two access modes are supported:

``exact key``
    The full object key is fully determined by the cycle date (the common case
    for the NOAA reanalysis bucket).  ``resolve_template`` builds the key and
    ``download_object`` fetches that single object with one GET -- no listing,
    so over-pulling is impossible.

``list and match``
    Used only when filenames carry a non-deterministic component.  A narrow
    prefix is listed and only keys whose basename matches a regex are returned.
"""

import datetime
import os
import re


def anonymous_s3_client():
    """Return a boto3 S3 client configured for anonymous (unsigned) access."""
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config as BotocoreConfig
    return boto3.client('s3', config=BotocoreConfig(signature_version=UNSIGNED))


def resolve_template(template: str, when: datetime.datetime) -> str:
    """Substitute ``YYYY``/``MM``/``DD``/``JJJ``/``HH`` placeholders in a template
    using the supplied datetime."""
    day_of_year = when.timetuple().tm_yday
    return (template
            .replace('YYYY', f'{when.year:04d}')
            .replace('MM', f'{when.month:02d}')
            .replace('DD', f'{when.day:02d}')
            .replace('JJJ', f'{day_of_year:03d}')
            .replace('HH', f'{when.hour:02d}'))


def download_object(client, bucket: str, key: str, dest_path: str) -> None:
    """Download a single S3 object (exact key) to ``dest_path``.

    Raises ``botocore.exceptions.ClientError`` if the key does not exist so the
    caller can treat a missing object like a missing R2D2 fetch.
    """
    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    client.download_file(bucket, key, dest_path)


def list_matching_keys(client, bucket: str, key_prefix: str,
                       filename_regex: re.Pattern) -> list:
    """Return all object keys under ``key_prefix`` whose basename matches
    ``filename_regex`` (paginated). Scoped to the given prefix only."""
    paginator = client.get_paginator('list_objects_v2')
    keys = []
    for page in paginator.paginate(Bucket=bucket, Prefix=key_prefix):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if filename_regex.match(os.path.basename(key)):
                keys.append(key)
    return keys


def glob_to_regex(filename_glob: str) -> re.Pattern:
    """Compile a shell-style ``*`` filename pattern into an anchored regex."""
    return re.compile('^' + re.escape(filename_glob).replace(r'\*', '.*') + '$')
