# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from typing import Union, Optional

from swell.utilities.logger import Logger


class GetAnswerDefaults:

    def get_answer(self, logger: Logger, key: str, val: dict,
                   model: Optional[str] = None) -> Union[int, float, str]:
        default = val['default_value']
        data_type = val['data_type']

        if isinstance(data_type, list):
            if not any([dtype.is_type(default) for dtype in data_type]):
                self.__logger__.warning(f'Warning: Experiment key {name} does not conform to any expected'
                                        f' types {" ".join(data_type)}')

        elif not data_type.is_type(default):
            logger.warning(f'Default value for {key}, {default}, does not conform to type '
                           f'{data_type.value}, check the override file or '
                           'suite configuration.')

        return default

# --------------------------------------------------------------------------------------------------
