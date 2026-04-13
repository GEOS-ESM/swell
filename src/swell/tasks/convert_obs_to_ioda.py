# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for converting downloaded native observation files to IODA format.

Runs an ioda-converters Python script installed in the JEDI bundle's bin
directory against the raw files produced by DownloadObs, writing a single
IODA-formatted NetCDF file per cycle into the cycle's ioda/ directory.
"""

import glob
import os
import subprocess
import sys
import yaml
from datetime import datetime

from swell.tasks.base.task_base import taskBase


class ConvertObsToIoda(taskBase):
    """Convert downloaded native observation files to IODA format.

    For each observation in ``obs_to_download``, this task:

    1. Reads a per-obs converter config from
       ``convert_observations/<obs_name>.yaml`` in the experiment's
       configuration directory.
    2. Collects all raw files from ``<cycle_dir>/download/<obs_name>/``.
    3. Runs the ioda-converters Python script from the JEDI bundle's bin
       directory, passing all input files in a single invocation.
    4. Writes the converted IODA file to
       ``<cycle_dir>/ioda/<obs_name>/<output_filename>``.

    The converter script is invoked as::

        python3 <jedi_bundle>/build/bin/<converter_script>
            -i <file1> <file2> ...
            -o <output_file>
            [additional flags from converter config]

    Args:
        config: Inherited from ``taskBase``.  Relevant keys:

            - ``obs_to_download``: list of obs names — reuses the same list
              set for ``DownloadObs`` so no extra config key is needed.
            - ``dry_run``: if ``True``, log the command but do not run it.

    Example:
        In a Cylc suite::

            swell task ConvertObsToIoda experiment.yaml -d 2024-01-01T00:00:00Z -m geos_cf
    """

    def execute(self) -> None:

        obs_to_convert = self.config.obs_to_download([])
        dry_run = self.config.dry_run(True)

        if dry_run:
            self.logger.info('DRY RUN MODE - No converters will be run')

        jedi_bin = os.path.join(
            self.experiment_path(), 'jedi_bundle', 'build', 'bin')

        cycle_time_dto = self.cycle_time_dto()

        for obs_name in obs_to_convert:
            self.logger.info(f'Converting: {obs_name}')

            config_path = os.path.join(
                self.experiment_path(),
                'configuration', 'jedi', 'interfaces',
                self.get_model(),
                'convert_observations',
                f'{obs_name}.yaml')

            if not os.path.exists(config_path):
                self.logger.error(
                    f'Converter config not found for {obs_name} at {config_path}')
                continue

            with open(config_path, 'r') as fh:
                conv_config = yaml.safe_load(fh)

            self._run_converter(
                obs_name, conv_config, jedi_bin, cycle_time_dto, dry_run)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run_converter(
        self,
        obs_name: str,
        conv_config: dict,
        jedi_bin: str,
        cycle_time_dto: datetime,
        dry_run: bool,
    ) -> None:
        """Build and run the ioda-converter command for one observation type."""

        # Collect all downloaded input files
        download_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        input_pattern = os.path.join(download_dir, conv_config.get('input_glob', '*.h5'))
        input_files = sorted(glob.glob(input_pattern))

        if not input_files:
            self.logger.warning(
                f'No input files found for {obs_name} in {download_dir}')
            return

        self.logger.info(f'  Found {len(input_files)} input file(s)')

        # Build output path
        ioda_dir = os.path.join(self.cycle_dir(), 'ioda', obs_name)
        output_filename = cycle_time_dto.strftime(
            conv_config.get('output_filename_template', f'{obs_name}_%Y%m%d%H.nc'))
        output_file = os.path.join(ioda_dir, output_filename)

        if not dry_run:
            os.makedirs(ioda_dir, exist_ok=True)

        # Locate the converter script in the JEDI bundle bin directory
        script_name = conv_config['converter_script']
        script_path = os.path.join(jedi_bin, script_name)

        if not dry_run and not os.path.exists(script_path):
            self.logger.error(f'Converter script not found: {script_path}')
            return

        # Build command: python3 <script> -i <files...> -o <output> [extra flags]
        cmd = [sys.executable, script_path,
               '-i', *input_files,
               '-o', output_file]

        # Append any additional flags defined in the converter config
        for flag, value in conv_config.get('extra_flags', {}).items():
            cmd += [flag, str(value)]

        self.logger.info(f'  Command: {" ".join(cmd)}')

        if dry_run:
            self.logger.info(f'  [DRY RUN] Would write to: {output_file}')
            return

        result = subprocess.run(cmd, check=False)

        if result.returncode != 0:
            self.logger.error(
                f'Converter exited with code {result.returncode} for {obs_name}')
        else:
            self.logger.info(f'  Converted output: {output_file}')
