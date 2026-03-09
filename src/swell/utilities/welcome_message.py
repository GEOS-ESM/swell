# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


from swell import __version__


# --------------------------------------------------------------------------------------------------


def write_welcome_message() -> None:

    print("                  _ _ ")
    print(" _____      _____| | |  Swell workflow deployment manager")
    print("/ __\ \ /\ / / _ \ | |  NASA Global Modeling and Assimilation Office")  # noqa
    print("\__ \\\ V  V /  __/ | |  Version {__version__}".format(__version__=__version__))  # noqa
    print("|___/ \_/\_/ \___|_|_|  Documentation located at: https://geos-esm.github.io/swell")  # noqa
    print()
    print("Swell fetches and stores files using the R2D2 database framework")
    print("Setup of R2D2 credentials is required to use Swell. For instructions, see:")
    print("https://geos-esm.github.io/swell/#/configs/r2d2_v3_credentials")
