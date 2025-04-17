# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union

from dataclasses import field

# --------------------------------------------------------------------------------------------------


def mutable_field(list_dict: Union[list, dict]):
    # Need to construct field using lambda because by default dataclass fields
    # cannot be initialized to mutable types
    return field(default_factory=lambda: list_dict)

# --------------------------------------------------------------------------------------------------
