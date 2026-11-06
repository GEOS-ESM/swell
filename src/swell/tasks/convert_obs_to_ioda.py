# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""
Task for converting downloaded raw observation files to IODA format.

Runs an ioda-converters Python script installed in the JEDI bundle's bin
directory or available in converter_path against the raw files produced
by DownloadObs task, writing a single IODA-formatted NetCDF
file per cycle into the cycle's directory.
"""

import glob
import os
import subprocess
import sys
import yaml
from datetime import datetime

from swell.tasks.base.task_base import taskBase


class ConvertObsToIoda(taskBase):
    """Convert downloaded raw observation files to IODA format.

    For each observation in ``obs_to_download``, this task:

    1. Reads a per-obs converter config from
       ``convert_observations/<obs_name>.yaml`` in the experiment's
       configuration directory.
    2. Collects all raw files from ``<cycle_dir>/download/<obs_name>/``.
    3. Runs the ioda-converters Python script by passing all
       input files in a single invocation.
    4. Writes the converted IODA file to
       ``<cycle_dir>/ioda/<obs_name>/<output_filename>``.

    The converter script is invoked as::

        python3 <jedi_bundle>/build/bin/<converter_script>
            -i <file1> <file2> ...
            -o <output_file>
            [additional flags from converter config]

    ``extra_flags`` values may use the ``{window_begin}`` and ``{window_end}``
    placeholders, replaced by the DA window bounds (``%Y-%m-%dT%H:%M:%SZ``), and
    ``{key}`` placeholders for any string/number key of the obs' download YAML
    (after ``download_obs_config_overrides`` are applied), e.g. ``{mls_version}``.
    The input files are those matching the (overridden) ``filename_pattern``.

    Args:
        config: Inherited from ``taskBase``.  Relevant keys:

            - ``obs_to_download``: list of obs names — reuses the same list
              set for ``DownloadObs`` so no extra config key is needed.
            - ``converter_path``: path to directory containing ioda-converter
              scripts. Falls back to ``<experiment>/jedi_bundle/build/bin`` if
              not set.
            - ``dry_run``: if ``True``, log the command but do not run it.
            - ``download_obs_config_overrides``: same overrides as for ``DownloadObs``.

    Example:
        In a Cylc suite::

            swell task ConvertObsToIoda experiment.yaml -d 2024-01-01T00:00:00Z -m geos_cf
    """

    def execute(self) -> None:

        obs_to_convert = self.config.obs_to_download([])
        dry_run = self.config.dry_run(True)

        if dry_run:
            self.logger.info('DRY RUN MODE - No converters will be run')

        download_obs_config_overrides = self.config.download_obs_config_overrides({})

        converter_path = self.config.converter_path('')
        if converter_path:
            converter_bin = converter_path
        else:
            converter_bin = os.path.join(
                self.experiment_path(), 'jedi_bundle', 'build', 'bin')

        cycle_time_dto = self.cycle_time_dto()

        # DA window bounds, available to converter flags as {window_begin} / {window_end}
        window_length = self.config.window_length()
        window_format = '%Y-%m-%dT%H:%M:%SZ'
        window_placeholders = {
            '{window_begin}': self.da_window_params.window_begin_iso(
                window_length, dto=True).strftime(window_format),
            '{window_end}': self.da_window_params.window_end_iso(
                window_length, dto=True).strftime(window_format),
        }

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

            with open(config_path, 'r') as fh:
                conv_config = yaml.safe_load(fh)

            # The download config (with the experiment overrides applied) tells which
            # files were downloaded and provides {key} placeholders for extra_flags.
            dl_config = self._load_download_config(obs_name, download_obs_config_overrides)
            placeholders = {f'{{{key}}}': str(value) for key, value in dl_config.items()
                            if isinstance(value, (str, int, float))}
            placeholders.update(window_placeholders)

            self._run_converter(
                obs_name, conv_config, dl_config, converter_bin, cycle_time_dto,
                placeholders, dry_run)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_download_config(self, obs_name: str, overrides: dict) -> dict:
        """Load download_observations/<obs_name>.yaml with the per-obs
        ``download_obs_config_overrides`` applied (as DownloadObs does).
        Returns an empty dict if there is no download config."""
        download_config_path = os.path.join(
            self.experiment_path(),
            'configuration', 'jedi', 'interfaces',
            self.get_model(),
            'download_observations',
            f'{obs_name}.yaml')

        if not os.path.exists(download_config_path):
            return {}

        with open(download_config_path, 'r') as fh:
            dl_config = yaml.safe_load(fh) or {}

        dl_config.update(overrides.get(obs_name, {}))
        return dl_config

    def _input_glob_from_download_config(self, dl_config: dict) -> str:
        """Derive a glob pattern from the download config's filename_pattern.

        Replaces all date/time placeholders (YYYY, MM, DD, JJJ, HH) with '*'
        so that every file downloaded for this obs matches regardless of timestamp.
        Falls back to '*' if the download config has no filename_pattern.
        """
        pattern = dl_config.get('filename_pattern', '*')
        for placeholder in ('YYYY', 'MM', 'DD', 'JJJ', 'HH'):
            pattern = pattern.replace(placeholder, '*')
        return pattern

    def _run_converter(
        self,
        obs_name: str,
        conv_config: dict,
        dl_config: dict,
        converter_bin: str,
        cycle_time_dto: datetime,
        placeholders: dict,
        dry_run: bool,
    ) -> None:
        """Build and run the ioda-converter command for one observation type."""

        # Collect all downloaded input files using the filename pattern from
        # the download config rather than a separate input_glob in the convert config.
        download_dir = os.path.join(self.cycle_dir(), 'download', obs_name)
        file_glob = self._input_glob_from_download_config(dl_config)
        input_pattern = os.path.join(download_dir, file_glob)
        input_files = sorted(glob.glob(input_pattern))

        if not input_files:
            self.logger.warning(
                f'No input files found for {obs_name} in {download_dir} - skipping')
            return

        self.logger.info(f'Found {len(input_files)} input file(s)')

        # Build output path
        ioda_dir = os.path.join(self.cycle_dir(), 'ioda', obs_name)
        output_filename = cycle_time_dto.strftime(
            conv_config.get('output_filename_template', f'{obs_name}_%Y%m%d%H.nc4'))
        output_file = os.path.join(ioda_dir, output_filename)

        if not dry_run:
            os.makedirs(ioda_dir, exist_ok=True)

        # Locate the converter script
        script_name = conv_config.get('converter_script')
        if not script_name:
            self.logger.abort(f"No 'converter_script' key found for {obs_name}")
        script_path = os.path.join(converter_bin, script_name)

        if not dry_run and not os.path.exists(script_path):
            self.logger.abort(f'Converter not found: {script_path}')

        # Build command: python3 <script> -i <files...> -o <output> [extra flags]
        cmd = [sys.executable, script_path,
               '-i', *input_files,
               '-o', output_file]

        # Append any additional flags defined in the converter config. Values may
        # contain placeholders (see the class docstring).
        for flag, value in conv_config.get('extra_flags', {}).items():
            cmd.append(flag)
            # A YAML null value denotes a value-less command-line switch.
            if value is not None:
                value = str(value)
                for placeholder, replacement in placeholders.items():
                    value = value.replace(placeholder, replacement)
                cmd.append(value)

        self.logger.info(f'  Command: {" ".join(cmd)}')

        if dry_run:
            self.logger.info(f'  [DRY RUN] Would write to: {output_file}')
            return

        result = subprocess.run(cmd, check=False)

        if result.returncode != 0:
            self.logger.abort(
                f'Converter exited with code {result.returncode} for {obs_name}')

        self.logger.info(f'  Converted output: {output_file}')
