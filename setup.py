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
import subprocess
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

# --------------------------------------------------------------------------------------------------


class InstallCommand(install):
    def run(self):
        install.run(self)

        install_gmao_perl_lib()

# --------------------------------------------------------------------------------------------------


class DevelopCommand(develop):
    def run(self):
        develop.run(self)

        install_gmao_perl_lib()


# --------------------------------------------------------------------------------------------------


class EggInfoCommand(egg_info):
    def run(self):
        egg_info.run(self)

        install_gmao_perl_lib()


# --------------------------------------------------------------------------------------------------


def install_gmao_perl_lib():
    # Clone (if not already present) and install GMAO_perllib
    # at the g1.0.1 tag
    # Source files are put under src/GMAO_perllib
    # Binaries are put under ~/.swell/bin, make sure this is in your path

    root_dir = os.path.dirname(os.path.abspath(__file__))

    perllib_dir = f'{root_dir}/src/GMAO_perllib'

    if not os.path.isdir(perllib_dir):
        subprocess.run(f'git clone https://github.com/GEOS-ESM/GMAO_perllib.git' +
                       ' {perllib_dir} --depth=1 --branch=g1.0.1', shell=True)

        # ignore (seemingly) unused call to esma_set_this()
        with open(f'{perllib_dir}/CMakeLists.txt', 'r') as f:
            lines = f.readlines()
        first_line = lines[0]
        if first_line.strip() == 'esma_set_this()':
            with open(f'{perllib_dir}/CMakeLists.txt', 'w') as f:
                f.write('#' + first_line)
                for line in lines[1:]:
                    f.write(line)

    os.chdir(perllib_dir)
    subprocess.run(f'cmake -DCMAKE_INSTALL_PREFIX=~/.local {perllib_dir} && make all install',
                   shell=True)


# --------------------------------------------------------------------------------------------------


setup(
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
               'utilities/pinned_versions/*.yaml'
             ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'swell = swell.swell:main'
        ],
    },
    cmdclass={
        'install': InstallCommand,
        'develop': DevelopCommand,
        'egg_info': EggInfoCommand,
    },
    )

# --------------------------------------------------------------------------------------------------
