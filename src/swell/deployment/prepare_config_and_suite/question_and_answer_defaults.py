# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from typing import Union

from swell.utilities.logger import Logger

class GetAnswerDefaults:

    def get_answer(self, logger: Logger, key: str, val: dict) -> Union[int, float, str]:
        default = val['default_value']
        widget_type = val['widget_type']
        options = val['options']

        if not widget_type.validate_value(default):
            logger.abort(f'Default value for {key}, {default}, does not conform to type '
                           '{widget_type.base_type.__name__}, check the override file or '
                           'suite configuration.')

        return default

# --------------------------------------------------------------------------------------------------
