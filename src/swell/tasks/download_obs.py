# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for downloading raw observation files from remote servers.

Downloads native observation files (e.g. HDF5, NetCDF) from either HTTPS
servers such as NASA GES DISC, from public AWS S3 buckets, or from
protected S3 buckets via the NASA Earthdata Cumulus distribution service.

HTTPS authentication is handled via ~/.netrc (same mechanism used by
wget/curl).

S3 (``retrieval_method: s3_public``) uses anonymous boto3 access for
publicly readable buckets (e.g. ``s3://meeo-s5p``).  Requires ``boto3``.

S3 (``retrieval_method: s3_secure``) authentication is done by exchanging
Earthdata credentials (read from ``~/.netrc`` for
``urs.earthdata.nasa.gov``) for temporary AWS credentials via the NASA ASDC
Cumulus S3 distribution endpoint.  Requires ``boto3`` to be installed.
"""

import base64
import datetime
import netrc
import os
import re
import yaml
import isodate
import requests

from swell.tasks.base.task_base import taskBase


class DownloadObs(taskBase):
    """Download raw observation files from a remote server.

    For each observation in ``obs_to_download``, this task reads a per-obs
    YAML from ``download_observations/<obs_name>.yaml`` in the model's
    configuration directory.

    Two retrieval methods are supported:

    ``https`` (default)
        Scrapes an HTML directory listing from ``remote_host`` +
        ``remote_path_template``, matches filenames against
        ``filename_pattern``, and streams files via HTTPS.
        Authentication uses ``~/.netrc``.

    ``s3_public``
        Downloads files from a publicly readable S3 bucket path given by
        ``s3_source`` (e.g. ``s3://meeo-s5p/NRTI/L2__NO2___/YYYY/MM/DD``).
        No credentials required; uses anonymous boto3 access.
        Requires ``boto3``.

    ``s3_secure``
        Downloads files from an S3 bucket path given by ``s3_source``
        (e.g. ``s3://asdc-prod-protected/TEMPO/TEMPO_NO2_L2_V03/YYYY.MM.DD``).
        Temporary AWS credentials are obtained automatically via the NASA
        Earthdata Cumulus distribution endpoint using the Earthdata login
        stored in ``~/.netrc`` for ``urs.earthdata.nasa.gov``.
        Requires ``boto3``.

    Raw obs files are placed in ``<cycle_dir>/download/<obs_name>/``.

    The task can run in dry-run mode (``dry_run: true``) where it only logs
    which files it would download without performing any network calls.

    Args:
        config: Inherited from ``taskBase``.  Relevant keys:

            - ``obs_to_download``: list of obs names whose YAML files are
              present under ``download_observations/``.
            - ``window_length``: ISO-8601 duration (e.g. ``"PT6H"``).
            - ``dry_run``: if ``True``, skip actual downloads.

    Example:
        In a Cylc suite::

            swell task DownloadObs experiment.yaml -d 2024-01-01T00:00:00Z -m geos_cf
    """

    def execute(self) -> None:

        obs_to_download = self.config.obs_to_download([])
        window_length = self.config.window_length()
        dry_run = self.config.dry_run(True)

        if dry_run:
            self.logger.info('DRY RUN MODE - No files will be downloaded')

        window_begin_dto = self.da_window_params.window_begin_iso(window_length, dto=True)
        window_end_dto = self.da_window_params.window_end_iso(window_length, dto=True)

        total_downloaded = 0
        total_failed = 0

        for obs_name in obs_to_download:
            self.logger.info(f'Preparing to download: {obs_name}')

            config_path = os.path.join(
                self.experiment_path(),
                'configuration', 'jedi', 'interfaces',
                self.get_model(),
                'download_observations',
                f'{obs_name}.yaml')

            if not os.path.exists(config_path):
                self.logger.error(f'Config file not found for {obs_name} at {config_path}')
                total_failed += 1
                continue

            with open(config_path, 'r') as fh:
                obs_config = yaml.safe_load(fh)

            downloaded, failed = self._download_obs(
                obs_config, obs_name,
                window_begin_dto, window_end_dto,
                dry_run)

            total_downloaded += downloaded
            total_failed += failed

        self.logger.info('DOWNLOAD SUMMARY')
        verb = 'Would download' if dry_run else 'Downloaded'
        self.logger.info(f'{verb}: {total_downloaded} files')
        self.logger.info(f'Failed: {total_failed} files')

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _download_obs(
        self,
        obs_config: dict,
        obs_name: str,
        window_begin_dto: datetime.datetime,
        window_end_dto: datetime.datetime,
        dry_run: bool,
    ) -> tuple[int, int]:
        """Dispatch to the correct retrieval method and download all files
        for one observation type.

        Returns ``(n_downloaded, n_failed)``.
        """
        retrieval_method = obs_config.get('retrieval_method', 'https')

        if retrieval_method == 's3_public':
            return self._download_obs_s3_public(
                obs_config, obs_name, window_begin_dto, window_end_dto, dry_run)

        if retrieval_method == 's3_secure':
            return self._download_obs_s3_secure(
                obs_config, obs_name, window_begin_dto, window_end_dto, dry_run)

        if retrieval_method == 'cmr':
            return self._download_obs_cmr(
                obs_config, obs_name, window_begin_dto, window_end_dto, dry_run)

        # ------------------------------------------------------------------
        # Default: HTTPS directory listing
        # ------------------------------------------------------------------
        remote_host = obs_config['remote_host']
        remote_path_template = obs_config['remote_path_template']
        filename_pattern = obs_config['filename_pattern']
        max_orbit_dur_str = obs_config.get('max_orbit_duration', 'PT0H')
        max_orbit_dur = isodate.parse_duration(max_orbit_dur_str)

        # Extend the search window backwards so we catch orbits that started
        # before window_begin but still have data inside the window.
        search_start = window_begin_dto - max_orbit_dur
        search_end = window_end_dto

        hour_slots = self._hour_slots(search_start, search_end)

        dest_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)

        # requests.Session uses ~/.netrc automatically for basic-auth
        # endpoints (e.g. GES DISC).  For ASDC Cumulus endpoints that use
        # OAuth, set earthdata_auth: true in the obs YAML to get a fully
        # authenticated session with the accessToken cookie instead.
        if obs_config.get('earthdata_auth', False):
            try:
                session = self._create_earthdata_session()
            except Exception as exc:
                self.logger.abort(f'Failed to create Earthdata session: {exc}')
        else:
            session = requests.Session()

        downloaded = 0
        failed = 0

        for slot_date, slot_hour in hour_slots:
            remote_path = self._resolve_path(remote_path_template, slot_date)
            file_glob = self._resolve_filename(filename_pattern, slot_date, slot_hour)

            file_regex = re.compile(
                '^' + re.escape(file_glob).replace(r'\*', '.*') + '$')

            listing_url = remote_host.rstrip('/') + '/' + remote_path.lstrip('/')

            if dry_run:
                self.logger.info(
                    f'  [DRY RUN] Would list {listing_url} for pattern {file_glob}')
                continue

            try:
                names = self._list_remote_dir(session, listing_url)
            except requests.RequestException as exc:
                self.logger.error(f'Failed to list {listing_url}: {exc}')
                failed += 1
                continue

            matches = [n for n in names if file_regex.match(n)]
            self.logger.info(
                f'  Hour {slot_hour:02d}z on {slot_date.strftime("%Y-%m-%d")}: '
                f'{len(matches)} file(s) found')

            for filename in matches:
                file_url = listing_url.rstrip('/') + '/' + filename
                dest_path = os.path.join(dest_dir, filename)

                if os.path.exists(dest_path):
                    self.logger.info(f'  Already exists, skipping: {filename}')
                    downloaded += 1
                    continue

                try:
                    self._download_file(session, file_url, dest_path)
                    self.logger.info(f'  Downloaded: {filename}')
                    downloaded += 1
                except requests.RequestException as exc:
                    self.logger.error(f'  Failed to download {filename}: {exc}')
                    failed += 1

        return downloaded, failed

    def _download_obs_s3_public(
        self,
        obs_config: dict,
        obs_name: str,
        window_begin_dto: datetime.datetime,
        window_end_dto: datetime.datetime,
        dry_run: bool,
    ) -> tuple[int, int]:
        """Download files for one observation type from a publicly readable
        S3 bucket using anonymous (unsigned) boto3 access.

        The ``obs_config`` dict must contain:

        - ``s3_source``: S3 URI template with ``YYYY``, ``MM``, ``DD``
          placeholders, e.g.
          ``s3://meeo-s5p/NRTI/L2__NO2___/YYYY/MM/DD``.

        Optional keys:

        - ``max_orbit_duration``: ISO-8601 duration; extends the search
          window backwards (default ``PT0H``).

        Returns ``(n_downloaded, n_failed)``.
        """
        try:
            import boto3
            from botocore import UNSIGNED
            from botocore.config import Config as BotocoreConfig
            from botocore.exceptions import BotoCoreError, ClientError
        except ImportError:
            self.logger.abort(
                "boto3 is required for 's3_public' retrieval but is not installed. "
                'Install it with: pip install boto3')

        s3_source_template = obs_config['s3_source']
        max_orbit_dur = isodate.parse_duration(
            obs_config.get('max_orbit_duration', 'PT0H'))

        search_start = window_begin_dto - max_orbit_dur
        search_end = window_end_dto

        dest_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)

        without_scheme = s3_source_template[len('s3://'):]
        bucket, _, prefix_template = without_scheme.partition('/')

        if dry_run:
            for day_date in self._day_slots(search_start, search_end):
                prefix = self._resolve_s3_prefix(prefix_template, day_date)
                self.logger.info(
                    f'  [DRY RUN] Would list s3://{bucket}/{prefix}')
            return 0, 0

        s3_client = boto3.client(
            's3',
            config=BotocoreConfig(signature_version=UNSIGNED))

        downloaded = 0
        failed = 0

        for day_date in self._day_slots(search_start, search_end):
            prefix = self._resolve_s3_prefix(prefix_template, day_date)
            self.logger.info(f'  Listing s3://{bucket}/{prefix}')

            try:
                paginator = s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
                keys = [
                    obj['Key']
                    for page in pages
                    for obj in page.get('Contents', [])
                ]
            except (BotoCoreError, ClientError) as exc:
                self.logger.error(
                    f'  Failed to list s3://{bucket}/{prefix}: {exc}')
                failed += 1
                continue

            if not keys:
                self.logger.info(
                    f'  No objects found under s3://{bucket}/{prefix}')
                continue

            self.logger.info(
                f'  {day_date}: {len(keys)} object(s) found')

            for key in keys:
                filename = os.path.basename(key)
                dest_path = os.path.join(dest_dir, filename)

                if os.path.exists(dest_path):
                    self.logger.info(f'  Already exists, skipping: {filename}')
                    downloaded += 1
                    continue

                try:
                    s3_client.download_file(bucket, key, dest_path)
                    self.logger.info(f'  Downloaded: {filename}')
                    downloaded += 1
                except (BotoCoreError, ClientError) as exc:
                    self.logger.error(
                        f'  Failed to download {filename}: {exc}')
                    failed += 1

        return downloaded, failed

    def _download_obs_s3_secure(
        self,
        obs_config: dict,
        obs_name: str,
        window_begin_dto: datetime.datetime,
        window_end_dto: datetime.datetime,
        dry_run: bool,
    ) -> tuple[int, int]:
        """Download files for one observation type from an S3 bucket using
        temporary credentials obtained via the NASA Earthdata Cumulus
        distribution endpoint.

        The ``obs_config`` dict must contain:

        - ``s3_source``: S3 URI template with ``YYYY``, ``MM``, ``DD``
          placeholders, e.g.
          ``s3://asdc-prod-protected/TEMPO/TEMPO_NO2_L2_V03/YYYY.MM.DD``.

        Optional keys:

        - ``max_orbit_duration``: ISO-8601 duration; extends the search
          window backwards (default ``PT0H``).
        - ``filename_datetime_field``: 0-based index of the start-time
          field when the filename is split on ``_`` (default ``4``,
          matching the TEMPO L2 naming convention).
        - ``filename_datetime_format``: strptime format string for that
          field (default ``%Y%m%dT%H%M%SZ``).

        Returns ``(n_downloaded, n_failed)``.
        """
        try:
            import boto3
            from botocore.exceptions import BotoCoreError, ClientError
        except ImportError:
            self.logger.abort(
                "boto3 is required for 's3_secure' retrieval but is not installed. "
                "Install it with: pip install boto3")

        s3_source_template = obs_config['s3_source']
        max_orbit_dur = isodate.parse_duration(
            obs_config.get('max_orbit_duration', 'PT0H'))

        # Index (0-based) of the start-time token when the filename is
        # split on '_'.  TEMPO L2 filenames look like:
        #   TEMPO_NO2_L2_V03_20231015T180000Z_20231015T190000Z_S001G01.nc
        #                ^^^^ field 4 = start time
        datetime_field = obs_config.get('filename_datetime_field', 4)
        datetime_fmt = obs_config.get('filename_datetime_format', '%Y%m%dT%H%M%SZ')

        # Extend window backwards for long-orbit instruments.
        search_start = window_begin_dto - max_orbit_dur
        search_end = window_end_dto

        # Make both bounds UTC-aware for comparison against parsed timestamps.
        utc = datetime.timezone.utc
        if search_start.tzinfo is None:
            search_start = search_start.replace(tzinfo=utc)
        if window_begin_dto.tzinfo is None:
            window_begin_dto = window_begin_dto.replace(tzinfo=utc)
        if window_end_dto.tzinfo is None:
            window_end_dto = window_end_dto.replace(tzinfo=utc)
        search_end = window_end_dto

        dest_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)

        # Parse the S3 URI: s3://bucket/prefix/template
        without_scheme = s3_source_template[len('s3://'):]
        bucket, _, prefix_template = without_scheme.partition('/')

        if dry_run:
            for day_date in self._day_slots(search_start, search_end):
                prefix = self._resolve_s3_prefix(prefix_template, day_date)
                self.logger.info(
                    f'  [DRY RUN] Would list s3://{bucket}/{prefix}')
            return 0, 0

        # Obtain temporary AWS credentials via Earthdata Cumulus.
        try:
            creds = self._get_earthdata_s3_credentials()
        except Exception as exc:
            self.logger.abort(f'Failed to obtain Earthdata S3 credentials: {exc}')

        s3_client = boto3.client(
            's3',
            aws_access_key_id=creds['accessKeyId'],
            aws_secret_access_key=creds['secretAccessKey'],
            aws_session_token=creds['sessionToken'],
            region_name='us-west-2',
        )

        downloaded = 0
        failed = 0

        for day_date in self._day_slots(search_start, search_end):
            prefix = self._resolve_s3_prefix(prefix_template, day_date)
            self.logger.info(
                f'  Listing s3://{bucket}/{prefix}')

            try:
                paginator = s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
            except (BotoCoreError, ClientError) as exc:
                self.logger.error(
                    f'  Failed to list s3://{bucket}/{prefix}: {exc}')
                failed += 1
                continue

            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    filename = os.path.basename(key)

                    # Skip sidecar/metadata files.
                    if filename.endswith(('.met', '.dmrpp')):
                        continue

                    # Parse the granule start time from the filename.
                    try:
                        parts = filename.split('_')
                        ts_str = parts[datetime_field]
                        # Ensure the format string ends with Z and the
                        # token also ends with Z (strip trailing chars if any).
                        if not ts_str.endswith('Z'):
                            ts_str = ts_str[:15] + 'Z'
                        file_dt = datetime.datetime.strptime(
                            ts_str, datetime_fmt).replace(tzinfo=utc)
                    except (IndexError, ValueError) as exc:
                        self.logger.warning(
                            f'  Could not parse timestamp from {filename}: {exc}')
                        continue

                    # Include files whose granule start time falls within
                    # the extended search window (search_start..window_end).
                    if not (search_start <= file_dt <= search_end):
                        continue

                    dest_path = os.path.join(dest_dir, filename)
                    if os.path.exists(dest_path):
                        self.logger.info(
                            f'  Already exists, skipping: {filename}')
                        downloaded += 1
                        continue

                    try:
                        s3_client.download_file(bucket, key, dest_path)
                        self.logger.info(f'  Downloaded: {filename}')
                        downloaded += 1
                    except (BotoCoreError, ClientError) as exc:
                        self.logger.error(
                            f'  Failed to download {filename}: {exc}')
                        failed += 1

        return downloaded, failed

    def _download_obs_cmr(
        self,
        obs_config: dict,
        obs_name: str,
        window_begin_dto: datetime.datetime,
        window_end_dto: datetime.datetime,
        dry_run: bool,
    ) -> tuple[int, int]:
        """Download files for one observation type by querying the NASA CMR
        API for granule download URLs, then fetching each file via
        authenticated HTTPS.

        The ``obs_config`` dict must contain:

        - ``cmr_short_name``: CMR collection short name, e.g. ``TEMPO_NO2_L2``.

        Optional keys:

        - ``cmr_version``: collection version string, e.g. ``V03``.
        - ``max_orbit_duration``: ISO-8601 duration; extends the temporal
          search backwards (default ``PT0H``).

        Returns ``(n_downloaded, n_failed)``.
        """
        CMR_GRANULES_URL = 'https://cmr.earthdata.nasa.gov/search/granules.json'
        DATA_LINK_REL = 'http://esipfed.org/ns/fedsearch/1.1/data#'
        SKIP_SUFFIXES = ('.met', '.dmrpp', '.xml', '.md5')

        cmr_short_name = obs_config['cmr_short_name']
        cmr_version = obs_config.get('cmr_version', '')
        max_orbit_dur = isodate.parse_duration(
            obs_config.get('max_orbit_duration', 'PT0H'))

        # Extend window backwards for instruments with long scan durations.
        utc = datetime.timezone.utc
        search_start = window_begin_dto - max_orbit_dur
        search_end = window_end_dto
        if search_start.tzinfo is None:
            search_start = search_start.replace(tzinfo=utc)
        if search_end.tzinfo is None:
            search_end = search_end.replace(tzinfo=utc)

        temporal = (f'{search_start.strftime("%Y-%m-%dT%H:%M:%SZ")},'
                    f'{search_end.strftime("%Y-%m-%dT%H:%M:%SZ")}')

        if dry_run:
            self.logger.info(
                f'  [DRY RUN] Would query CMR: short_name={cmr_short_name} '
                f'version={cmr_version} temporal={temporal}')
            return 0, 0

        # CMR search is public — no auth required.
        params = {'short_name': cmr_short_name,
                  'temporal[]': temporal,
                  'page_size': 2000}
        if cmr_version:
            params['version'] = cmr_version

        self.logger.info(
            f'  Querying CMR: short_name={cmr_short_name} '
            f'version={cmr_version} temporal={temporal}')

        try:
            cmr_resp = requests.get(CMR_GRANULES_URL, params=params, timeout=30)
            cmr_resp.raise_for_status()
        except requests.RequestException as exc:
            self.logger.abort(f'CMR query failed: {exc}')

        granules = cmr_resp.json().get('feed', {}).get('entry', [])
        self.logger.info(f'  CMR returned {len(granules)} granule(s)')

        if not granules:
            self.logger.info('  No granules found for this window — nothing to download')
            return 0, 0

        # Authenticated session for ASDC HTTPS downloads.
        try:
            session = self._create_earthdata_session()
        except Exception as exc:
            self.logger.abort(f'Failed to create Earthdata session: {exc}')

        dest_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        os.makedirs(dest_dir, exist_ok=True)

        downloaded = 0
        failed = 0

        for granule in granules:
            # Find the primary HTTPS data link for this granule.
            data_url = None
            for link in granule.get('links', []):
                if DATA_LINK_REL in link.get('rel', '') and \
                        link.get('href', '').startswith('https://'):
                    data_url = link['href']
                    break

            if not data_url:
                self.logger.warning(
                    f'  No HTTPS data link found for granule: '
                    f'{granule.get("id", "unknown")}')
                continue

            filename = os.path.basename(data_url)

            if filename.endswith(SKIP_SUFFIXES):
                continue

            dest_path = os.path.join(dest_dir, filename)
            if os.path.exists(dest_path):
                self.logger.info(f'  Already exists, skipping: {filename}')
                downloaded += 1
                continue

            try:
                self._download_file(session, data_url, dest_path)
                self.logger.info(f'  Downloaded: {filename}')
                downloaded += 1
            except requests.RequestException as exc:
                self.logger.error(f'  Failed to download {filename}: {exc}')
                failed += 1

        return downloaded, failed

    def _create_earthdata_session(self) -> requests.Session:
        """Return an authenticated ``requests.Session`` for NASA Earthdata
        protected HTTPS endpoints (e.g. ``data.asdc.earthdata.nasa.gov``).

        Reads Earthdata credentials from ``~/.netrc`` for
        ``urs.earthdata.nasa.gov`` and performs the four-step Cumulus OAuth
        redirect chain, leaving the session's cookie jar populated with the
        ``accessToken`` cookie that ASDC requires for both HTTPS file access
        and the ``/s3credentials`` endpoint.

        Raises:
            ValueError: if ``~/.netrc`` has no entry for Earthdata or if
                the credential exchange fails.
        """
        DISTRIBUTION_URL = 'https://data.asdc.earthdata.nasa.gov'
        CREDENTIALS_URL = f'{DISTRIBUTION_URL}/s3credentials'
        EARTHDATA_HOST = 'urs.earthdata.nasa.gov'

        # Read username/password from ~/.netrc.
        try:
            nrc = netrc.netrc()
            auth_info = nrc.authenticators(EARTHDATA_HOST)
        except FileNotFoundError:
            raise ValueError('~/.netrc not found. Please create it with '
                             f'credentials for {EARTHDATA_HOST}.')
        if auth_info is None:
            raise ValueError(
                f'No credentials found for {EARTHDATA_HOST} in ~/.netrc. '
                'Add a line: machine urs.earthdata.nasa.gov login <user> password <pass>')

        username, _, password = auth_info
        auth_encoded = base64.b64encode(
            f'{username}:{password}'.encode()).decode()

        session = requests.Session()

        # Step 1 — GET the credentials URL; Cumulus redirects to URS.
        r1 = session.get(CREDENTIALS_URL, allow_redirects=False, timeout=30)
        r1.raise_for_status()
        authorize_url = r1.headers.get('location', '').strip()
        if not authorize_url:
            raise ValueError(
                'No redirect received from Cumulus credentials endpoint. '
                f'Response status: {r1.status_code}')

        # Step 2 — POST credentials to URS to get a grant-code redirect.
        r2 = session.post(
            authorize_url,
            data={'credentials': auth_encoded},
            headers={'Origin': DISTRIBUTION_URL},
            allow_redirects=False,
            timeout=30,
        )
        r2.raise_for_status()
        redirect_url = r2.headers.get('location', '').strip()
        if not redirect_url:
            raise ValueError(
                'No redirect received after posting Earthdata credentials. '
                f'Response status: {r2.status_code}')

        # Step 3 — Follow the full redirect chain; session captures the
        #           accessToken cookie regardless of which hop sets it.
        session.get(redirect_url, allow_redirects=True, timeout=30)

        self.logger.info('Obtained Earthdata session (accessToken cookie set)')
        return session

    def _get_earthdata_s3_credentials(self) -> dict:
        """Obtain temporary AWS credentials via the NASA Earthdata Cumulus
        S3 distribution endpoint.

        Reads Earthdata username and password from ``~/.netrc`` for
        ``urs.earthdata.nasa.gov`` and performs the OAuth redirect chain
        against the ASDC Cumulus distribution URL, returning a dict with
        keys ``accessKeyId``, ``secretAccessKey``, ``sessionToken``, and
        ``expiration``.

        The credentials are valid for **1 hour** (AWS STS role-chaining
        limit).  For DA cycles whose download phase takes longer than 1
        hour a new call to this method will be required; callers should
        catch ``botocore.exceptions.ClientError`` with error code
        ``ExpiredTokenException`` and re-invoke this method.

        **In-region access only**: the ASDC S3 bucket resides in
        ``us-west-2``.  Direct S3 access only works from compute running
        in the same AWS region.

        Raises:
            ValueError: if ``~/.netrc`` has no entry for Earthdata or if
                the credential exchange fails.

        Reference:
            https://data.asdc.earthdata.nasa.gov/s3credentialsREADME
        """
        CREDENTIALS_URL = 'https://data.asdc.earthdata.nasa.gov/s3credentials'

        # Reuse the shared OAuth exchange — session already has the
        # accessToken cookie after this call.
        session = self._create_earthdata_session()

        # Step 4 — Re-request the credentials URL; the session now carries
        #           the accessToken cookie and Cumulus returns JSON with
        #           temporary AWS keys.
        r4 = session.get(CREDENTIALS_URL, timeout=30)
        r4.raise_for_status()
        creds = r4.json()

        required_keys = {'accessKeyId', 'secretAccessKey', 'sessionToken'}
        if not required_keys.issubset(creds):
            raise ValueError(
                f'Unexpected credentials response (missing keys): {creds}')

        self.logger.info(
            f'Obtained temporary S3 credentials from Earthdata Cumulus '
            f'(expires: {creds.get("expiration", "unknown")})')
        return creds

    # ------------------------------------------------------------------
    # Slot/date helpers
    # ------------------------------------------------------------------

    def _hour_slots(
        self,
        search_start: datetime.datetime,
        search_end: datetime.datetime,
    ) -> list[tuple[datetime.datetime, int]]:
        """Return a list of (date, hour) tuples spanning search_start to search_end."""
        slots = []
        current = search_start.replace(minute=0, second=0, microsecond=0)
        while current <= search_end:
            slots.append((current.date(), current.hour))
            current += datetime.timedelta(hours=1)
        return slots

    def _day_slots(
        self,
        search_start: datetime.datetime,
        search_end: datetime.datetime,
    ) -> list[datetime.date]:
        """Return a list of unique date objects from search_start to search_end."""
        days = []
        current = search_start.date()
        end_date = search_end.date()
        while current <= end_date:
            days.append(current)
            current += datetime.timedelta(days=1)
        return days

    # ------------------------------------------------------------------
    # Template resolution helpers
    # ------------------------------------------------------------------

    def _resolve_path(self, template: str, date: datetime.date) -> str:
        """Substitute YYYY, MM, DD, JJJ placeholders in a path template."""
        day_of_year = date.timetuple().tm_yday
        return (template
                .replace('YYYY', f'{date.year:04d}')
                .replace('MM', f'{date.month:02d}')
                .replace('DD', f'{date.day:02d}')
                .replace('JJJ', f'{day_of_year:03d}'))

    def _resolve_filename(self, template: str, date: datetime.date, hour: int) -> str:
        """Substitute date/hour placeholders in a filename pattern."""
        day_of_year = date.timetuple().tm_yday
        return (template
                .replace('YYYY', f'{date.year:04d}')
                .replace('MM', f'{date.month:02d}')
                .replace('DD', f'{date.day:02d}')
                .replace('JJJ', f'{day_of_year:03d}')
                .replace('HH', f'{hour:02d}'))

    def _resolve_s3_prefix(self, template: str, date: datetime.date) -> str:
        """Substitute YYYY, MM, DD in an S3 prefix template.

        Handles both slash-separated (``YYYY/MM/DD``) and dot-separated
        (``YYYY.MM.DD``) date formats that appear in NASA ASDC S3 paths.
        """
        return (template
                .replace('YYYY', f'{date.year:04d}')
                .replace('MM', f'{date.month:02d}')
                .replace('DD', f'{date.day:02d}'))

    # ------------------------------------------------------------------
    # HTTPS helpers
    # ------------------------------------------------------------------

    def _list_remote_dir(self, session: requests.Session, url: str) -> list[str]:
        """Return filenames found in an HTML directory listing at ``url``."""
        response = session.get(url, timeout=(5, 30))
        response.raise_for_status()
        return re.findall(r'href="([^"/][^"]*)"', response.text)

    def _download_file(
        self, session: requests.Session, url: str, dest_path: str
    ) -> None:
        """Stream a remote file to ``dest_path`` in 1 MB chunks.

        Verifies the number of bytes written against the Content-Length 
        in the response header.  If they do not match (truncated download), 
        the partial file is deleted and a requests.RequestException is raised
        so the caller can record the failure and the file will be
        re-attempted on the next run.
        """
        with session.get(url, stream=True, timeout=(5, 30)) as response:
            response.raise_for_status()
            expected = int(response.headers.get('Content-Length', 0))
            written = 0
            with open(dest_path, 'wb') as fh:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    fh.write(chunk)
                    written += len(chunk)

        if expected and written != expected:
            os.remove(dest_path)
            raise requests.RequestException(
                f'Incomplete download: got {written} of {expected} bytes for '
                f'{os.path.basename(dest_path)}'
            )
