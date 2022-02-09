# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import re
import glob
from shutil import copyfile

from swell.tasks.base.task_base import taskBase
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class Stage(taskBase):

    def execute(self):
        """Acquires listed files under the YAML STAGE directive.

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        cfg = self.config['STAGE']

        for group in cfg:
            self.get_files(group, 'copy_files', self.copy_file)
            self.get_files(group, 'link_files', self.link_file)

        return

    # ----------------------------------------------------------------------------------------------

    def get_files(self, group, type, fh):
        """Acquires indicated files using the supplied file handler.

           Parameters
           ----------
           group : dict, required
             Staging dictionary (copy_files or link_files directives)

           type : string, required
             Desired staging file directive type

           fh : method, required
             File handler for executing the staging directive
        """

        for k, v in iter(group.get(type, {}).items()):
            for args in v:

                src = args[0]
                dir = args[1]

                filelist = glob.glob(src)

                if not filelist:
                    self.logger.abort('Source inputs not found "' + src + '"')

                try:
                    os.makedirs(dir, 0o755, exist_ok=True)
                except Exception:
                    self.logger.abort('Unable to create "' + dir + '"')

                for file in filelist:
                    dest = os.path.join(dir, os.path.basename(file))
                    fh(file, dest)

    # ----------------------------------------------------------------------------------------------

    def copy_file(self, src, dest):
        """File handler - copies a file

           Parameters
           ----------
           src : string, required
             Source file to be copied.

           dest : string, required
             Destination file to be created.
        """

        self.logger.info("Copying " + src + " to " + dest)
        if not os.path.isfile(src):
            self.logger.abort('Source file does not exist: "' + src + '"')

        try:
            copyfile(src, dest)
        except Exception:
            self.logger.abort('Unable to copy "' + src + '" to "' + dest + '"')

    # ----------------------------------------------------------------------------------------------

    def link_file(self, src, dest):
        """File handler - Symbolically links a file

           Parameters
           ----------
           src : string, required
             Source file to be linked.

           dest : string, required
             Destination link file to be created.
        """

        self.logger.info('Linking "' + dest + '" to "' + src + '"')
        if not os.path.isfile(src):
            self.logger.abort('Source file does not exist: "' + src + '"')

        try:
            if os.path.islink(dest):
                os.remove(dest)
            if os.path.isfile(dest):
                self.logger.abort('File already exists: "' + dest + '"')
            if not os.path.isfile(dest):
                os.symlink(src, dest)
        except Exception:
            self.logger.abort('Unable to link "' + dest + '" to "' + src + '"')
