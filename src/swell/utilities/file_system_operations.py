# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import shutil

# --------------------------------------------------------------------------------------------------


def copy_to_dst_dir(logger: 'Logger', src: str, dst_dir: str) -> None:

    """ Source could be a directory or single file which necesitates different handling
    """

    try:
        if not os.path.isfile(src):
            logger.info(' Copying files from: '+src)
            shutil.copytree(src, dst_dir, dirs_exist_ok=True)
        else:
            logger.info(' Copying file: '+src)
            shutil.copy(src, dst_dir)

    except Exception:
        logger.abort('Copying failed, see if source files exists')

# --------------------------------------------------------------------------------------------------


def link_all_files_from_first_in_hierarchy_of_sources(
        logger: 'Logger',
        source_paths: list,
        target_path: str
) -> None:
    """For a list of source paths check for the existence of the source paths and for files
       residing in at least one of the paths. For the first source path in the list that is found
       to contain files link them into the target path (remove first if existing)

    Parameters
    ----------
        logger: Logger to use for reporting any errors
        source_paths: list of source paths to search for files
        target_path: directory into which all found files will be linked to
    """

    # First sweep to see if directories exist
    logger.info('Source Paths', source_paths)

    found_paths = []
    for source_path in source_paths:
        if os.path.exists(source_path):
            found_paths.append(True)
        else:
            found_paths.append(False)

    # Check that at least one path was found
    if not any(found_paths):
        logger.abort(f'In link_all_files_from_first_in_hierarchy_of_sources none of the ' +
                     f'directories being searched were found to exist. Directories: {source_paths}')

    # Second sweep to establish if directories contain files
    found_files = False
    for ind, source_path in enumerate(source_paths):
        if found_paths[ind]:
            source_path_files = os.listdir(source_path)
            if source_path_files:
                found_files = True
                source_path = source_paths[ind]
                break

    # Check that at least one path contains some files
    if not found_files:
        logger.abort(f'In link_all_files_from_first_in_hierarchy_of_sources none of the ' +
                     f'directories being searched contained any files. Directories: {source_paths}')

    # Link all the files from the first directory searched that contains files
    source_files = os.listdir(source_path)
    for source_file in source_files:
        source_path_file = os.path.join(source_path, source_file)
        target_path_file = os.path.join(target_path, source_file)
        link_file_existing_link_ok(logger, source_path_file, target_path_file)

# --------------------------------------------------------------------------------------------------


def check_if_files_exist_in_path(logger: 'Logger', path_to_files: str) -> bool:
    """Checks if path to directory exists, and if files are present within it.

    Parameters
    ----------
    logger: Logger to output results to
    path_to_files: path to target directory
    """

    if os.path.exists(path_to_files):
        if os.listdir(path_to_files):
            logger.info(f'Files found within {path_to_files}')
            return True
        else:
            logger.info(f'No files found within {path_to_files}')
            return False

# --------------------------------------------------------------------------------------------------


def link_file_existing_link_ok(
    logger: 'Logger',
    source_path_file: str,
    target_path_file: str
) -> None:

    """Create a symbolic link from a source location to a target location. If a symbolic link
       already exists it will be deleted. If a file already exists and it is not a link the code
       will abort

    Parameters
    ----------
        logger: Logger to use for reporting any errors
        source_path_file: source for the symbolic link
        target_path_file: target for the symbolic link
    """

    # Check for existence and remove if symbolic link exists. Abort if concrete file exists
    if os.path.exists(target_path_file):
        if os.path.islink(target_path_file):
            os.remove(target_path_file)
        else:
            logger.abort(f'In link_file_with_overwrite when linking source file ' +
                         f'{source_path_file} to {target_path_file} a file was already found ' +
                         f'that is not a symbolic link. This code will not replace concrete ' +
                         f'files with symbolic links.')

    # Create symbolic link
    logger.info(f'Linking {source_path_file} to {target_path_file}')
    os.symlink(source_path_file, target_path_file)

    # ----------------------------------------------------------------------------------------------


def move_files(logger: 'Logger', src_dir: str, dst_dir: str) -> None:

    try:
        logger.info(' Moving file(s) from: '+src_dir)
        shutil.move(src_dir, dst_dir)

    except Exception:
        logger.abort('Moving failed, see if source files exist')

# ----------------------------------------------------------------------------------------------
