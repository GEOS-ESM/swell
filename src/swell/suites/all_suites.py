# --------------------------------------------------------------------------------------------------
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from enum import Enum
from importlib import import_module

from swell.swell_path import get_swell_path
from swell.utilities.suite_utils import get_suites

# --------------------------------------------------------------------------------------------------


# Class methods for AllSuites enum

@classmethod
def get_config(cls, config_name):
    return getattr(cls, config_name).value.value


@classmethod
def config_names(cls):
    return cls._member_names_


@classmethod
def base_suite(cls, config: str) -> str:
    return cls.__config_suite_map__[config]

# --------------------------------------------------------------------------------------------------


def construct_suite_enum():
    # Automatically construct enum of all suite configs

    def format_config_name(config_name):
        return config_name[1:] if config_name[0] == '_' else config_name

    def wrapper(suite_config_enum):
        # Dictionary used to create the enum
        enum_dict = {}
        # Map of config names to their parent suites
        config_suite_map = {}

        # Find all of the suite configs
        for suite in get_suites():
            config_path = os.path.join(get_swell_path(), 'suites', suite, 'suite_config.py')
            if os.path.exists(config_path):
                suite_container = getattr(
                        import_module(f'swell.suites.{suite}.suite_config'), 'SuiteConfig')
                suite_configs = suite_container.get_all()

                for config in suite_configs:
                    enum_dict[format_config_name(config)] = getattr(suite_container, config)
                    config_suite_map[format_config_name(config)] = suite
            else:
                enum_dict[suite] = SuiteQuestions.all_suites
                config_suite_map[suite] = suite

        # Set the map dictionary to a hidden attribute
        enum_dict['__config_suite_map__'] = config_suite_map

        # Override with manually specified keys in enum
        for item in suite_config_enum:
            enum_dict[item.name] = item.value

        # Build the enum
        enum_cls = Enum(suite_config_enum.__name__, enum_dict)

        # Set classmethods for the enum
        setattr(enum_cls, 'get_config', get_config)
        setattr(enum_cls, 'config_names', config_names)
        setattr(enum_cls, 'base_suite', base_suite)

        return enum_cls
    return wrapper

# --------------------------------------------------------------------------------------------------


@construct_suite_enum()
class AllSuites(Enum):
    pass


# --------------------------------------------------------------------------------------------------
