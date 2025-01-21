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

import os.path
import setuptools

setuptools.setup(
    name='swell',
    author='NASA Global Modeling and Assimilation Office',
    description='Workflow suites, tasks and configuration for coupled data assimilation',
    url='https://github.com/geos-esm/swell',
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
    package_data={
        '': [
               'deployment/platforms/*/modules*',
               'deployment/platforms/*/*.yaml',
               'suites/*',
               'suites/*/*',
               'suites/*/*/*',
               'tasks/task_questions.yaml',
               'test/suite_tests/*.yaml',
               'configuration/*',
               'configuration/*/*',
               'configuration/*/*/*',
               'configuration/*/*/*/*',
               'configuration/*/*/*/*/*',
               'configuration/*/*/*/*/*/*',
               'utilities/pinned_versions/*.yaml'
             ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'swell = swell.swell:main'
        ],
    },
    )

# --------------------------------------------------------------------------------------------------
