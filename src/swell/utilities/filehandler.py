# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# -----------------------------------------------------------------------------
#
# This module provides file handlers for reading data structures describing
# files to be copied or linked. There are two YAML data structure conventions
# supported by this module: (1) StageData and (2) GetData. Each is expected to
# be a list of dictionaries where each dictionary describes a collection of
# files to be retrieved.
#
# StageData collections (or dictionaries) have the following form:
#
#   <directive>:
#     directories:
#       - [src, dst]
#       - [src, dst]
#       -    .
#       -    .
#
# where
#
#   <directive>: "copy_file" or "link_file" denoting how the source file is to
#                be retrieved.
#   src: source file or glob expression describing file(s) to be acquired.
#   dst: directory to receive the acquired files.
#
# GetData collections (or dictionaries) have the following form:
#
#   src: <path1> <path2> ...
#     Path locations where source files reside. Paths will be searched in the
#     order specified.
#   dst: <path>
#     Destination directory (unqualified files will be copied here)
#   min_count: <count>
#     Minimum file count (default: 1). Every copy or link resulting in a
#     new file is counted. Duplicate copies to the same file are only counted
#     once.
#   min_age: <age>
#     Minimum file age (default: 0 seconds). Only files resulting in a unique
#     copy or link are assessed.
#   link: <0|1>
#     Indicates that a symbolic link is desired (default: False)
#   files: <list of files>
#     List of source files to be acquired. Each file can be paired with
#     a destination name. Absolute paths can be used to override src and
#     dst directories. For example:
#
#     - file1 (copy src/file1 to dst/file1)
#     - file1 file2 (copy src/file1 to dst/file2)
#     - /data/file1 (copy /data/file1 to dst/file1)
#     - /data/file1 /data/file2 (copy /data/file1 to /data/file2)
#
#     Listed source files may contain wildcards. If the "files" parameter
#     is omitted, all files in "src" will be copied to "dst".
# -----------------------------------------------------------------------------

import os
import glob
import copy
import datetime as dt
from shutil import copyfile
from typing import Union

from swell.utilities.exceptions import *


def get_file_handler(config: list, **kwargs) -> Union['StageFileHandler', 'GetDataFileHandler']:
    """Factory for determining the file handler type for retrieving data.

       This method uses a heuristic algorithm to determine the staging
       file structure convention and the appropriate file handler.

       Parameters
       ----------
       config : list, required
         Staging data structure from YAML configuration
       strict : boolean, optional
         Requires that all specified files exist when True.

       Returns
       -------
       fh : FileHandler
         FileHandler for input data structure type (see GetDataFileHandler
         and StageFileHandler)
    """

    strict = kwargs.get('strict', True)
    if not isinstance(config, list):
        raise SWELLConfigError(config)

    group = config[0]
    collection = group.get('copy_files', {}).get('directories', [])
    if collection:
        return StageFileHandler(config, strict=strict)

    collection = group.get('link_files', {}).get('directories', [])
    if collection:
        return StageFileHandler(config, strict=strict)

    return GetDataFileHandler(config, strict=strict)

# ------------------------------------------------------------------------------


class FileHandler(object):

    def __init__(self, config: list, **kwargs) -> None:

        self.listing = []
        self.config = copy.deepcopy(config)
        self.strict = kwargs.get('strict', True)

# ------------------------------------------------------------------------------

    def is_ready(self, fc: Union['FileCollection', None] = None) -> bool:
        """Determines if the file collection meets the criteria for
           readiness (e.g. minimum file count etc.)

           Parameters
           ----------
           fc : FileCollection, optional
             FileCollection object. If absent, all file collections will
             be visited.

           Returns
           -------
           result : boolean
             True: collection(s) are ready
             False: one or more collections are not ready
        """

        if fc is None:
            for fc in self.list(True):
                if not self.is_ready(fc):
                    return False
            return True

        if fc.num_files() < fc.min_count:
            return False

        for srcfile, dstfile in fc:

            if not os.path.isfile(srcfile):
                continue

            mt = dt.datetime.fromtimestamp(os.stat(srcfile).st_mtime)
            now = dt.datetime.now()
            age = (now - mt).total_seconds()

            if age < fc.min_age:
                return False

        return True

# ------------------------------------------------------------------------

    def get(self, fc: Union['FileCollection', None] = None) -> None:
        """Retrieves the files in the specified file collection.

           Parameters
           ----------
           fc : FileCollection, optional
             FileCollection object. If absent, files in all file
             collections will be retrieved.
        """

        if fc is None:
            for fc in self.list():
                self.get(fc)
            return

        for srcfile, dstfile in fc:

            dir = os.path.dirname(dstfile)

            try:
                os.makedirs(dir, 0o755, exist_ok=True)
            except Exception as e:
                raise SWELLFileError(str(e))

            if fc.link:
                self.link(srcfile, dstfile)
            else:
                self.copy(srcfile, dstfile)

# ---------------------------------------------------------------------------

    def copy(self, src: str, dst: str) -> None:
        """File handler - copies a file

           Parameters
           ----------
           src : string, required
             Source file to be copied.

           dst : string, required
             Destination file to be created.
        """

        if not os.path.isfile(src):
            raise SWELLFileError('Source file does not exist: "' + src + '"')

        try:
            copyfile(src, dst)
        except Exception as e:
            raise SWELLFileError(str(e))

# ---------------------------------------------------------------------------

    def link(self, src: str, dst: str) -> None:
        """File handler - Symbolically links a file

           Parameters
           ----------
           src : string, required
             Source file to be linked.

           dst : string, required
             Destination link file to be created.
        """

        if not os.path.isfile(src):
            raise SWELLFileError('Source file does not exist: "' + src + '"')

        try:
            if os.path.islink(dst):
                os.remove(dst)
            if os.path.isfile(dst):
                raise SWELLFileError('File exists where link expected: "' + dst + '"')
            if not os.path.isfile(dst):
                os.symlink(src, dst)
        except Exception as e:
            raise SWELLFileError(str(e))

# ---------------------------------------------------------------------------


class StageFileHandler(FileHandler):

    def list(self, force: bool = False) -> list:
        """Creates a list of file collections defined in configuration
           using the "stage" data structure convention.

           This method will only query the filesystem once for files to
           preserve the status at the time of the intitial invocation.

           Parameters
           ----------
           force : boolean, optional
             Forces a new query of the filesystem for collection files.

           Returns
           -------
           listing : list of FileCollections
             List of all file collections defined in configuration.
        """

        listing = []
        if self.listing and not force:
            return copy.deepcopy(self.listing)

        for collection in self.config:

            for directive, entry in iter(collection.items()):

                link = False
                if directive == 'link_files':
                    link = True

                fc = FileCollection({'link': link})
                files = entry['directories']

                for record in files:

                    src = record[0]
                    dst = record[1]

                    filelist = glob.glob(src)

                    if not filelist and self.strict:
                        raise SWELLConfigError('Source inputs not found "'
                                               + src + '"')

                    for srcfile in filelist:
                        bname = os.path.basename(srcfile)
                        dstfile = os.path.join(dst, bname)
                        fc.update(srcfile, dstfile)

                listing.append(fc)

        self.listing = copy.deepcopy(listing)

        return listing

# ---------------------------------------------------------------------------


class GetDataFileHandler(FileHandler):

    def list(self, force: bool = False) -> list:
        """Creates a list of file collections defined in configuration
           using the "get_data" data structure convention.

           This method will only query the filesystem once for files to
           preserve the status at the time of the intitial invocation.

           Parameters
           ----------
           force : boolean, optional
             Forces a new query of the filesystem for collection files.

           Returns
           -------
           listing : list of FileCollections
             List of all file collections defined in configuration.
        """

        listing = []
        if self.listing and not force:
            return copy.deepcopy(self.listing)

        for collection in self.config:

            # Get collection parameters

            options = {k: v for k, v in iter(collection.items())
                       if k not in ['src', 'dst', 'files']}

            paths = collection.get('src', '').split()
            dst = collection.get('dst', '')
            if not paths:
                paths = ['']

            # Create file listing

            registry = {}
            fc = FileCollection(options)

            for entry in collection.get('files', ['*']):

                args = entry.split() + ['']
                found = False

                for src in paths:

                    srcfile = os.path.join(src, args[0])
                    if os.path.isabs(args[0]):
                        srcfile = args[0]

                    filelist = glob.glob(srcfile)
                    found = found or filelist

                    for srcfile in filelist:

                        dstfile = args[1]
                        bname = os.path.basename(srcfile)

                        if not dstfile:
                            dstfile = bname
                        if not os.path.isabs(dstfile) and dst:
                            dstfile = os.path.join(dst, dstfile)

                        if dstfile in registry:
                            continue

                        registry[dstfile] = srcfile
                        fc.update(srcfile, dstfile)

                if not found and self.strict:
                    raise SWELLConfigError('Source inputs not found "' +
                                           srcfile + '"')

            listing.append(fc)

        self.listing = copy.deepcopy(listing)

        return listing

# ------------------------------------------------------------------------------


class FileCollection(object):

    def __init__(self, config: list) -> None:

        self.config = copy.deepcopy(config)

        self.listing = []
        self.link = config.get('link', False)
        self.min_count = config.get('min_count', 1)
        self.min_age = config.get('min_age', 0)

# ------------------------------------------------------------------------------

    def update(self, srcfile: list, dstfile: list) -> None:

        self.listing.append((srcfile, dstfile))

# ------------------------------------------------------------------------------

    def num_files(self) -> int: return len(self.listing)

# ------------------------------------------------------------------------------

    def __iter__(self):
        for v in self.listing:
            yield v
