# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import os
import shutil
import subprocess

from swell.tasks.base.task_base import taskBase
from swell.utilities.git_utils import git_got


# --------------------------------------------------------------------------------------------------


class BuildJedi(taskBase):

    def execute(self):
        """
          Comment here
        """

        cfg = self.config

        # Path to JEDI build
        jedi_build = self.config.get('jedi_build')

        # Get path to jedi executable
        if 'executable' in cfg.keys() and 'existing build directory' in cfg['build jedi'].keys():

            # Check for presence of required executable and link build directory
            # ------------------------------------------------------------------
            ex_build_dir = os.path.join(cfg['build jedi']['existing build directory'])

            if os.path.exists(os.path.join(ex_build_dir, 'bin', cfg['executable'])):
                self.logger.info("Suitable JEDI build found, linking build directory. Warning: " +
                                 "problems will follow if the loaded modules are not consistent " +
                                 "with those used to build this version of JEDI.")
                # Remove any exisiting
                if os.path.isdir(jedi_build):
                    shutil.rmtree(jedi_build)
                # Link directory
                os.symlink(ex_build_dir, jedi_build)

        else:

            # Build the JEDI code
            # -------------------
            # No jedi executable was found
            self.logger.info('No jedi executable found... \nBuilding Jedi...')

            # Get bundle and suite directories
            bundle_dir = cfg['bundle']
            suite_dir = cfg['suite_dir']

            # Get the repos from the repo dict and clone them if they haven't already been cloned
            repo_dict = cfg['build jedi']['bundle repos']

            # Prep ecbuild string
            ecb_tmp = 'ecbuild_bundle( PROJECT {} GIT "https://github.com/{}/{}.git" ' + \
                      'BRANCH {} UPDATE )\n'

            # Prepare CMakeLists file
            cmake_dst = os.path.join(bundle_dir, 'CMakeLists.txt')

            # Template CMakeLists.txt
            cmake = ['cmake_minimum_required( VERSION 3.12 FATAL_ERROR )\n',
                     'find_package( ecbuild 3.5 REQUIRED HINTS ${CMAKE_CURRENT_SOURCE_DIR} ' +
                     '${CMAKE_CURRENT_SOURCE_DIR}/../ecbuild)\n',
                     'project( jedi-bundle VERSION 1.1.0 LANGUAGES C CXX Fortran )\n',
                     'list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")\n',
                     'include( ecbuild_bundle )\n',
                     'set( ECBUILD_DEFAULT_BUILD_TYPE Release )\n',
                     'set( ENABLE_MPI ON CACHE BOOL "Compile with MPI")\n',
                     'ecbuild_bundle_initialize()\n',
                     'ecbuild_bundle_finalize()\n']

            # Iterate over repo dictionary
            for d in repo_dict:
                project = d['project']
                org = d['git org']
                repo = d['repo']
                branch = d['branch']
                proj_dir = os.path.join(bundle_dir, project)
                cmake.insert(-4, ecb_tmp.format(project, org, repo, branch))
                if not os.path.exists(proj_dir):
                    self.logger.info('Cloning into {}...'.format(project))
                    git_url = 'https://github.com/{}/{}.git'.format(org, repo)
                    git_got(git_url, branch, proj_dir, self.logger)
                else:
                    self.logger.info('{} has already been cloned into bundle'.format(project))

            # Write out new cmake lists file in bundle directory
            with open(cmake_dst, 'w') as f:
                f.writelines(cmake)

            # Create and change into the build directory
            if not os.path.exists(jedi_build):
                os.mkdir(jedi_build)
            os.chdir(jedi_build)
            self.logger.info('Starting Jedi build at {}'.format(os.getcwd()))

            # Commands to build jedi
            subprocess.run(['ecbuild -DMPIEXEC=$MPIEXEC {}'.format(bundle_dir)], shell=True)
            # Format string used to be '../' so we need to point it directly to bundle
            os.chdir('fv3-jedi/')
            subprocess.run(['make -j6'], shell=True)

            self.logger.info('Build Jedi is complete!')
