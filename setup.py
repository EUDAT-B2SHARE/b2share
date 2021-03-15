# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 EUDAT.
#
# B2SHARE is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""EUDAT Collaborative Data Infrastructure."""

import os, sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

readme = open('README.rst').read()

tests_require = [
]

extras_require = {
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('sqlite', 'mysql', 'postgresql') \
            or name.startswith('elasticsearch'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
]

install_requires = [
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

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('b2share', 'version.py'), 'rt') as fp:
	exec(fp.read(), g)
	version = g['__version__']

def my_setup(**kwargs):
	with open('entry_points.txt', 'r') as f:
		entry_point = None

		for line in [l.rstrip() for l in f]:

			if line.startswith('[') and line.endswith(']'):
				entry_point = line.lstrip('[').rstrip(']')

			else:
				if 'entry_points' not in kwargs:
					kwargs['entry_points'] = {}

				if entry_point not in kwargs['entry_points']:
					kwargs['entry_points'][entry_point] = []

				if entry_point and line > '':
					kwargs['entry_points'][entry_point].append(line)

	setup(**kwargs)

my_setup(
	name='b2share',
	version=version,
	description=__doc__,
	long_description=readme,
	keywords='b2share Invenio',
	license='MIT',
	author='EUDAT',
	author_email='info@eudat.eu',
	url='https://github.com/HarryKodden/b2share-new',
	packages=packages,
	zip_safe=False,
	include_package_data=True,
	platforms='any',
	entry_points={
	},
	classifiers=[
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Development Status :: 3 - Alpha',
	],
	extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
)
