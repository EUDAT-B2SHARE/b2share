# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
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

"""B2Share demonstration."""

from setuptools import find_packages, setup

setup(
    name='b2share_demo',
    packages=find_packages(),
    entry_points={
        'invenio_base.api_apps': [
            'b2share_demo = b2share_demo:B2ShareDemo',
        ],
        # 'console_scripts': [
        #     'b2share = b2share_demo.cli:cli'
        # ],
    },
    install_requires=[
        'b2share>=2.0.0.beta-2',
    ],
)
