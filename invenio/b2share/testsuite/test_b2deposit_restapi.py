# -*- coding: utf-8 -*-
"""Unit Tests for B2share restapi"""

from invenio.testsuite import InvenioTestCase
from invenio.testsuite import make_test_suite, run_test_suite


class TestB2depositRestapiConnect(InvenioTestCase):
    """Unit tests for restapi connecting"""

    def test_connect_with_oauth(self):
        # TODO: implement!
        self.assertTrue(False)

class TestB2depositRestapiRecord(InvenioTestCase):
    """Unit tests for restapi record"""

    def test_records(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_records_paginate(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_read_record_by_id(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_read_record_by_domain(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_create_record(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_update_record(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_delete_record(self):
        # TODO: implement!
        self.assertTrue(False)

TEST_SUITE = make_test_suite(TestB2depositRestapiConnect,
                TestB2depositRestapiRecord)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
