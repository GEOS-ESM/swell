# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.utilities.shell_commands import run_track_log_subprocess


# --------------------------------------------------------------------------------------------------


def jedi_dictionary_iterator(jedi_config_dict, jedi_rendering, window_type, obs,
                             jedi_forecast_model=None):

    # Assemble configuration YAML file
    # --------------------------------
    for key, value in jedi_config_dict.items():
        if isinstance(value, dict):
            jedi_dictionary_iterator(value, jedi_rendering, window_type, obs, jedi_forecast_model)

        elif isinstance(value, bool):
            continue

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    jedi_dictionary_iterator(item, jedi_rendering, window_type, obs,
                                             jedi_forecast_model)

        else:
            if 'TASKFILL' in value:
                value_file = value.replace('TASKFILL', '')
                value_dict = jedi_rendering.render_interface_model(value_file)

                jedi_config_dict[key] = value_dict

            elif 'SPECIAL' in value:
                value_special = value.replace('SPECIAL', '')
                if value_special == 'observations':
                    observations = []
                    for ob in obs:
                        # Get observation dictionary
                        obs_dict = jedi_rendering.render_interface_observations(ob)

                        # Use the satellite channel record to set the correct channels


                        observations.append(obs_dict)
                    jedi_config_dict[key] = observations

                elif value_special == 'model' and window_type == '4D':
                    model_dict = jedi_rendering.render_interface_model(jedi_forecast_model)
                    jedi_config_dict[key] = model_dict


# ----------------------------------------------------------------------------------------------


def run_executable(logger, cycle_dir, np, jedi_executable_path, jedi_config_file, output_log):

    # Run the JEDI executable
    # -----------------------
    logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')

    command = ['mpirun', '-np', str(np), jedi_executable_path, jedi_config_file]

    # Move to the cycle directory
    # ---------------------------
    os.chdir(cycle_dir)

    # Run command
    # -----------
    run_track_log_subprocess(logger, command, output_log=output_log)


# --------------------------------------------------------------------------------------------------
