# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import shutil

from jedi_bundle.bin.jedi_bundle import get_default_config, get_bundles


# --------------------------------------------------------------------------------------------------


def build_and_source_dirs(jedi_bundle_path):

    # Make jedi_bundle directory
    # --------------------------
    os.makedirs(jedi_bundle_path, 0o755, exist_ok=True)

    jedi_bundle_build_path = os.path.join(jedi_bundle_path, 'build')
    jedi_bundle_source_path = os.path.join(jedi_bundle_path, 'source')

    # Remove trailing slash if needed
    if jedi_bundle_build_path.endswith('/'):
        jedi_bundle_build_path = jedi_bundle_build_path[:-1]
    if jedi_bundle_source_path.endswith('/'):
        jedi_bundle_source_path = jedi_bundle_source_path[:-1]

    return jedi_bundle_build_path, jedi_bundle_source_path


# --------------------------------------------------------------------------------------------------


def link_path(source, target):

    # Remove existing source path if present
    if os.path.islink(target):  # Is a link
        os.remove(target)
    elif os.path.isdir(target):  # Is a directory
        shutil.rmtree(target)

    # Link existing source into the directory
    os.symlink(source, target)


# --------------------------------------------------------------------------------------------------


def set_jedi_bundle_config(bundles, path_to_source, path_to_build, cores_to_use_for_make = 6):

    # Start from the default jedi_bundle config file
    jedi_bundle_config = get_default_config()

    # Always build certain JEDI packages
    bundles.append('iodaconv')

    # Set the clone stage options
    jedi_bundle_config['clone_options']['bundles'] = bundles
    jedi_bundle_config['clone_options']['path_to_source'] = path_to_source

    # Set the configure stage options
    jedi_bundle_config['configure_options']['path_to_build'] = path_to_build

    # Set the make stage options
    jedi_bundle_config['make_options']['cores_to_use_for_make'] = cores_to_use_for_make

    # Return the dictionary object
    return jedi_bundle_config


# --------------------------------------------------------------------------------------------------
