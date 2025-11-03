"""
Test Task for R2D2 Observation Ingestion
"""

import glob
import netCDF4 as nc
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
import r2d2


class TestIngestObs(taskBase):

    def execute(self) -> None:
        
        # Get config metadata 
        ingest_items = self.config.ingest_items([])
        window_begin = self.da_window_params.window_begin_iso(self.config.window_offset())
        window_length = self.config.window_length()
        
        create_r2d2_config(
            self.logger, 
            self.platform(), 
            self.cycle_dir(), 
            self.config.r2d2_local_path()
        )
        
        # Process observations
        for item in ingest_items:
            if item.get('item_type') != 'observation':
                continue
                
            provider = item.get('provider')
            source_dir = item.get('source_directory')
            obs_types = item.get('observation_types', [])
            create_empty = item.get('create_empty_if_missing', True)
            
            self.logger.info(f"Ingesting observations from {provider}")
            
            for obs in obs_types:
                # Get metadata from config
                if isinstance(obs, dict):
                    obs_name = obs.get('name')
                    file_ext = obs.get('file_extension', 'nc4')
                else:
                    obs_name = obs
                    file_ext = 'nc4'
                
                self.logger.info(f"Processing: {obs_name}")
                
                expected_file = f"{provider}.{obs_name}.{window_begin}.{file_ext}"
                
                # Find file
                file_path = self.find_file(source_dir, expected_file)
                
                if not file_path:
                    self.logger.warning(f"File not found: {expected_file}")
                    if create_empty:
                        file_path = os.path.join(self.cycle_dir(), expected_file)
                        self.create_empty_ioda(file_path, obs_name)
                        self.logger.info(f"Created empty file")
                    else:
                        continue
                
                # Store to R2D2
                try:
                    r2d2.store(
                        item='observation',
                        provider=provider,          # From config
                        observation_type=obs_name,  # From config
                        file_extension=file_ext,    # From config
                        window_start=window_begin,
                        window_length=window_length,
                        source_file=file_path
                    )
                    self.logger.info(f"✓ Successfully ingested {obs_name}")
                    
                except Exception as e:
                    self.logger.error(f"✗ Failed to ingest {obs_name}: {e}")
        
        self.logger.info("Test ingestion complete!")
    
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
        ds.setncattr('description', f'Empty placeholder for {obs_type}')
        ds.close()

