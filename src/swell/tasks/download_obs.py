# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for downloading raw observation files from remote servers.

Downloads native observation files (e.g. HDF5, NetCDF) from either HTTPS
servers such as NASA GES DISC, from public AWS S3 buckets, or from
authenticated HTTPS endpoints for NASA ASDC datasets.

``https`` (default)
    Scrapes an HTML directory listing and streams files via HTTPS.
    Authentication uses ``~/.netrc``. With ``index_url`` set, file URLs are
    instead taken from an OGC API - Features index queried for the window
    (e.g. the WOUDC ``data_records`` collection).

``s3_public``
    Downloads from a publicly readable S3 bucket using anonymous boto3
    access (e.g. ``s3://meeo-s5p``).  Requires ``boto3``.

``cmr``
    Queries the NASA CMR API for granule URLs, then downloads via
    authenticated HTTPS (Earthdata ``~/.netrc``).  Use this for NASA ASDC
    datasets such as TEMPO NO2 whose S3 bucket is restricted to AWS
    ``us-west-2``.

``local``
    Links granule files that already exist on a local filesystem (e.g. on
    NCCS Discover) into the download directory instead of downloading them.
    Selected per observation with ``download_obs_config_overrides``.
"""

import base64
import datetime
import glob
import netrc
import os
import re
import time
import yaml
import isodate
import requests
from urllib.parse import urlparse

from swell.tasks.base.task_base import taskBase
from swell.utilities import s3 as swell_s3


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
        Authentication uses ``~/.netrc``. If ``index_url`` is set, the files
        to download are listed by an OGC API - Features index instead (see
        ``_download_obs_https_index``).

    ``cmr``
        Queries the NASA CMR API for granule download URLs and fetches
        each file via authenticated HTTPS (Earthdata ``~/.netrc``).

    ``local``
        Uses a locally archived copy instead of a remote server.  It is not
        the default of any obs YAML; select it with
        ``download_obs_config_overrides`` (``retrieval_method: local`` and
        ``local_file_template: ...``).

    Raw obs files are placed in ``<cycle_dir>/download/<obs_name>/``.

    The task can run in dry-run mode (``dry_run: true``) where it only logs
    which files it would download without performing any network calls.

    Args:
        config: Inherited from ``taskBase``.  Relevant keys:

            - ``obs_to_download``: list of obs names whose YAML files are
              present under ``download_observations/``.
            - ``window_length``: ISO-8601 duration (e.g. ``"PT6H"``).
            - ``dry_run``: if ``True``, skip actual downloads.
            - ``download_obs_config_overrides``: per-obs overrides of the YAML keys.

    Example:
        In a Cylc suite::

            swell task DownloadObs experiment.yaml -d 2024-01-01T00:00:00Z -m geos_cf
    """

    def execute(self) -> None:

        obs_to_download = self.config.obs_to_download([])
        window_length = self.config.window_length()
        dry_run = self.config.dry_run(True)
        download_obs_config_overrides = self.config.download_obs_config_overrides({})

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

            # Apply any per-obs overrides from the experiment config.
            # This allows, e.g., switching s3_source from NRTI to OFFL, or
            # retrieval_method to 'local', via the experiment override YAML
            # without editing source files.
            if obs_name in download_obs_config_overrides:
                obs_config.update(download_obs_config_overrides[obs_name])
                self.logger.info(
                    f'  Applied download_obs_config_overrides for {obs_name}: '
                    f'{download_obs_config_overrides[obs_name]}')

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

        if retrieval_method == 'cmr':
            return self._download_obs_cmr(
                obs_config, obs_name, window_begin_dto, window_end_dto, dry_run)

        if retrieval_method == 'local':
            return self._download_obs_local(
                obs_config, obs_name, window_begin_dto, window_end_dto, dry_run)

        # ------------------------------------------------------------------
        # HTTPS with file URLs resolved through a remote index
        # ------------------------------------------------------------------
        if obs_config.get('index_url'):
            return self._download_obs_https_index(
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

        # Patterns without an hour placeholder (e.g. one file per day) resolve to
        # the same listing and glob for every hour slot; handle each only once.
        seen_slots = set()
        listing_cache = {}

        for slot_date, slot_hour in hour_slots:
            remote_path = self._resolve_path(remote_path_template, slot_date)
            file_glob = self._resolve_filename(filename_pattern, slot_date, slot_hour)

            file_regex = swell_s3.glob_to_regex(file_glob)

            listing_url = remote_host.rstrip('/') + '/' + remote_path.lstrip('/')

            if (listing_url, file_glob) in seen_slots:
                continue
            seen_slots.add((listing_url, file_glob))

            if dry_run:
                self.logger.info(
                    f'  [DRY RUN] Would list {listing_url} for pattern {file_glob}')
                continue

            try:
                if listing_url not in listing_cache:
                    listing_cache[listing_url] = self._list_remote_dir(session, listing_url)
                names = listing_cache[listing_url]
            except requests.RequestException as exc:
                self.logger.error(f'Failed to list {listing_url}: {exc}')
                failed += 1
                continue

            matches = [n for n in names if file_regex.match(n)
                       and self._granule_in_window(n, obs_config, search_start, search_end)]
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

    def _download_obs_https_index(
        self,
        obs_config: dict,
        obs_name: str,
        window_begin_dto: datetime.datetime,
        window_end_dto: datetime.datetime,
        dry_run: bool,
    ) -> tuple[int, int]:
        """Download files listed by a remote JSON index over HTTPS.

        Used by the ``https`` method when ``index_url`` is set, for archives
        whose directory layout cannot be listed per window (e.g. WOUDC, where
        files are stored per station and year and file names follow no
        common pattern).

        ``index_response_format`` selects the index layout.  Only
        ``ogc_features`` (default) is supported: an OGC API - Features
        ``items`` response, whose pages are followed through their ``next``
        links until a page has no ``next`` link or no feature.

        The ``obs_config`` dict must contain:

        - ``index_url``: index endpoint, e.g.
          ``https://api.woudc.org/collections/data_records/items``.

        Optional keys:

        - ``index_params``: extra query parameters (e.g.
          ``{content_category: OzoneSonde}``).  For ``ogc_features``, the
          ``f=json``, ``datetime`` (search interval) and ``limit`` parameters
          are added unless set here.
        - ``index_url_property``: feature property holding the file URL
          (default ``url``).
        - ``index_filename_parts``: number of trailing URL path components
          joined with ``_`` to name the local file, so that files with the
          same name in different remote directories do not collide
          (default 1, the file name only).
        - ``index_page_size``: features requested per page (default 1000).
        - ``index_time_padding``: ISO-8601 duration added on both sides of
          the search interval, for indexes whose times may be shifted from
          the true observation time (default ``PT0H``).  The converter is
          then expected to select the observations of the window exactly.
        - ``max_orbit_duration``: ISO-8601 duration; extends the search
          interval backwards (default ``PT0H``).
        - ``index_retries``: attempts per index page before giving up
          (default 3, at least 1, with a growing pause between attempts).

        ``index_url`` and string ``index_params`` values may use the
        placeholders ``{search_begin}`` and ``{search_end}`` (ISO-8601 UTC)
        and ``{search_begin_date}`` and ``{search_end_date}``
        (``YYYY-MM-DD``).  They are the bounds of the *search interval*:
        the DA window extended by ``max_orbit_duration`` and
        ``index_time_padding``, not the DA window itself.

        An index query that still fails after the retries aborts the task
        (so that the cycle can be retried); an empty index result is not an
        error.

        Returns ``(n_downloaded, n_failed)``.
        """
        index_format = obs_config.get('index_response_format', 'ogc_features')
        if index_format != 'ogc_features':
            self.logger.abort(
                f"Unsupported index_response_format '{index_format}' for {obs_name} "
                "(supported: ogc_features)")

        retries = int(obs_config.get('index_retries', 3))
        if retries < 1:
            self.logger.abort(f'index_retries must be at least 1 for {obs_name}, got {retries}')

        max_orbit_dur = isodate.parse_duration(
            obs_config.get('max_orbit_duration', 'PT0H'))
        padding = isodate.parse_duration(
            obs_config.get('index_time_padding', 'PT0H'))
        search_start = window_begin_dto - max_orbit_dur - padding
        search_end = window_end_dto + padding
        placeholders = {
            'search_begin': search_start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'search_end': search_end.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'search_begin_date': search_start.strftime('%Y-%m-%d'),
            'search_end_date': search_end.strftime('%Y-%m-%d'),
        }
        temporal = f"{placeholders['search_begin']}/{placeholders['search_end']}"
        index_url = self._format_index_template(obs_config['index_url'], placeholders, obs_name)
        params = self._format_index_params(
            obs_config.get('index_params', {}), placeholders, obs_name)
        params.setdefault('f', 'json')
        params.setdefault('datetime', temporal)
        params.setdefault('limit', int(obs_config.get('index_page_size', 1000)))

        if dry_run:
            self.logger.info(f'  [DRY RUN] Would query {index_url} with {params}')
            return 0, 0

        self.logger.info(f'  Querying {index_url} with {params}')
        session = requests.Session()
        indexed_files = []
        seen_urls = set()
        next_url, next_params = index_url, params
        while next_url:
            page = self._query_index_page(
                session, next_url, next_params, retries, obs_name)
            records = self._extract_index_records(page, obs_name)
            # Stop on an empty page even if it advertises a 'next' link, so that
            # a server that always returns one cannot cause an endless loop.
            if not records:
                break
            for record in records:
                file_url, filename = self._index_record_file(record, obs_config, obs_name)
                if file_url and file_url not in seen_urls:
                    indexed_files.append((file_url, filename))
                    seen_urls.add(file_url)
            # The 'next' link carries the full query (including the offset).
            next_url = next((link.get('href') for link in page.get('links', [])
                             if link.get('rel') == 'next'), None)
            next_params = None

        self.logger.info(f'  Index returned {len(indexed_files)} file(s) for {temporal}')
        if not indexed_files:
            self.logger.info('  No files found for this window - nothing to download')
            return 0, 0

        dest_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        os.makedirs(dest_dir, exist_ok=True)
        downloaded = 0
        failed = 0
        for file_url, filename in indexed_files:
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

    def _format_index_template(self, template: str, placeholders: dict, obs_name: str) -> str:
        """Render the search-interval placeholders in an index URL or value."""
        try:
            return template.format(**placeholders)
        except KeyError as exc:
            self.logger.abort(
                f'Unknown index placeholder {exc} in configuration for {obs_name} '
                f'(supported: {", ".join(placeholders)})')

    def _format_index_params(self, params: dict, placeholders: dict, obs_name: str) -> dict:
        """Render the search-interval placeholders in string query parameters."""
        return {
            key: (self._format_index_template(value, placeholders, obs_name)
                  if isinstance(value, str) else value)
            for key, value in params.items()
        }

    def _query_index_page(
        self,
        session: requests.Session,
        url: str,
        params: dict | None,
        retries: int,
        obs_name: str,
    ) -> object:
        """Request and decode one index page, retrying transient failures."""
        for attempt in range(1, retries + 1):
            try:
                response = session.get(url, params=params, timeout=(30, 120))
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                if attempt == retries:
                    self.logger.abort(f'Index query failed for {obs_name} after '
                                      f'{retries} attempt(s): {exc}')
                self.logger.info(f'  Index query attempt {attempt} failed ({exc}), retrying')
                time.sleep(30 * attempt)

    def _extract_index_records(self, page: object, obs_name: str) -> list[dict]:
        """Return the features of one OGC API - Features page."""
        if not isinstance(page, dict):
            self.logger.abort(f'OGC index response for {obs_name} is not an object')
        records = page.get('features', [])
        if not isinstance(records, list):
            self.logger.abort(f'Index response records for {obs_name} are not a list')
        if not all(isinstance(record, dict) for record in records):
            self.logger.abort(f'Index response records for {obs_name} are not objects')
        return records

    def _index_record_file(
        self, record: dict, obs_config: dict, obs_name: str
    ) -> tuple[str | None, str | None]:
        """Resolve one feature into its remote URL and a safe local file name.

        The file name is built from the last ``index_filename_parts`` URL
        path components joined with ``_``; it never contains a path
        separator and cannot be ``.`` or ``..``.  Records without a URL or
        a valid file name are skipped with a warning.
        """
        url_property = obs_config.get('index_url_property', 'url')
        file_url = (record.get('properties') or {}).get(url_property)
        filename = None
        if isinstance(file_url, str) and file_url:
            filename_parts = int(obs_config.get('index_filename_parts', 1))
            path_parts = [p for p in urlparse(file_url).path.split('/') if p]
            filename = self._safe_filename('_'.join(path_parts[-filename_parts:]))
        if not file_url or not filename:
            self.logger.warning(
                f'  Skipping index record without a valid file URL or name for {obs_name}: '
                f'{file_url!r}')
            return None, None
        return file_url, filename

    @staticmethod
    def _safe_filename(name: str) -> str | None:
        """Return ``name`` if it is safe to use as a file name in the download
        directory (no path separator, not empty, ``.`` or ``..``), else None."""
        if not name or name in ('.', '..') or '/' in name or '\\' in name or '\0' in name:
            return None
        return name

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
            from botocore.exceptions import BotoCoreError, ClientError
        except ImportError:
            self.logger.abort(
                "boto3 is required for 's3_public' retrieval but is not installed. "
                'Install it with: pip install boto3')

        s3_source_template = obs_config['s3_source']
        filename_pattern = obs_config.get('filename_pattern', '')
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
                prefix = self._resolve_path(prefix_template, day_date)
                pattern_info = (f' matching {self._resolve_path(filename_pattern, day_date)}'
                                if filename_pattern else '')
                self.logger.info(
                    f'  [DRY RUN] Would list s3://{bucket}/{prefix}{pattern_info}')
            return 0, 0

        s3_client = swell_s3.anonymous_s3_client()

        downloaded = 0
        failed = 0

        for day_date in self._day_slots(search_start, search_end):
            prefix = self._resolve_path(prefix_template, day_date)
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

            # download only files that are in the window
            if filename_pattern:
                valid_hours = [h for d, h in self._hour_slots(search_start, search_end)
                               if d == day_date]
                hours_window = [
                    swell_s3.glob_to_regex(
                        self._resolve_filename(filename_pattern, day_date, h))
                    for h in valid_hours
                ]
                keys = [k for k in keys
                        if any(r.match(os.path.basename(k)) for r in hours_window)]

            utc = datetime.timezone.utc
            s_start = (search_start.replace(tzinfo=utc)
                       if search_start.tzinfo is None else search_start)
            s_end = (search_end.replace(tzinfo=utc)
                     if search_end.tzinfo is None else search_end)
            timestamp_rx = re.compile(r'\d{8}T\d{6}')
            filtered = []
            any_timestamp_found = False
            for k in keys:
                basename = os.path.basename(k)
                matches = timestamp_rx.findall(basename)
                if not matches:
                    filtered.append(k)
                    continue
                any_timestamp_found = True
                granule_start_str = matches[0]
                try:
                    gran_start = datetime.datetime.strptime(
                        granule_start_str, '%Y%m%dT%H%M%S'
                    ).replace(tzinfo=utc)
                except ValueError:
                    filtered.append(k)
                    continue
                if s_start <= gran_start <= s_end:
                    filtered.append(k)
            if any_timestamp_found:
                keys = filtered
            elif not filename_pattern:
                self.logger.warning(
                    f'  {day_date}: no YYYYMMDDTHHmmss timestamp found in filenames ')

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

    def _download_obs_local(
        self,
        obs_config: dict,
        obs_name: str,
        window_begin_dto: datetime.datetime,
        window_end_dto: datetime.datetime,
        dry_run: bool,
    ) -> tuple[int, int]:
        """Link granules that already exist on a local filesystem into the
        download directory (the files are used as is, nothing is extracted).

        The ``obs_config`` dict must contain:

        - ``local_file_template``: ``strftime`` template (``%Y``, ``%m``,
          ``%d``, ``%j``) of the granule path(s) for one day; ``*`` wildcards
          are allowed.  The template is resolved for every day touched by the
          search window.

        Optional keys:

        - ``granule_start_regex`` / ``granule_start_format``: extract the start
          time of a granule from its file name and keep it only if it lies in
          the search window (see ``_granule_in_window``).
        - ``max_orbit_duration``: ISO-8601 duration; extends the search window
          backwards (default ``PT0H``).

        Returns ``(n_linked, n_failed)``.
        """
        file_template = obs_config['local_file_template']
        max_orbit_dur = isodate.parse_duration(
            obs_config.get('max_orbit_duration', 'PT0H'))

        search_start = window_begin_dto - max_orbit_dur
        search_end = window_end_dto

        dest_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)

        linked = 0
        failed = 0

        for day_date in self._day_slots(search_start, search_end):
            file_pattern = day_date.strftime(file_template)
            files = [f for f in sorted(glob.glob(file_pattern))
                     if self._granule_in_window(
                         os.path.basename(f), obs_config, search_start, search_end)]

            if dry_run:
                self.logger.info(
                    f'  [DRY RUN] Would link {len(files)} local file(s) '
                    f'matching {file_pattern}')
                continue

            if not files:
                self.logger.error(f'  No local file found matching {file_pattern}')
                failed += 1
                continue

            for source in files:
                dest_path = os.path.join(dest_dir, os.path.basename(source))
                if not os.path.lexists(dest_path):
                    os.symlink(source, dest_path)
                linked += 1

            self.logger.info(f'  {day_date}: {len(files)} local file(s) linked')

        return linked, failed

    def _granule_in_window(
        self,
        filename: str,
        obs_config: dict,
        search_start: datetime.datetime,
        search_end: datetime.datetime,
    ) -> bool:
        """Return False if the start time encoded in ``filename`` is outside
        ``[search_start, search_end]``.

        The start time is taken from the first match of the
        ``granule_start_regex`` key of ``obs_config`` and parsed with the
        ``granule_start_format`` key (``strptime`` format, UTC).  If either key
        is missing, or the file name does not carry a parsable time, the file
        is kept.
        """
        regex = obs_config.get('granule_start_regex')
        fmt = obs_config.get('granule_start_format')
        if not regex or not fmt:
            return True

        found = re.search(regex, filename)
        if not found:
            return True
        try:
            granule_start = datetime.datetime.strptime(found.group(0), fmt)
        except ValueError:
            return True

        def naive_utc(dto: datetime.datetime) -> datetime.datetime:
            if dto.tzinfo is None:
                return dto
            return dto.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        return naive_utc(search_start) <= granule_start <= naive_utc(search_end)

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

    # ------------------------------------------------------------------
    # Slot/date helpers
    # ------------------------------------------------------------------

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
