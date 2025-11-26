# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for R2D2 v3 Data Ingestion

Supports observations, bias corrections, and backgrounds/forecasts.
All metadata comes from experiment.yaml configuration.
"""

import glob
import netCDF4 as nc
import os
from datetime import datetime

from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
import r2d2


class IngestObs(taskBase):
    """
    Task to ingest data to R2D2 v3 (observations, bias corrections, backgrounds/forecasts).
    
    All metadata comes from experiment.yaml configuration.
    """

    def execute(self) -> None:
        """
        Ingest data to R2D2 v3 using metadata from config.
        
        Supports:
        - Observations: provider, observation_type, file_extension, window_start, window_length
        - Bias corrections: provider, experiment, model, observation_type, file_extension, file_type
        - Backgrounds/Forecasts: model, experiment, file_extension, resolution, step, file_type
        
        Dry-run mode: Set dry_run: true in config to preview what would be ingested without
        actually storing to R2D2.
        """
        
        # Get config metadata
        ingest_items = self.config.ingest_items([])
        window_begin = self.da_window_params.window_begin_iso(self.config.window_offset())
        window_length = self.config.window_length()
        
        # Check for dry-run mode (default True for safety)
        dry_run = self.config.dry_run(True)
        
        if dry_run:
            self.logger.info("="*60)
            self.logger.info("DRY RUN MODE - No files will be ingested to R2D2")
            self.logger.info("="*60)
        else:
            # Setup R2D2 only if not in dry-run mode
            create_r2d2_config(
                self.logger, 
                self.platform(), 
                self.cycle_dir(), 
                self.config.r2d2_local_path()
            )
        
        # Track results
        total_ingested = 0
        total_failed = 0
        
        # Process each ingest item
        for item in ingest_items:
            item_type = item.get('item_type')
            self.logger.info(f"Processing {item_type} ingestion")
            
            if item_type == 'observation':
                ingested, failed = self.ingest_observations(item, window_begin, window_length, dry_run)
            elif item_type == 'bias_correction':
                ingested, failed = self.ingest_bias_corrections(item, window_begin, dry_run)
            elif item_type in ['background', 'forecast']:
                ingested, failed = self.ingest_backgrounds(item, window_begin, dry_run)
            else:
                self.logger.warning(f"Unknown item type: {item_type}, skipping")
                continue
            
            total_ingested += len(ingested)
            total_failed += len(failed)
        
        # Summary
        self.logger.info("="*60)
        self.logger.info("INGESTION SUMMARY")
        self.logger.info("="*60)
        if dry_run:
            self.logger.info(f"Would ingest: {total_ingested}")
            self.logger.info(f"Would fail: {total_failed}")
            self.logger.info("DRY RUN - No files were actually ingested")
            self.logger.info("Set dry_run: false in experiment.yaml to actually ingest")
        else:
            self.logger.info(f"Successfully ingested: {total_ingested}")
            self.logger.info(f"Failed: {total_failed}")
        self.logger.info("Test ingestion complete!")
    
    def ingest_observations(self, config, window_start, window_length, dry_run=True):
        """Ingest observations using metadata from config."""
        ingested = []
        failed = []
        
        provider = config.get('provider')
        source_dir = config.get('source_directory')
        obs_types = config.get('observation_types', [])
        create_empty = config.get('create_empty_if_missing', True)
        filename_pattern = config.get('filename_pattern')
        
        self.logger.info(f"Ingesting observations from {provider}")
        
        for obs in obs_types:
            # Handle both formats: string or dict
            if isinstance(obs, dict):
                obs_name = obs.get('name')
                file_ext = obs.get('file_extension', 'nc4')
            else:
                obs_name = obs
                file_ext = 'nc4'
            
            self.logger.info(f"Processing observation: {obs_name}")
            
            # Build expected filename from metadata
            # -------------------------------------
            dt = datetime.strptime(window_start, "%Y-%m-%dT%H:%M:%SZ")

            if filename_pattern:
                # Use user-provided pattern ("{obs_name}/%Y/%m/%d/ioda-obs-%Y%m%d%H-{obs_name}.nc")
                # First replace placeholders
                pattern = filename_pattern.format(
                    provider=provider,
                    obs_name=obs_name,
                    file_extension=file_ext
                )
                # Then format datetime
                expected_file = dt.strftime(pattern)

            elif provider in ['soca', 'geos_marine']:
                # Marine pattern: ioda-obs-YYYYMMDDHH-obsname.nc
                date_str = dt.strftime("%Y%m%d%H")
                expected_file = f"ioda-obs-{date_str}-{obs_name}.{file_ext}"

            else:
                # Standard/Default pattern: provider.obs.date.nc
                expected_file = f"{provider}.{obs_name}.{window_start}.{file_ext}"
            
            # Find file
            file_path = self.find_file(source_dir, expected_file)
            
            if not file_path:
                self.logger.warning(f"File not found: {expected_file}")
                if create_empty:
                    # Create empty IODA file
                    file_path = os.path.join(self.cycle_dir(), expected_file)
                    if not dry_run:
                        self.create_empty_ioda(file_path, obs_name)
                    self.logger.info(f"{'Would create' if dry_run else 'Created'} empty file: {expected_file}")
                else:
                    failed.append((obs_name, "File not found"))
                    continue
            
            # Print dry-run info
            if dry_run:
                self.logger.info(f"  [DRY RUN] Would ingest:")
                self.logger.info(f"    File: {file_path if file_path else expected_file}")
                self.logger.info(f"    Provider: {provider}")
                self.logger.info(f"    Observation Type: {obs_name}")
                self.logger.info(f"    File Extension: {file_ext}")
                self.logger.info(f"    Window Start: {window_start}")
                self.logger.info(f"    Window Length: {window_length}")
                ingested.append(file_path if file_path else expected_file)
            else:
                # Store to R2D2
                try:
                    r2d2.store(
                        item='observation',
                        provider=provider,
                        observation_type=obs_name,
                        file_extension=file_ext,
                        window_start=window_start,
                        window_length=window_length,
                        source_file=file_path
                    )
                    ingested.append(file_path)
                    self.logger.info(f"Successfully ingested {obs_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to ingest {obs_name}: {e}")
                    failed.append((obs_name, str(e)))
        
        return ingested, failed
    
    def ingest_bias_corrections(self, config, date, dry_run=True):
        """Ingest bias corrections using metadata from config."""
        ingested = []
        failed = []
        
        provider = config.get('provider', 'gsi')
        experiment = config.get('experiment')
        model = config.get('model', 'geos')
        source_dir = config.get('source_directory')
        bias_files = config.get('bias_files', [])
        
        self.logger.info(f"Ingesting bias corrections from {provider}")
        
        for bias_item in bias_files:
            obs_type = bias_item.get('observation_type')
            file_ext = bias_item.get('file_extension')
            file_type = bias_item.get('file_type')
            
            if not all([obs_type, file_ext, file_type]):
                self.logger.warning(f"Incomplete bias file config: {bias_item}")
                failed.append((str(bias_item), "Missing required fields"))
                continue
            
            self.logger.info(f"Processing bias: {obs_type}.{file_ext}")
            
            # Build expected filename from metadata
            expected_file = f"{provider}.{experiment}.bc.{obs_type}.{date}.{file_ext}"
            
            # Find file
            file_path = self.find_file(source_dir, expected_file)
            
            if not file_path:
                self.logger.warning(f"Bias file not found: {expected_file}")
                failed.append((expected_file, "File not found"))
                continue
            
            # Print dry-run info
            if dry_run:
                self.logger.info(f"  [DRY RUN] Would ingest:")
                self.logger.info(f"    File: {file_path}")
                self.logger.info(f"    Item: bias_correction")
                self.logger.info(f"    Model: {model}")
                self.logger.info(f"    Experiment: {experiment}")
                self.logger.info(f"    Provider: {provider}")
                self.logger.info(f"    Observation Type: {obs_type}")
                self.logger.info(f"    File Extension: {file_ext}")
                self.logger.info(f"    File Type: {file_type}")
                self.logger.info(f"    Date: {date}")
                ingested.append(file_path)
            else:
                # Store to R2D2
                try:
                    r2d2.store(
                        item='bias_correction',
                        source_file=file_path,
                        model=model,
                        experiment=experiment,
                        provider=provider,
                        observation_type=obs_type,
                        file_extension=file_ext,
                        file_type=file_type,
                        date=date
                    )
                    ingested.append(file_path)
                    self.logger.info(f"Successfully ingested {expected_file}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to ingest {expected_file}: {e}")
                    failed.append((file_path, str(e)))
        
        return ingested, failed
    
    def ingest_backgrounds(self, config, date, dry_run=True):
        """Ingest backgrounds/forecasts using metadata from config."""
        ingested = []
        failed = []
        
        model = config.get('model', 'geos')
        experiment = config.get('experiment')
        source_dir = config.get('source_directory')
        file_ext = config.get('file_extension', 'nc4')
        resolution = config.get('resolution')
        step = config.get('step', 'P0H')
        file_type = config.get('file_type')
        
        self.logger.info(f"Ingesting backgrounds/forecasts for {model}")
        
        # Build expected filename pattern
        # Format varies by model, using a simple pattern
        expected_pattern = f"*{date}*{file_ext}"
        
        # Find files matching pattern
        search_path = os.path.join(source_dir, "**", expected_pattern)
        files = glob.glob(search_path, recursive=True)
        
        if not files:
            self.logger.warning(f"No background files found matching: {expected_pattern}")
            failed.append((expected_pattern, "No files found"))
            return ingested, failed
        
        # Ingest each file found
        for file_path in files:
            if dry_run:
                self.logger.info(f"  [DRY RUN] Would ingest:")
                self.logger.info(f"    File: {file_path}")
                self.logger.info(f"    Item: forecast")
                self.logger.info(f"    Model: {model}")
                self.logger.info(f"    Experiment: {experiment}")
                self.logger.info(f"    File Extension: {file_ext}")
                self.logger.info(f"    Resolution: {resolution}")
                self.logger.info(f"    Step: {step}")
                self.logger.info(f"    Date: {date}")
                self.logger.info(f"    File Type: {file_type}")
                ingested.append(file_path)
            else:
                try:
                    r2d2.store(
                        item='forecast',
                        model=model,
                        experiment=experiment,
                        file_extension=file_ext,
                        resolution=resolution,
                        step=step,
                        date=date,
                        file_type=file_type,
                        source_file=file_path
                    )
                    ingested.append(file_path)
                    self.logger.info(f"Successfully ingested {os.path.basename(file_path)}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to ingest {file_path}: {e}")
                    failed.append((file_path, str(e)))
        
        return ingested, failed
    
    def find_file(self, source_dir, filename):
        """Find file by name (no parsing, just matching)."""
        pattern = os.path.join(source_dir, "**", filename)
        files = glob.glob(pattern, recursive=True)
        return files[0] if files else None
    
    def create_empty_ioda(self, filepath, obs_type):
        """Create empty IODA file (Skylab/Ewok approach)."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        ds = nc.Dataset(filepath, 'w', format='NETCDF4')
        ds.createDimension('Location', 0)
        ds.setncattr('_ioda_layout', 'ObsGroup')
        ds.setncattr('_ioda_layout_version', 0)
        ds.setncattr('description', f'Empty placeholder for {obs_type}')
        ds.close()
