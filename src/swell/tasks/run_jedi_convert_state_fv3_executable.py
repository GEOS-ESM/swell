# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import isodate
import os
from ruamel.yaml import YAML

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.run_jedi_executables import run_executable


# --------------------------------------------------------------------------------------------------


class RunJediConvertStateFv3Executable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:
        """Converts a single FV3 atmospheric background file from one cubed-sphere
        resolution to a user-specified target resolution using fv3jedi_convertstate.x.

        This task is designed to be called in parallel within the convert_state suite,
        one instance per background file in the DA window. The specific background file
        to process is identified via the ensemble-packet index (-p flag), which is used
        to index into the background_window_times list from the suite configuration.

        Background files are expected to follow the JEDI-standard naming convention
        produced by GetBackgroundGeosExperiment (e.g. bkg.2021-12-11T21:00:00Z.nc4).
        The converted output file is written as bkg_c{target_res}.{time_iso}.nc4 and
        is later collected by TarBackgroundGeosConvertState.
        """

        # Jedi application name
        # ---------------------
        jedi_application = 'convert_state_fv3'

        # Read configuration
        # ------------------
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        background_window_times = self.config.background_window_times()
        target_horizontal_resolution = self.config.target_horizontal_resolution()

        # Determine which background file this task instance is responsible for.
        # The ensemble-packet index (-p) is reused as a background-file index.
        # -----------------------------------------------------------------------
        bkg_idx = int(self.get_ensemble_packet())
        bkg_time_offset_str = background_window_times[bkg_idx]
        bkg_time_offset_dur = isodate.parse_duration(bkg_time_offset_str)
        bkg_time_dto = self.cycle_time_dto() + bkg_time_offset_dur
        bkg_time_iso = bkg_time_dto.strftime(datetime_formats['directory_format'])

        self.logger.info(f' Converting background file for time: {bkg_time_iso}'
                         f' (offset {bkg_time_offset_str}, index {bkg_idx})')

        # Populate jedi interface template dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('background_time_iso', bkg_time_iso)
        self.jedi_rendering.add_key('target_horizontal_resolution', target_horizontal_resolution)
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc())
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc())
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('cycle_dir', self.cycle_dir())

        # JEDI config and log file paths (include bkg index to avoid collisions)
        # -----------------------------------------------------------------------
        jedi_config_file = os.path.join(self.cycle_dir(),
                                        f'jedi_{jedi_application}_{bkg_idx:02d}_config.yaml')
        output_log_file = os.path.join(self.cycle_dir(),
                                       f'jedi_{jedi_application}_{bkg_idx:02d}_log.log')

        # Render the OOPS configuration
        # -----------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(jedi_application,
                                                                None,
                                                                jedi_forecast_model)

        yaml = YAML()
        yaml.default_flow_style = False
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open)

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()
        np = eval(str(model_component_meta['total_processors']))

        # Jedi executable path
        # --------------------
        jedi_executable = model_component_meta['executables'][jedi_application]
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                            'build', 'bin', jedi_executable)

        # Run the executable
        # ------------------
        if not generate_yaml_and_exit:
            self.logger.info(f'Running {jedi_executable_path} with {np} processors.')
            run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                           jedi_config_file, output_log_file)
        else:
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
