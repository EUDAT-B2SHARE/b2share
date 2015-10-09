# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

# """Invenio is a framework for digital libraries and data repositories.

# Invenio enables you to run your own digital library or document
# repository on the web.  Invenio covers all aspects of digital library
# management, from document ingestion, through classification, indexing
# and further processing, to curation, archiving, and dissemination.
# The flexibility and performance of Invenio make it a comprehensive
# solution for management of document repositories of moderate to large
# sizes (several millions of records).

# Links
# -----

# * `website <http://invenio-software.org/>`_
# * `documentation <http://invenio.readthedocs.org/en/latest/>`_
# * `development <https://github.com/inveniosoftware/invenio>`_

# """

"""B2Share application
"""  # FIXME improve this documentation

import os
import sys

from distutils.command.build import build

from setuptools import find_packages, setup
from setuptools.command.install_lib import install_lib


# class _build(build):  # noqa

#     """Compile catalog before building the package."""

#     sub_commands = [('compile_catalog', None)] + build.sub_commands


# class _install_lib(install_lib):  # noqa

#     """Custom install_lib command."""

#     def run(self):
#         """Compile catalog before running installation command."""
#         install_lib.run(self)
#         self.run_command('compile_catalog')


# install_requires = [

# ]


# extras_require = {
# }

# Get the version string.  Cannot be done with import!
g = {}
with open(os.path.join("b2share", "version.py"), "rt") as fp:
    exec(fp.read(), g)
version = g["__version__"]

# packages = find_packages(exclude=['docs'])
# packages.append('invenio_docs')

setup(
    name='b2share',
    version=version,
    url='https://github.com/EUDAT-B2SHARE/b2share',
    license='GPLv2',
    author='CERN',
    # author_email='info@invenio-software.org',
    description='B2Share application',
    long_description=__doc__,
    # packages=packages,
    # package_dir={'invenio_docs': 'docs'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    entry_points={
        'invenio.config': [
            'b2share = b2share.config'
        ]

        # "distutils.commands": [
        #     "inveniomanage = invenio.base.setuptools:InvenioManageCommand",
        # ]
    },
    install_requires=[
        'invenio>2.0',
        'invenio-oaiharvester',
        'invenio-oauth2server',
        'invenio-celery',
        'markdown2',
        'validate_email',
        'recaptcha-client',
        'markdown',
        'httplib2',
        'simplejson',
    ],
    extras_require={
        'development': [
            'Flask-DebugToolbar>=0.9',
            'setuptools-bower>=0.2'
        ],
    },
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'Flask-Testing'
    ],


    # setup_requires=setup_requires,
    # install_requires=install_requires,
    # extras_require=extras_require,
    # classifiers=[
    #     'Development Status :: 4 - Beta',
    #     'Environment :: Web Environment',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: GNU General Public License v2'
    #     ' or later (GPLv2+)',
    #     'Operating System :: OS Independent',
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: 2',
    #     'Programming Language :: Python :: 2.6',
    #     'Programming Language :: Python :: 2.7',
    #     'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    # ],
    # test_suite='invenio.testsuite.suite',
    # tests_require=tests_require,
    # cmdclass={
    #     'build': _build,
    #     'install_lib': _install_lib,
    # },
)
