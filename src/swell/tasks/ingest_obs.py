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

from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
from swell.utilities.observations import get_ioda_names_list, get_provider_for_observation
from swell.swell_path import get_swell_path
import r2d2


class IngestObs(taskBase):
    """
    Task to ingest observations to R2D2 v3 using modular YAML configuration files.
    
    - 'obs_to_ingest' list comes from experiment.yaml (e.g., ['geos_restart', 'mom6_forecast'])
    - Separate YAML file for each observation type defining retrieval method and metadata.
    """

    def execute(self) -> None:
        
        # Get list of observations to ingest (strings)
        obs_to_ingest = self.config.obs_to_ingest([])

        # Read observation ioda names (for provider lookup)
        self.ioda_names_list = get_ioda_names_list()
        
        # Get window parameters
        window_length = self.config.window_length()
        # window_begin = self.da_window_params.window_begin_iso(window_length)
        window_begin = self.cycle_time()
        
        # Check for dry-run mode (default True for safety)
        dry_run = self.config.dry_run(True)
        
        if dry_run:
            self.logger.info("="*60)
            self.logger.info("DRY RUN MODE - No files will be ingested to R2D2")
            self.logger.info("="*60)
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
            
            # Locate the configuration file
            # Look in the JEDI config directory and get obs yaml file from obs_name (e.g. adt_cryosat2n.yaml)
            config_path = os.path.join(get_swell_path(), 'configuration', 'jedi', 'interfaces', 
                                      'geos_marine', 'ingest_observations', f'{obs_name}.yaml')
            
            if not os.path.exists(config_path):
                self.logger.error(f"Config file not found for {obs_name} at {config_path}")
                total_failed += 1
                continue
                
            # Load the YAML config
            with open(config_path, 'r') as f:
                obs_config = yaml.safe_load(f)
                
            # 3. Perform Ingestion
            ingested, failed = self.process_obs_config(obs_config, obs_name, window_begin, window_length, dry_run)
            
            total_ingested += len(ingested)
            total_failed += len(failed)
            if len(ingested) == 0 and len(failed) == 0:
                total_skipped += 1

        # Summary
        self.logger.info("="*60)
        self.logger.info("INGESTION SUMMARY")
        self.logger.info("="*60)
        if dry_run:
            self.logger.info(f"Would ingest: {total_ingested} files")
            self.logger.info(f"Would fail: {total_failed} files")
        else:
            self.logger.info(f"Successfully ingested: {total_ingested} files")
            self.logger.info(f"Skipped (already exist): {total_skipped} files")
            self.logger.info(f"Failed: {total_failed} files")

    def check_already_in_r2d2(self, obs_name, provider, window_start, window_length):
        """Check if observation already exists in R2D2."""
        try:
            # Query R2D2 to see if this observation already exists
            results = r2d2.fetch(
                item='observation',
                provider=provider,
                observation_type=obs_name,
                window_start=window_start,
                window_length=window_length,
                type='fetch'  # Just check, don't download
            )
            # If fetch succeeds, the observation exists
            return True
        except Exception as e:
            # If fetch fails (e.g., "not found"), it doesn't exist
            self.logger.debug(f"Observation not found in R2D2: {e}")
            return False


    def process_obs_config(self, config, obs_name, window_start, window_length, dry_run):
        """Process a single observation configuration file."""
        ingested = []
        failed = []
        total_skipped = 0

        # Extract metadata
        # obs_metadata = config.get('obs_to_ingest', {})
        provider = get_provider_for_observation(obs_name, self.ioda_names_list, self.logger)

        # Check if already in R2D2
        if self.check_already_in_r2d2(obs_name, provider, window_start, window_length):
            self.logger.info(f"  SKIPPING: {obs_name} already exists in R2D2 for {window_start}")
            return [], []  # Already ingested, skip

        retrieval_method = config.get('retrieval_method') # cp or s3
        
        # Determine source pattern based on method
        source_pattern = config.get(f'{retrieval_method}_source') # cp_source or s3_source
        
        if not source_pattern:
            self.logger.error(f"No source pattern found for method '{retrieval_method}' in {obs_name}.yaml")
            return ingested, [(obs_name, "Missing source pattern")]
        
        # TODO: This will need to be handled different for s3_source and cp_source
        # Handle simple YYYY/MM replacements
        dt = datetime.strptime(window_start, "%Y-%m-%dT%H:%M:%SZ")
        
        # Basic support for Skylab-style placeholders
        final_pattern = source_pattern.replace('YYYYMMDDHH', '%Y%m%d%H') \
                                      .replace('YYYY', '%Y') \
                                      .replace('MM', '%m') \
                                      .replace('DD', '%d') \
                                      .replace('HH', '%H')
        
        expected_file = dt.strftime(final_pattern)
        
        # Handle wildcards if present (glob)
        if '*' in expected_file:
            files_found = glob.glob(expected_file)
            if not files_found:
                self.logger.warning(f"No files matched pattern: {expected_file}")
                return ingested, [(obs_name, "No files found")]
            target_file = files_found[0] # Take first match
        else:
            target_file = expected_file

        # Check existence
        if not os.path.exists(target_file):
            self.logger.warning(f"File not found: {target_file}")
            return ingested, [(obs_name, "File not found")]

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
                    file_extension=os.path.splitext(target_file)[1][1:], # 'nc' from '.nc'
                    window_start=window_start,
                    window_length=window_length,
                    source_file=target_file
                )

                ingested.append(target_file)
                self.logger.info(f"Successfully ingested {obs_name}")
            except Exception as e:
                self.logger.error(f"Failed to ingest {obs_name}: {e}")
                failed.append((obs_name, str(e)))
                
        return ingested, failed
