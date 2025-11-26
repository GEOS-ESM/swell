# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for R2D2 v3 Data Ingestion (Test Suite)

Supports observations
TODO: bias corrections
All metadata comes from experiment.yaml configuration, not filename parsing.
"""

import glob
import netCDF4 as nc
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
import r2d2


class IngestObs(taskBase):
    """
    Task to ingest data to R2D2 v3 (observations)
    
    All metadata comes from experiment.yaml configuration.
    """

    def execute(self) -> None:
        """
        Ingest data to R2D2 v3 using metadata from config.
        
        Supports:
        - Observations: provider, observation_type, file_extension, window_start, window_length
        
        Dry-run mode: Set dry_run: true in config to preview what would be ingested without
        actually storing to R2D2.
        """
        
        # Get config metadata
        ingest_observations = self.config.ingest_observations([])
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
        
        # Track results, with timestamps
        total_ingested = 0
        total_failed = 0
        
        # Process each ingest item
        for item in ingest_observations:
            
            # Get the observation_ingest yaml from the interface/geos_marine/ingest_observations/*
            # similar to how its done for observations/*yaml
            # observation_dict = self.jedi_rendering.render_interface_observations(observation)
            
            item_type = item.get('item_type')
            self.logger.info(f"Processing {item_type} ingestion")
            
            if item_type == 'observation':
                ingested, failed = self.ingest_observations(item, window_begin, window_length, dry_run)
            else:
                self.logger.warning(f"Unknown item type: {item_type}, skipping")
                continue
            
            total_ingested += len(ingested)
            total_failed += len(failed)
            
        # ioda-obs-2024060118-adt_cryosat2n.nc
        # Her bir task and timestep icin following structure yaratmak istiyoruz
        # /discover/nobackup/projects/gmao/soca/obs/ioda/ocean/adt_sentinel6a/2023/07/ioda-obs-2023070218-adt_sentinel6a.nc
        
    
    def retrive_method(self):
        
        if self.config.retrive_methode() == 'cp':
            return self.method_cp()
        elif self.config.retrive_methode() == 'wget':
            return self.method_wget()
        
    
    def method_cp(self, source, destination):
        
        
        return file_path

    def create_empty_ioda(self, filepath, obs_type):
        """Create empty IODA file (Skylab/Ewok approach)."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        ds = nc.Dataset(filepath, 'w', format='NETCDF4')
        ds.createDimension('Location', 0)
        ds.setncattr('_ioda_layout', 'ObsGroup')
        ds.setncattr('_ioda_layout_version', 0)
        ds.setncattr('description', f'Empty placeholder for {obs_type}')
        ds.close()
    
        # Summary
    #     if dry_run:
    #         self.logger.info(f"Would ingest: {total_ingested}")
    #         self.logger.info(f"Would fail: {total_failed}")
    #         self.logger.info("DRY RUN - No files were actually ingested")
    #         self.logger.info("Set dry_run: false in experiment.yaml to actually ingest")
    #     else:
    #         self.logger.info(f"Successfully ingested: {total_ingested}")
    #         self.logger.info(f"Failed: {total_failed}")
    #     self.logger.info("Test ingestion complete!")
    
    # def ingest_observations(self, config, window_start, window_length, dry_run=True):
    #     """Ingest observations using metadata from config."""
    #     ingested = []
    #     failed = []
        
    #     provider = config.get('provider')
    #     source_dir = config.get('source_directory')
    #     obs_types = config.get('observation_types', [])
    #     create_empty = config.get('create_empty_if_missing', True)
        
    #     self.logger.info(f"Ingesting observations from {provider}")
        
    #     for obs in obs_types:
    #         # Handle both formats: string or dict
    #         if isinstance(obs, dict):
    #             obs_name = obs.get('name')
    #             file_ext = obs.get('file_extension', 'nc4')
    #         else:
    #             obs_name = obs
    #             file_ext = 'nc4'
            
    #         self.logger.info(f"Processing observation: {obs_name}")
            
    #         # Build expected filename from metadata
    #         expected_file = f"{provider}.{obs_name}.{window_start}.{file_ext}"
            
    #         # Find file
    #         file_path = self.find_file(source_dir, expected_file)
            
    #         if not file_path:
    #             self.logger.warning(f"File not found: {expected_file}")
    #             if create_empty:
    #                 # Create empty IODA file
    #                 file_path = os.path.join(self.cycle_dir(), expected_file)
    #                 if not dry_run:
    #                     self.create_empty_ioda(file_path, obs_name)
    #                 self.logger.info(f"{'Would create' if dry_run else 'Created'} empty file: {expected_file}")
    #             else:
    #                 failed.append((obs_name, "File not found"))
    #                 continue
            
    #         # Print dry-run info
    #         if dry_run:
    #             self.logger.info(f"  [DRY RUN] Would ingest:")
    #             self.logger.info(f"    File: {file_path if file_path else expected_file}")
    #             self.logger.info(f"    Provider: {provider}")
    #             self.logger.info(f"    Observation Type: {obs_name}")
    #             self.logger.info(f"    File Extension: {file_ext}")
    #             self.logger.info(f"    Window Start: {window_start}")
    #             self.logger.info(f"    Window Length: {window_length}")
    #             ingested.append(file_path if file_path else expected_file)
    #         else:
    #             # Store to R2D2
    #             try:
    #                 r2d2.store(
    #                     item='observation',
    #                     provider=provider,
    #                     observation_type=obs_name,
    #                     file_extension=file_ext,
    #                     window_start=window_start,
    #                     window_length=window_length,
    #                     source_file=file_path
    #                 )
    #                 ingested.append(file_path)
    #                 self.logger.info(f"Successfully ingested {obs_name}")
                    
    #             except Exception as e:
    #                 self.logger.error(f"Failed to ingest {obs_name}: {e}")
    #                 failed.append((obs_name, str(e)))
        
    #     return ingested, failed
