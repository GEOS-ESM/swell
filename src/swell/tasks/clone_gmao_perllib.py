# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class CloneGmaoPerllib(taskBase):

    def execute(self) -> None:

        # Get experiment directory where GMAO_perllib will be cloned/linked
        swell_exp_path = self.experiment_path()
        experiment_perllib_path = os.path.join(swell_exp_path, 'GMAO_perllib')

        # Get the existing location of GMAO_perllib
        existing_perllib_path = self.config.gmao_perllib_path(None)
        gmao_perllib_tag = self.config.gmao_perllib_tag(None)

        # Set the default tag to g1.0.1 if not specified
        if gmao_perllib_tag is None:
            gmao_perllib_tag = 'g1.0.1'
            self.logger.info("The target branch for gmao_perllib, 'gmao_perllib_branch', "
                             + "is unspecified in the experiment config file, "
                             + f"defaulting to {gmao_perllib_tag}")

        # Don't clone or link if GMAO_perllib already exists in experiment directory
        if os.path.exists(experiment_perllib_path):
            self.logger.info(f"{experiment_perllib_path} exists, defaulting to this installation")

        # Clone from github if existing perllib is unspecified
        elif existing_perllib_path is None:
            self.logger.info("The path to GMAO_perllib, 'gmao_perllib_path'"
                             + "has not been specified in experiment.yaml. "
                             + "CloneGMAOPerllib will now attempt to clone "
                             + "it from Github, which will fail on compute "
                             + "nodes with no internet access.")
            subprocess.run(f"git clone -b {gmao_perllib_tag} "
                           + "https://github.com/GEOS-ESM/GMAO_perllib.git "
                           + os.path.join(experiment_path()))

        # Link to existing GMAO_perllib
        elif os.path.exists(existing_perllib_path):

            # Check that the tag of the existing repository matches the intended tag
            existing_tag = self.get_tag(existing_perllib_path)
            if not existing_tag or existing_tag != gmao_perllib_tag:
                self.logger.debug("The git tag of the existing GMAO_perllib repository, "
                                  + f"{existing_perllib_path}, does not match the specified tag "
                                  + f"{gmao_perllib_tag}. Please check the directory and make "
                                  + "sure the installation is correct.")

            # Link the existing directory to the experiment directory
            os.symlink(existing_perllib_path, experiment_perllib_path)

        # Check to make sure the path contains acquire and acquire_obsys
        if len(list(set(['acquire', 'acquire_obsys'])
                    & set(os.listdir(experiment_perllib_path)))) < 2:
            self.logger.abort(f"{experiment_perllib_path} does not contain "
                              + "acquire and acquire_obsys")

    # --------------------------------------------------------------------------------------------------

    def get_tag(self, path):
        try:
            prc = subprocess.run(['git', 'describe'], capture_output=True, text=True, check=True)
            return prc.stdout.strip()
        except subprocess.CalledProcessError:
            return None

# --------------------------------------------------------------------------------------------------
