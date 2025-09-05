# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# -----------------------------------------------------------------------------

from enum import Enum, member

# -----------------------------------------------------------------------------


class ExceptionTypes(Enum):

    # -----------------------------------------------------------------------------

    @member
    class SwellError(Exception):
        pass

    # -----------------------------------------------------------------------------

    @member
    class SwellFileError(SwellError):
        pass

    # -----------------------------------------------------------------------------

    @member
    class SwellConfigError(SwellError):
        pass

    # -----------------------------------------------------------------------------

    @classmethod
    def get_type(cls, name: str):
        return cls.name.value

    # -----------------------------------------------------------------------------

    @classmethod
    def get_all(cls) -> list:
        member_list = []
        for name in cls._member_names_:
            member_list.append(cls.get_type(name))

        return member_list

    # -----------------------------------------------------------------------------