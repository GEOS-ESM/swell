# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for R2D2 v3 Observation Ingestion

Ingests model observations to R2D2.
"""

import glob
import os
import yaml
from datetime import datetime

import requests

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.utilities.r2d2 import create_r2d2_config
from swell.utilities.observations import get_ioda_names_list, get_provider_for_observation
import r2d2

# --------------------------------------------------------------------------------------------------

task_name = 'IngestObs'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.is_cycling = True
        self.model_dep = True
        self.questions = [
            qd.dry_run(),
            qd.obs_to_ingest(),
            qd.r2d2_local_path(),
            qd.window_length(),
            # qd.window_offset(),
        ]

# --------------------------------------------------------------------------------------------------


class IngestObs(taskBase):
    """Ingest observation files into R2D2 v3.

    This task reads a list of observation types from the experiment configuration
    (``obs_to_ingest``), looks up per-observation metadata from YAML files in the
    experiment's ``configuration/jedi/interfaces/<model-name>/ingest_observations/``
    directory, resolves file paths for the current cycle time, and stores them
    in R2D2.

    The observation YAML files are copied from the swell source code to the
    experiment directory during ``swell create``. Users should modify these files
    in their experiment directory to change file paths or retrieval methods
    without touching the source code.

    The task can run in a "dry run" mode where it only logs which files it would
    ingest, without calling ``r2d2.store``.

    Args:
        config: Inherited from ``taskBase``. Provides task configuration
            including:

            - ``obs_to_ingest``: List of observation names to ingest
              (e.g. ``['adt_cryosat2n']``).
            - ``window_length``: Length of the DA window as an ISO-8601 duration
              (e.g. ``"PT6H"``).
            - ``dry_run``: If ``True``, only log which files would be ingested.
            - ``r2d2_local_path``: Optional local cache path used when writing
              R2D2 configuration (non–dry run).

    Example:
        In a Cylc suite:

        ```bash
        swell task IngestObs experiment.yaml -d 2021-07-02T06:00:00Z -m geos_marine
        ```

        With an ``experiment.yaml`` snippet:

        ```yaml
        obs_to_ingest: ['adt_cryosat2n']
        dry_run: true
        ```
    """

    def execute(self) -> None:

        # Get list of observations to ingest (strings)
        obs_to_ingest = self.config.obs_to_ingest([])

        # Read observation ioda names (for provider lookup)
        self.ioda_names_list = get_ioda_names_list()

        # Get window parameters
        window_length = self.config.window_length()

        # Beginning of the DA window
        window_start = self.da_window_params.window_begin_iso(window_length)

        # Used for file path construction
        cycle_time = self.cycle_time()

        # Check for dry-run mode (default True for safety)
        dry_run = self.config.dry_run(True)

        if dry_run:
            self.logger.info(
                "DRY RUN MODE - No files will be ingested to R2D2")
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
        for obs_name in obs_to_ingest:
            self.logger.info(f"Preparing to ingest: {obs_name}")

            # Locate the configuration file from the experiment directory.
            # Look in the experiment directory for the configuration file.
            config_path = os.path.join(
                self.experiment_path(),
                'configuration',
                'jedi',
                'interfaces',
                self.get_model(),
                'ingest_observations',
                f'{obs_name}.yaml')

            if not os.path.exists(config_path):
                self.logger.error(
                    f"Config file not found for {obs_name} at {config_path}")
                total_failed += 1
                continue

            # Load the YAML config
            with open(config_path, 'r') as f:
                obs_config = yaml.safe_load(f)

            # Ingest
            ingested, failed = self.process_obs_config(
                obs_config, obs_name, cycle_time, window_start, window_length, dry_run)

            total_ingested += len(ingested)
            total_failed += len(failed)

        # Summary
        self.logger.info("INGESTION SUMMARY")
        if dry_run:
            self.logger.info(f"Would ingest: {total_ingested} files")
            self.logger.info(f"Would fail: {total_failed} files")
        else:
            self.logger.info(f"Successfully ingested: {total_ingested} files")
            self.logger.info(f"Failed: {total_failed} files")

    def process_obs_config(
        self,
        config: dict,
        obs_name: str,
        cycle_time: str,
        window_start: str,
        window_length: str,
        dry_run: bool,
    ) -> tuple[list[str], list[tuple[str, str]]]:
        """Process a single observation configuration file."""
        ingested = []
        failed = []

        provider = get_provider_for_observation(
            obs_name, self.ioda_names_list, self.logger)

        retrieval_method = config.get('retrieval_method')  # cp or s3

        # Determine source pattern based on method
        source_pattern = config.get(
            f'{retrieval_method}_source')  # cp_source or s3_source

        if not source_pattern:
            msg = (
                f"No source pattern found for method '{retrieval_method}' in "
                f"{obs_name}.yaml (expected key '{retrieval_method}_source')."
            )
            self.logger.error(msg)
            raise ValueError(msg)

        # Use cycle_time to construct file path
        dt = datetime.strptime(cycle_time, "%Y-%m-%dT%H:%M:%SZ")

        # Basic support for Skylab-style placeholders
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
            return ingested, [(obs_name, "No files found")]
        target_file = files_found[0]

        if dry_run:
            self.logger.info(f"  [DRY RUN] Would ingest:")
            self.logger.info(f"    Obs Name: {obs_name}")
            self.logger.info(f"    Provider: {provider}")
            self.logger.info(f"    Method: {retrieval_method}")
            self.logger.info(f"    Source: {target_file}")
            ingested.append(target_file)
        else:
            try:
                # Store to R2D2
                r2d2.store(
                    item='observation',
                    provider=provider,
                    observation_type=obs_name,
                    file_extension=os.path.splitext(
                        target_file)[1][1:],  # 'nc' from '.nc'
                    window_start=window_start,
                    window_length=window_length,
                    source_file=target_file
                )
            except (ValueError, KeyError, FileNotFoundError,
                    OSError, requests.RequestException) as e:
                self.logger.error(f"Failed to ingest {obs_name}: {e}")
                failed.append((obs_name, str(e)))
            else:
                ingested.append(target_file)
                self.logger.info(f"Successfully ingested {obs_name}")

        return ingested, failed
