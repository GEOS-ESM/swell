# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


from swell import __version__
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def write_welcome_message(application):

    logger = Logger('')

    logger.blank(f"                  _ _ ", False)  # noqa
    logger.blank(f" _____      _____| | |", False)  # noqa
    logger.blank(f"/ __\ \ /\ / / _ \ | |  Swell workflow deployment manager", False)  # noqa
    logger.blank(f"\__ \\\ V  V /  __/ | |  NASA Global Modelling and Assimilation Office", False)  # noqa
    logger.blank(f"|___/ \_/\_/ \___|_|_|  Version {__version__}", False)  # noqa
    logger.blank(f"                                         ", False)  # noqa
    logger.blank(f"Welcome to swell {application.lower()}.", False)  # noqa
    logger.blank('', False)  # noqa
