# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# -----------------------------------------------------------------------------

from typing import Optional

from swell.utilities.logger import Logger


class SWELLError(Exception):

    def __init__(
        self,
        message: str,
        logger: Optional[Logger] = None
    ) -> None:

        self.message = message
        super().__init__(message)

        if logger:
            logger(message)

# -----------------------------------------------------------------------------


class SWELLFileError(SWELLError):

    pass

# -----------------------------------------------------------------------------


class SWELLConfigError(SWELLError):

    pass

# -----------------------------------------------------------------------------
