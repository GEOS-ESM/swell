# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os

from generate_aircraft_bias_csv import csv_write

from swell.tasks.base.task_base import taskBase
from swell.utilities.dictionary import write_dict_to_yaml
from swell.utilities.shell_commands import run_track_log_subprocess


# --------------------------------------------------------------------------------------------------


class GsiBcToIoda(taskBase):

    def execute(self):

        # Parse configuration
        # -------------------
        observations = self.config.observations()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        observing_system_records_path = self.config.observing_system_records_path()
        cycle_dir = self.cycle_dir()
        if observing_system_records_path == 'None':
            observing_system_records_path = os.path.join(cycle_dir, 'observing_system_records')

        # Get window beginning time
        window_begin = self.da_window_params.window_begin(window_offset)
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)

        # Prepare dictionary for rendering jedi interface files
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Assemble list of needed sensors
        # -------------------------------
        sensors = []
        sensors_satbias = []
        sensors_tlapse = []

        cycle_time = os.path.normpath(cycle_dir).split('/')[-2]
        for observation in observations:

            print('observation', observation)
            # Open configuration file for observation
            observation_dict = self.jedi_rendering.render_interface_observations(
                observation,
                observing_system_records_path,
                cycle_time
            )

            # Check for sensor key
            try:
                sensor = observation_dict['obs operator']['obs options']['Sensor_ID']
            except Exception:
                continue

            sensors.append(sensor)
            sensors_satbias.append(f'{sensor}.{background_time}.satbias.nc4')
            sensors_tlapse.append(f'{sensor}.{background_time}.tlapse.txt')

        # If there are no sensors then there is nothing to do
        if not sensors:
            self.logger.info('In GsiBcToIoda no radiance observations were found so nothing to do.')
            return

        # Holding directory
        gsi_bc_dir = os.path.join(self.cycle_dir(), 'gsi_bcs')

        # Get list of files from holding directory
        bc_files = glob.glob(os.path.join(gsi_bc_dir, '*.txt'))

        # Assert that the number of files is 3 or less
        self.logger.assert_abort(len(bc_files) <= 3, f'In GsiBcToIoda too many files found in ' +
                                                     f'{gsi_bc_dir}. Expected 3 or less, found ' +
                                                     f'{len(bc_files)}.')

        # Get index of file that contains satbias but not satbiaspc
        satbias_file_index = None
        satbiaspc_file_index = None
        acftbias_file_index = None

        for index, bc_file in enumerate(bc_files):
            if 'satbias' in bc_file and 'satbiaspc' not in bc_file:
                satbias_file_index = index
            if 'satbiaspc' in bc_file:
                satbiaspc_file_index = index
            if 'acftbias' in bc_file:
                acftbias_file_index = index

        # Assert that the files were all found
        self.logger.assert_abort(satbias_file_index is not None,
                                 f'In GsiBcToIoda no satbias file found in {gsi_bc_dir}.')
        self.logger.assert_abort(satbiaspc_file_index is not None,
                                 f'In GsiBcToIoda no satbiaspc file found in {gsi_bc_dir}.')
        if 'aircraft' in observations:
            self.logger.assert_abort(acftbias_file_index is not None,
                                     f'In GsiBcToIoda no acftbias file found in {gsi_bc_dir}.')

        # Create dictionary that will be passed to converter
        satbias_converter_dict = {}

        # Add the files
        satbias_converter_dict['input coeff file'] = bc_files[satbias_file_index]
        satbias_converter_dict['input err file'] = bc_files[satbiaspc_file_index]

        # Add the default predictors
        default_predictors = []
        default_predictors.append('constant')
        default_predictors.append('zenith_angle')
        default_predictors.append('cloud_liquid_water')
        default_predictors.append('lapse_rate_order_2')
        default_predictors.append('lapse_rate')
        default_predictors.append('cosine_of_latitude_times_orbit_node')
        default_predictors.append('sine_of_latitude')
        default_predictors.append('emissivity')
        default_predictors.append('scan_angle_order_4')
        default_predictors.append('scan_angle_order_3')
        default_predictors.append('scan_angle_order_2')
        default_predictors.append('scan_angle')

        gmi_gpm_predictors = []
        gmi_gpm_predictors.append('constant')
        gmi_gpm_predictors.append('zenith_angle')
        gmi_gpm_predictors.append('cosine_of_latitude_times_orbit_node')
        gmi_gpm_predictors.append('lapse_rate_order_2')
        gmi_gpm_predictors.append('lapse_rate')
        gmi_gpm_predictors.append('cloud_liquid_water_order_2')
        gmi_gpm_predictors.append('cloud_liquid_water')
        gmi_gpm_predictors.append('emissivity')
        gmi_gpm_predictors.append('scan_angle_order_4')
        gmi_gpm_predictors.append('scan_angle_order_3')
        gmi_gpm_predictors.append('scan_angle_order_2')
        gmi_gpm_predictors.append('scan_angle')

        satbias_converter_dict['default predictors'] = default_predictors

        satbias_converter_dict_output = []
        for sensor, sensor_satbias in zip(sensors, sensors_satbias):
            output_dict = {}
            output_dict['sensor'] = sensor
            output_dict['output file'] = os.path.join(self.cycle_dir(), sensor_satbias)
            if sensor == 'gmi_gpm':
                output_dict['predictors'] = gmi_gpm_predictors
            else:
                output_dict['predictors'] = default_predictors
            satbias_converter_dict_output.append(output_dict)

        satbias_converter_dict['output'] = satbias_converter_dict_output

        # Write to YAML file
        satbias_converter_yaml = os.path.join(gsi_bc_dir, 'satbias.yaml')
        write_dict_to_yaml(satbias_converter_dict, satbias_converter_yaml)

        # Run IODA satbias converter
        satbias_converter_exe = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                             'satbias2ioda.x')

        run_track_log_subprocess(self.logger, [satbias_converter_exe, satbias_converter_yaml])

        # Run tlapse converter (just a grep)
        for sensor, sensor_tlapse in zip(sensors, sensors_tlapse):
            sensor_tlapse_file = ''
            with open(satbias_converter_dict['input coeff file'], 'r') as f:
                for line in f.readlines():
                    if sensor in line:
                        sensor_tlapse_file = sensor_tlapse_file + ' '.join(line.split()[1:4]) + '\n'
            # Write to tlapse file
            with open(os.path.join(self.cycle_dir(), sensor_tlapse), 'w') as file_open:
                file_open.write(sensor_tlapse_file)

        # Do the conversion of the aircraft bias correction files
        # -------------------------------------------------------
        if 'aircraft' in observations:

            # Input file name
            coefFileName = bc_files[acftbias_file_index]
            coordVariableName = 'MetaData/stationIdentification'
            coordVariableType = 'string'
            coordVariableColumn = 0
            drawVariableType = 'float'

            aircraft_properties = [
                {'csvFileName': f'aircraft_abias_air_constant.{background_time}.csv',
                 'drawVariableName': 'BiasCoefficientValue/constantPredictor',
                 'drawVariableColumn': 2},
                {'csvFileName': f'aircraft_abias_air_ascent.{background_time}.csv',
                 'drawVariableName': 'BiasCoefficientValue/ascentPredictor',
                 'drawVariableColumn': 3},
                {'csvFileName': f'aircraft_abias_air_ascentSquared.{background_time}.csv',
                 'drawVariableName': 'BiasCoefficientValue/ascentSquaredPredictor',
                 'drawVariableColumn': 4},
            ]

            for aircraft_property in aircraft_properties:

                csv_write(os.path.join(self.cycle_dir(), aircraft_property['csvFileName']),
                          coefFileName,
                          coordVariableName,
                          coordVariableType,
                          coordVariableColumn,
                          aircraft_property['drawVariableName'],
                          drawVariableType,
                          aircraft_property['drawVariableColumn'])


# --------------------------------------------------------------------------------------------------
