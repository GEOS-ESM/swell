# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import importlib
import pkgutil

# --------------------------------------------------------------------------------------------------

def discover_plugins(package):
    '''Walk through packages to trigger any hooks.

    Parameters:
    package: Python package
    '''
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_module_name = f"{package.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)

        if is_pkg:
            discover_plugins(module)

# --------------------------------------------------------------------------------------------------
