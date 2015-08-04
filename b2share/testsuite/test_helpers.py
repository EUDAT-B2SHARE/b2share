# -*- coding: utf-8 -*-
# This file is part of B2SHARE.
# Copyright (C) 2015 CERN.
#
# B2SHARE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2SHARE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Tests of the test helpers"""

import unittest

from .helpers import TemporaryDirectory


class TestTemporaryDirectory(unittest.TestCase):
    """Test TemporaryDirectory context manager"""

    def test_temporary_directory(self):
        """Test dir creation and deletion"""
        import os.path
        dir_path = None
        file_path = None
        with TemporaryDirectory() as tmp_dir:
            dir_path = tmp_dir
            file_path = os.path.join(tmp_dir, "testfile.txt")
            # test that the directory exists
            self.assertTrue(os.path.isdir(dir_path))
            # test that we can create files in it
            with open(file_path, 'w') as file_desc:
                file_desc.write("mycontent")
            self.assertTrue(os.path.isfile(file_path))
        # check that the directory and file have been deleted
        self.assertFalse(os.path.isfile(file_path))
        self.assertFalse(os.path.isdir(dir_path))
