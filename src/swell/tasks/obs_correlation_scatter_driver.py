# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import os
import yaml

from swell.tasks.base.task_base import taskBase
from eva.utilities import ioda_definitions
from eva.base import create_and_run

# --------------------------------------------------------------------------------------------------


class ObsCorrelationScatterDriver(taskBase):

  """
  Task to generate config for observation scatter plotting tool
  """

  def execute(self):


    # Stand alone mode: call the diagnostic and return
    # ------------------------------------------------
    if not self.config.get("obs correlation scatter") == None:
      diagnostic_dictionary = self.config.get("obs correlation scatter")
      obs_correlation_scatter_plot(diagnostic_dictionary, self.logger)
      return


    # Workflow mode: create config and call the diagnostic
    # ----------------------------------------------------

    # Dictionary with observation config
    ob_configs = self.config.get("OBSERVATIONS")

    # Inform user if nothing to do
    if not ob_configs:
      self.logger.info("No observations to plot")
      return

    # Loop over observations
    for ob_config in ob_configs:

      # Split the full path into path and filename
      obs_path_file = ob_config["obs space"]["obsdataout"]["obsfile"]
      cycle_dir, obs_file = os.path.split(obs_path_file)

      # Get instrument name
      instrument, instrument_long = ioda_definitions.find_instrument_from_string(obs_file)

      # Create the dictionary to pass to the diagnostic tool
      # ----------------------------------------------------
      obs_plot_dict = {}
      obs_plot_dict["platforms"] = [instrument]
      obs_plot_dict["ioda experiment files"] = obs_path_file
      obs_plot_dict["ioda reference files"] = obs_path_file
      obs_plot_dict["comparisons"] = [["hofx", "GsiHofXBc"],
                                      ["hofx", "ObsValue"],
                                      ["GsiHofXBc", "ObsValue"],
                                      ["omb", "GsiombBc"]]
      obs_plot_dict["marker size"] = 2
      obs_plot_dict["output path"] = os.path.join(cycle_dir, "observation_scatter_plots")
      obs_plot_dict["figure file type"] = 'png'

      # Write the dictionary out to file
      # --------------------------------
      conf_dir = os.path.join(self.config.get("experiment_dir"), self.config.get("current_cycle"))
      conf_output = os.path.join(conf_dir, "ObsCorrelationScatterDriver.yaml")
      with open(conf_output, 'w') as outfile:
        yaml.dump(obs_plot_dict, outfile, default_flow_style=False)

      # Run the diagnostic application
      # ------------------------------
      self.logger.info("Creating the scatter plots for "+instrument+" ("+instrument_long+")")
      create_and_run("ObsCorrelationScatter", obs_plot_dict, self.logger)
