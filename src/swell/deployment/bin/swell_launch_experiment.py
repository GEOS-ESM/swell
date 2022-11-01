#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
import click
import os
import subprocess

# local imports
from swell.utilities.logger import Logger
from swell.utilities.welcome_message import write_welcome_message

# --------------------------------------------------------------------------------------------------


class DeployWorkflow():

    def __init__(self, suite_path, experiment_name, no_detach, log_path):

        self.logger = Logger('DeployWorkflow')
        self.suite_path = suite_path
        self.experiment_name = experiment_name
        self.no_detach = no_detach
        self.log_path = log_path

    # ----------------------------------------------------------------------------------------------

    def cylc_run_experiment(self):  # NB: Could be a factory based on workflow_manager

        # Move to the suite path
        os.chdir(self.suite_path)

        # Check flow.cylc is present in the provided suite path
        flow_path = os.path.join(self.suite_path, 'flow.cylc')
        if not os.path.exists(flow_path):
            self.logger.abort('In cylc_run_experiment the suite_path contains no flow.cylc file. ' +
                              'i.e. ' + flow_path + ' does not exist')

        # Check for user provided global.cylc
        if os.path.exists(self.suite_path + 'global.cylc'):
            os.environ['CYLC_CONF_PATH'] = self.suite_path

        # Install the suite
        if self.log_path:
            # Add optional path for workflow engine logging.
            option = '--symlink-dirs=run=' + self.log_path
            subprocess.run(['cylc', 'install', option], check=True)
        else:
            subprocess.run(['cylc', 'install'], check=True)

        # Start the workflow

        if self.no_detach:

            # Start the suite and wait for the workflow to complete.
            subprocess.run(['cylc', 'play', '--no-detach', self.experiment_name], check=True)

        else:

            # Start the suite and return
            subprocess.run(['cylc', 'play', self.experiment_name], check=True)

            # Pre TUI messages
            self.logger.info(' ', False)
            self.logger.info('Workflow is now running... ')
            self.logger.info(' ', False)
            self.logger.info('Use \'\u001b[32mcylc scan\033[0m\' to see running workflows.')
            self.logger.info(' ', False)
            self.logger.info('If the workflow needs to be stopped, close the TUI (if open)')
            self.logger.info('by pressing \'q\' and issue either:')
            self.logger.info(' ', False)
            self.logger.info('  \u001b[32mcylc stop ' + self.experiment_name + '\033[0m')
            self.logger.info(' ', False)
            self.logger.info('or to kill running tasks and stop:')
            self.logger.info(' ', False)
            self.logger.info('  \u001b[32mcylc stop --kill ' + self.experiment_name+ '\033[0m')
            self.logger.info(' ', False)

            # Launch the job monitor
            self.logger.input('Launching the TUI, press \'q\' at any time to exit the TUI')
            self.logger.info(' ', False)
            self.logger.info('TUI can be relaunched with:')
            self.logger.info(' ', False)
            self.logger.info('  \u001b[32mcylc tui ' + self.experiment_name+ '\033[0m')
            self.logger.info(' ', False)
            subprocess.run(['cylc', 'tui', self.experiment_name], check=True)

# --------------------------------------------------------------------------------------------------


@click.command()
@click.option('-p', '--suite_path', 'suite_path', default=None,
              help='Directory containing the suite file needed by the workflow manager')
@click.option('-w', '--workflow_manager', 'workflow_manager', default='cylc',
              help='Workflow manager to be used')
@click.option('-b', '--no-detach', 'no_detach', is_flag=True, default=False,
              help='Tells workflow manager to block until complete')
@click.option('-l', '--log_path', 'log_path', default=None,
              help='Directory to receive workflow manager logging output')
def main(suite_path, workflow_manager, no_detach, log_path):

    # Welcome message
    # ---------------
    write_welcome_message('Launch Experiment')

    # Get the path to where the suite files are located
    # -------------------------------------------------
    if suite_path is None:
        suite_path = os.getcwd()
    else:
        suite_path = os.path.realpath(suite_path)  # Full absolute path

    # Get suite name
    # --------------
    experiment_name = os.path.basename(os.path.normpath(suite_path))

    # Create the deployment object
    # ----------------------------
    deploy_workflow = DeployWorkflow(suite_path, experiment_name, no_detach, log_path)

    # Write some info for the user
    # ----------------------------
    deploy_workflow.logger.info('Launching workflow defined by files in \'' + suite_path + '\'.',
                                False)
    deploy_workflow.logger.info('Experiment name: ' + experiment_name)
    deploy_workflow.logger.info('Workflow manager: ' + workflow_manager)

    # Launch the workflow
    # -------------------
    if workflow_manager == 'cylc':
        deploy_workflow.cylc_run_experiment()


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
