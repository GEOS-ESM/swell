# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for R2D2 v3 Background/Forecast Ingestion

Ingests model backgrounds and forecasts to R2D2.
"""

import glob
import os
import yaml
from datetime import datetime

import requests

from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
from swell.swell_path import get_swell_path
import r2d2


class IngestBackground(taskBase):
    """Ingest background/forecast fields into R2D2.

    This task reads a list of background/forecast types from the experiment
    configuration (``backgrounds_to_ingest``), loads per‑type metadata from
    modular YAML files under
    ``configuration/jedi/interfaces/geos_marine/ingest_backgrounds/``, resolves
    the input file paths for the current DA window, and optionally stores them
    in R2D2 v3.

    Each YAML file specifies R2D2 metadata (``model``, ``experiment``,
    ``resolution``, ``file_type``, optional ``step``) and retrieval details
    (``retrieval_method``, ``cp_source`` or ``s3_source``).

    The task supports a dry‑run mode that only logs which files would be
    ingested and how they would be labeled in R2D2, without calling
    ``r2d2.store``.

    Args:
        config: Inherited from ``taskBase``. Provides task configuration
            including:

            - ``backgrounds_to_ingest``: List of background/forecast labels
              (e.g. ``['geos_restart', 'mom6_forecast']``).
            - ``window_length``: Length of the DA window as an ISO-8601 duration.
            - ``dry_run``: If ``True``, only log which files would be ingested.
            - ``r2d2_local_path``: Optional local cache path used when writing
              R2D2 configuration (non–dry run).

    Example:
        In a Cylc suite:

        ```bash
        swell task IngestBackground experiment.yaml -d 2021-07-02T06:00:00Z -m geos_marine
        ```

        With an ``experiment.yaml`` snippet:

        ```yaml
        backgrounds_to_ingest: ['geos_restart']
        dry_run: true
        ```
    """

    def execute(self) -> None:

        # Get list of backgrounds to ingest (strings)
        backgrounds_to_ingest = self.config.backgrounds_to_ingest([])

        # Get window parameters
        window_length = self.config.window_length()
        window_begin = self.da_window_params.window_begin_iso(window_length)
        # Check for dry-run mode
        dry_run = self.config.dry_run(True)

        if dry_run:
            self.logger.info("=" * 60)
            self.logger.info(
                "DRY RUN MODE - No files will be ingested to R2D2")
            self.logger.info("=" * 60)
        else:
            create_r2d2_config(
                self.logger,
                self.platform(),
                self.cycle_dir(),
                self.config.r2d2_local_path()
            )

        total_ingested = 0
        total_failed = 0

        # Iterate over the simple list of names
        for bg_name in backgrounds_to_ingest:
            self.logger.info(f"Preparing to ingest: {bg_name}")

            # Locate the configuration file
            config_path = os.path.join(
                get_swell_path(),
                'configuration',
                'jedi',
                'interfaces',
                'geos_marine',
                'ingest_backgrounds',
                f'{bg_name}.yaml')

            if not os.path.exists(config_path):
                self.logger.error(
                    f"Config file not found for {bg_name} at {config_path}")
                total_failed += 1
                continue

            # Load the YAML config
            with open(config_path, 'r') as f:
                bg_config = yaml.safe_load(f)

            # Ingestion
            ingested, failed = self.process_background_config(
                bg_config, bg_name, window_begin, dry_run)

            total_ingested += len(ingested)
            total_failed += len(failed)

        self.logger.info("=" * 60)
        self.logger.info("INGESTION SUMMARY")
        self.logger.info("=" * 60)
        if dry_run:
            self.logger.info(f"Would ingest: {total_ingested} files")
            self.logger.info(f"Would fail: {total_failed} files")
        else:
            self.logger.info(f"Successfully ingested: {total_ingested} files")
            self.logger.info(f"Failed: {total_failed} files")

    def process_background_config(
        self,
        config: dict,
        bg_name: str,
        date: str,
        dry_run: bool,
    ) -> tuple[list[str], list[tuple[str, str]]]:
        """Process a single background configuration file."""
        ingested = []
        failed = []

        # Extract metadata directly from config (flat structure)
        model = config.get('model')
        experiment = config.get('experiment')
        resolution = config.get('resolution')
        file_type = config.get('file_type')
        step = config.get('step', 'PT0H')  # Default to analysis time

        retrieval_method = config.get('retrieval_method')
        source_pattern = config.get(f'{retrieval_method}_source')

        if not source_pattern:
            msg = (
                f"No source pattern found for method '{retrieval_method}' in "
                f"{bg_name}.yaml (expected key '{retrieval_method}_source')."
            )
            self.logger.error(msg)
            raise ValueError(msg)

        # Handle datetime replacements
        dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

        # Support Skylab-style placeholders
        final_pattern = source_pattern.replace('YYYYMMDDHH', '%Y%m%d%H') \
                                      .replace('YYYY', '%Y') \
                                      .replace('MM', '%m') \
                                      .replace('DD', '%d') \
                                      .replace('HH', '%H')

        expected_file = dt.strftime(final_pattern)

        # Match file path using glob
        files_found = glob.glob(expected_file)
        if not files_found:
            self.logger.warning(f"No files matched pattern: {expected_file}")
            return ingested, [(bg_name, "No files found")]
        target_file = files_found[0]

        if dry_run:
            self.logger.info(f"  [DRY RUN] Would ingest:")
            self.logger.info(f"    Name: {bg_name}")
            self.logger.info(f"    Model: {model}")
            self.logger.info(f"    Experiment: {experiment}")
            self.logger.info(f"    Resolution: {resolution}")
            self.logger.info(f"    Method: {retrieval_method}")
            self.logger.info(f"    Source: {target_file}")
            ingested.append(target_file)
        else:
            try:
                # Store to R2D2
                r2d2.store(
                    item='forecast',
                    model=model,
                    experiment=experiment,
                    file_extension=os.path.splitext(target_file)[1][1:],
                    resolution=resolution,
                    step=step,
                    date=date,
                    file_type=file_type,
                    source_file=target_file
                )
            except (ValueError, KeyError, FileNotFoundError,
                    OSError, requests.RequestException) as e:
                self.logger.error(f"Failed to ingest {bg_name}: {e}")
                failed.append((bg_name, str(e)))
            else:
                ingested.append(target_file)
                self.logger.info(f"Successfully ingested {bg_name}")

        return ingested, failed
