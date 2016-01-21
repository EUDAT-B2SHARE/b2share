# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016 CERN.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""B2Share application
"""  # FIXME improve this documentation

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

install_requires = [
    'invenio-config>=1.0.0a1,<1.1.0',
    'invenio-base>=1.0.0a5,<1.1.0',
    'invenio-records-rest>=1.0.0a3,<1.1.0',
    'invenio-records>=1.0.0a8,<1.1.0',
    'invenio-db>=1.0.0a9,<1.1.0',
    'invenio-celery>=1.0.0a3,<1.1.0',
]

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pep257>=0.7.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'Flask-Testing'
]

extras_require = {
    'mysql': [
        'pymysql>=0.6.7',
    ],
    'postgresql': [
        'psycopg2>=2.6.1',
    ],
    'docs': [
        "Sphinx>=1.3",
    ],
    'development': [
        'Flask-DebugToolbar>=0.9',
        'setuptools-bower>=0.2'
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
]


class PyTest(TestCommand):
    """PyTest Test."""

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        """Init pytest."""
        TestCommand.initialize_options(self)
        self.pytest_args = []
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        config = ConfigParser()
        config.read('pytest.ini')
        self.pytest_args = config.get('pytest', 'addopts').split(' ')

    def finalize_options(self):
        """Finalize pytest."""
        TestCommand.finalize_options(self)
        if hasattr(self, '_test_args'):
            self.test_suite = ''
        else:
            self.test_args = []
            self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# extras_require = {
# }

# Get the version string.  Cannot be done with import!
g = {}
with open(os.path.join("b2share", "version.py"), "rt") as fp:
    exec(fp.read(), g)
version = g["__version__"]

setup(
    name='b2share',
    version=version,
    url='https://github.com/EUDAT-B2SHARE/b2share',
    license='GPLv2',
    author='CERN',
    description='B2Share application',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    entry_points={
        'console_scripts': [
            'b2share = b2share.cli:cli',
        ],
        'invenio_base.api_apps': [
            'b2share_communities = b2share.modules.communities:B2ShareCommunities',
            'b2share_schemas = b2share.modules.schemas:B2ShareSchemas',
            'b2share_users = b2share.modules.users:B2ShareUsers',
        ],
        # 'invenio_db.models': [
        #     'b2share_communities = b2share.modules.communities.models',
        # ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,

    cmdclass={'test': PyTest},
)
