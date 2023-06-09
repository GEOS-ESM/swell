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
    install_requires=[
        'tomlkit',
        'click',
        'jinja2>=3.0.3',
        'pyyaml>=6.0',
        'pycodestyle>=2.8.0',
        'pandas>=1.4.0',
        'isodate>=0.5.4',
        'xarray>=0.11.3',
        'questionary>=1.10.0',
        'flake8>=6.0.0',
    ],
    package_data={
        '': [
               'deployment/platforms/*/modules*',
               'deployment/platforms/*/*.yaml',
               'suites/*',
               'suites/*/*',
               'suites/*/*/*',
               'tasks/task_questions.yaml',
               'configuration/*',
               'configuration/*/*',
               'configuration/*/*/*',
               'configuration/*/*/*/*',
               'configuration/*/*/*/*/*',
             ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'swell_task = swell.tasks.base.task_base:main',
            'swell_create_experiment = swell.deployment.bin.swell_create_experiment:main',
            'swell_prepare_experiment_config = swell.deployment.bin.swell_prepare_config:main',
            'swell_launch_experiment = swell.deployment.bin.swell_launch_experiment:main',
            'swell_sat_db_processing = swell.deployment.bin.swell_sat_db_processing:main',
            # Utilities
            'swell_util_check_jedi_interface_templates = \
                swell.utilities.bin.check_jedi_interface_templates:main',
            'swell_util_task_question_dicts = swell.utilities.bin.task_question_dicts:tq_dicts',
            'swell_util_task_question_dicts_defaults = \
                swell.utilities.bin.task_question_dicts_defaults:tq_dicts_defaults',
            'swell_test_suite = swell.test.test_suite:main',
        ],
    },
    )

# --------------------------------------------------------------------------------------------------
