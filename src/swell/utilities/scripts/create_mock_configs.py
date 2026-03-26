# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os

from swell.swell_path import get_swell_path
from swell.utilities.mock_jedi_config import mock_jedi_config

# --------------------------------------------------------------------------------------------------

defaults_dict = {}

marine_default_datetime = '20210701T120000Z'
atmosphere_default_datetime = '20231010T000000Z'
compo_default_datetime = '20230805T1800Z'

defaults_dict['3dvar_marine'] = {'datetime': marine_default_datetime,
                                 'model': 'geos_marine',
                                 'executable_type': 'variational'}

defaults_dict['3dvar_marine_cycle'] = defaults_dict['3dvar_marine'].copy()

defaults_dict['3dfgat_marine_cycle'] = {'datetime': marine_default_datetime,
                                        'model': 'geos_marine',
                                        'executable_type': 'fgat'}

defaults_dict['3dvar_atmos'] = {'datetime': atmosphere_default_datetime,
                                'model': 'geos_atmosphere',
                                'executable_type': 'variational'}

defaults_dict['3dfgat_atmos'] = {'datetime': atmosphere_default_datetime,
                                 'model': 'geos_atmosphere',
                                 'executable_type': 'variational'}

defaults_dict['hofx'] = {'datetime': atmosphere_default_datetime,
                         'model': 'geos_atmosphere',
                         'executable_type': 'hofx'}

defaults_dict['hofx_cf'] = {'datetime': '20230805T180000Z',
                            'model': 'geos_cf',
                            'executable_type': 'hofx'}

defaults_dict['3dvar_cf'] = {'datetime': '20230805T180000Z',
                             'model': 'geos_cf',
                             'executable_type': 'variational'}

defaults_dict['localensembleda'] = {'datetime': atmosphere_default_datetime,
                                    'model': 'geos_atmosphere',
                                    'executable_type': 'localensembleda'}

# --------------------------------------------------------------------------------------------------


def main() -> None:
    for suite, defaults in defaults_dict.items():
        model = defaults['model']
        datetime = defaults['datetime']
        executable_type = defaults['executable_type']

        copy_dir = os.path.join(get_swell_path(), 'test', 'jedi_configs')

        mock_jedi_config(suite, model, datetime, executable_type, copy_dir)


# --------------------------------------------------------------------------------------------------
