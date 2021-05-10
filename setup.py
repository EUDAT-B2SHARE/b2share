# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016, University of Tuebingen, CERN.
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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share application
"""  # FIXME improve this documentation

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

install_requires = [
    'b2handle>=1.1.1,<2.0.0',
    'elasticsearch<3.0.0,>=2.0.0',
    'elasticsearch-dsl<3.0.0,>=2.0.0',
    'datacite>=1.1.1',
    'dcxml>=0.1.0',
    'doschema>=1.0.0a1',
    'dojson>=1.2.1',
    'easywebdav2>=1.3.0',
    'Flask-Login<0.4,>=0.3.2',
    'httplib2>=0.9.2',
    'invenio-access>=1.0.0a11,<1.1.0',
    'invenio-accounts>=1.0.0b9,<1.1.0',
    'invenio-accounts-rest>=1.0.0a4,<1.1.0',
    'invenio-base>=1.0.0a14,<1.1.0',
    'invenio-celery>=1.0.0b1,<1.1.0',
    'invenio-config>=1.0.0b2,<1.1.0',
    'invenio-db[postgresql,versioning]>=1.0.0b7,<1.1.0',
    'invenio-deposit>=1.0.0a8,<1.1.0',
    'invenio-files-rest>=1.0.0a21,<1.1.0',
    'invenio-mail>=1.0.0b1,<1.1.0',
    'invenio-marc21>=1.0.0a3',
    'invenio-oaiserver>=1.0.0a9,<1.1.0',
    'invenio-oauthclient>=1.0.0a13,<1.1.0',
    'invenio-oauth2server>=1.0.0a14,<1.1.0',
    'invenio-pidstore>=v1.0.0b1,<1.1.0',
    'invenio-pidrelations>=v1.0.0a4,<1.1.0',
    'invenio-query-parser>=0.6.0,<1.1.0',
    'invenio-records>=1.0.0b1,<1.1.0',
    'invenio-records-rest>=1.0.0a17,<1.1.0',
    'invenio-records-files>=1.0.0a9,<1.1.0',
    'invenio-rest[cors]>=1.0.0a10,<1.1.0',
    'invenio-search>=1.0.0a10,<1.1.0',
    'invenio-stats>=1.0.0a8',
    'invenio-logging>=1.0.0a3',
    'invenio-indexer>=1.0.0a9',
    'jsonresolver[jsonschema]>=0.2.1',
]

if sys.version_info < (3, 4):
    # In Python 3.4, pathlib is now part of the standard library.
    install_requires += ["pathlib >= 1.0.1"]
    # Backport of Python 3.4 enums to earlier versions
    install_requires.append('enum34>=1.1.6')

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pep257>=0.7.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'Flask-Testing',
    'mock',
    'responses>=0.5.1,<=0.10.6',
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
        'sphinxcontrib-httpdomain>=1.4.0',
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
            'b2share_apiroot = b2share.modules.apiroot:B2ShareApiRoot',
            'b2share_communities = b2share.modules.communities:B2ShareCommunities',
            'b2share_schemas = b2share.modules.schemas:B2ShareSchemas',
            'b2share_users = b2share.modules.users:B2ShareUsers',
            'b2share_roles = b2share.modules.roles:B2ShareRoles',
            'b2share_records = b2share.modules.records:B2ShareRecords',
            'b2share_deposit = b2share.modules.deposit:B2ShareDeposit',
            'b2share_handle = b2share.modules.handle:B2ShareHandle',
            'b2share_files = b2share.modules.files:B2ShareFiles',
            'b2share_remotes = b2share.modules.remotes:B2ShareRemotes',
            'b2share_access = b2share.modules.access:B2ShareAccess',
            'b2share_oaiserver = b2share.modules.oaiserver:B2ShareOAIServer',
            'b2share_upgrade = b2share.modules.upgrade:B2ShareUpgrade',
            # enable OAuthClient on the API
            'invenio_oauthclient = invenio_oauthclient:InvenioOAuthClient',
            'invenio_oauth2server = invenio_oauth2server:InvenioOAuth2Server',
            'invenio_mail = invenio_mail:InvenioMail',
            'invenio_oaiserver = invenio_oaiserver:InvenioOAIServer',
            'invenio_pidrelations = invenio_pidrelations:InvenioPIDRelations',
        ],
        'invenio_base.api_blueprints': [
            'invenio_oauthclient = invenio_oauthclient.views.client:blueprint',
            'b2share_communities = '
            'b2share.modules.communities.views:blueprint',
            'invenio_oaiserver = invenio_oaiserver.views.server:blueprint',
        ],
        'invenio_db.models': [
            'b2share_communities = b2share.modules.communities.models',
            'b2share_schemas = b2share.modules.schemas.models',
        ],
        'invenio_db.alembic': [
            'b2share_communities = b2share.modules.communities:alembic',
            'b2share_schemas = b2share.modules.schemas:alembic',
            'b2share_upgrade = b2share.modules.upgrade:alembic',
        ],
        'invenio_records.jsonresolver': [
            'b2share_schemas = b2share.modules.schemas.jsonresolver',
        ],
        'invenio_pidstore.minters': [
            'b2rec'
            '= b2share.modules.records.minters:b2share_record_uuid_minter',
            'b2dep'
            '= b2share.modules.deposit.minters:b2share_deposit_uuid_minter',
        ],
        'invenio_base.api_converters': [
            'file_key = b2share.modules.deposit.utils:FileKeyConverter',
        ],
        'invenio_search.mappings':[
            'records = b2share.modules.records.mappings',
            'deposits = b2share.modules.deposit.mappings',
        ],
        'invenio_pidstore.fetchers': [
            'b2rec'
            '= b2share.modules.records.fetchers:b2share_record_uuid_fetcher',
            'b2dep'
            '= b2share.modules.deposit.fetchers:b2share_deposit_uuid_fetcher',
        ],
        'invenio_celery.tasks': [
            'b2share_records = b2share.modules.records.tasks',
            'b2share_files = b2share.modules.files.tasks',
        ],
        'invenio_access.actions': [
            'create_deposit_need = '
            'b2share.modules.deposit.permissions:create_deposit_need',
            'read_deposit_need = '
            'b2share.modules.deposit.permissions:read_deposit_need',
            'update_deposit_publication_state_need = '
            'b2share.modules.deposit.permissions:update_deposit_publication_state_need',
            'update_deposit_metadata_need = '
            'b2share.modules.deposit.permissions:update_deposit_metadata_need',
            'update_record_metadata_need = '
            'b2share.modules.records.permissions:update_record_metadata_need',
            'assign_role_need = '
            'b2share.modules.users.permissions:assign_role_need',
            'search_accounts_need = '
            'b2share.modules.users.permissions:search_accounts_need',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,

    cmdclass={'test': PyTest},
)
