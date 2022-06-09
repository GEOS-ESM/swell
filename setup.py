# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

# Setup and installation script
#
# Usage: "pip install --prefix=/path/to/install ."

# --------------------------------------------------------------------------------------------------

import setuptools

setuptools.setup(
    name='swell',
    version='1.0.6',
    author='NASA Global Modeling and Assimilation Office',
    description='Workflow suites, tasks and configuraiton for coupled data assimilation',
    url='https://github.com/danholdaway/swell',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent'],
    python_requires='>=3.6',
    install_requires=[
        'click',
        'pyyaml>=5.4',
        'pycodestyle>=2.8.0',
        'pandas>=1.1.3',
        'isodate>=0.5.4',
        'xarray>=0.11.3',
    ],
    package_data={
        '': [
               'deployment/platforms/*/modules*',
               'deployment/platforms/*/r2d2_config.yaml',
               'suites/*/*',
               'configuration/*.yaml',
               'configuration/*/*',
             ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'swell_task = swell.tasks.base.task_base:main',
            'swell_create_experiment = swell.deployment.bin.swell_create_experiment:main',
            'swell_launch_experiment = swell.deployment.bin.swell_launch_experiment:main',
            'swell_sat_db_processing = swell.deployment.bin.swell_sat_db_processing:main',
        ],
    },
    )

# --------------------------------------------------------------------------------------------------
