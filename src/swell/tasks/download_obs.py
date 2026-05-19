# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for downloading raw observation files from remote servers.

Downloads native observation files (e.g. HDF5) from HTTPS servers such as
NASA GES DISC prior to ingestion into R2D2. Authentication is handled via
~/.netrc (same mechanism used by wget/curl).
"""

import os
import re
import yaml
import isodate
import datetime
import requests

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes

# --------------------------------------------------------------------------------------------------

task_name = 'DownloadObs'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.questions = [
            qd.dry_run(),
            qd.obs_to_download(),
            qd.window_length()
        ]

# --------------------------------------------------------------------------------------------------

class DownloadObs(taskBase):
    """Download raw observation files from a remote HTTPS server.

    For each observation in ``obs_to_download``, this task reads a per-obs
    YAML from ``download_observations/<obs_name>.yaml`` in the model's
    configuration directory and downloads all files whose start time
    falls within the DA window (extended backwards by ``max_orbit_duration``
    to capture orbits that started before the window but contain data inside
    it).

    Raw obs files are placed in ``<cycle_dir>/download/<obs_name>/``.

    The task can run in dry-run mode (``dry_run: true``) where it only logs
    which files it would download without performing any network calls.

    Args:
        config: Inherited from ``taskBase``.  Relevant keys:

            - ``obs_to_download``: list of YAML filenames with names matching the obs name
              in ``download_observations/``.
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
        """Download all files for one observation type.

        Returns ``(n_downloaded, n_failed)``.
        """
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

        # requests.Session uses ~/.netrc automatically for authentication.
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

    def _list_remote_dir(self, session: requests.Session, url: str) -> list[str]:
        """Return filenames found in an HTML directory listing at ``url``."""
        response = session.get(url, timeout=(5, 30))
        response.raise_for_status()
        return re.findall(r'href="([^"/][^"]*)"', response.text)

    def _download_file(
        self, session: requests.Session, url: str, dest_path: str
    ) -> None:
        """Stream a remote file to ``dest_path`` in 1 MB chunks."""
        with session.get(url, stream=True, timeout=(5, 30)) as response:
            response.raise_for_status()
            with open(dest_path, 'wb') as fh:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    fh.write(chunk)
