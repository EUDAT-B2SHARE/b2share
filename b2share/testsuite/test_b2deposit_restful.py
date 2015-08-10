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
"""Test the B2Deposit module API"""

from StringIO import StringIO

from itertools import chain, ifilter

from invenio.testsuite import make_test_suite, run_test_suite

from .helpers import B2ShareAPITestCase


class TestB2DepositRESTAPI(B2ShareAPITestCase):
    """Functional tests for the B2Deposit REST API"""

    generic_metadata = {
        "domain": "generic",
        "title": "Test title",
        "description": "Test description",
        "open_access": True,
    }
    rda_metadata = {
        "domain": "RDA",
        "title": "Test title",
        "description": "Test description",
        "open_access": True,
    }

    def setUp(self):
        super(TestB2DepositRESTAPI, self).setUp()
        # init user context
        self.create_and_login_user()

    def tearDown(self):
        self.remove_user()

    def test_create_and_submit_deposition_without_files(self):
        """Check that submitting a deposition without any file fails."""
        # create the deposition
        deposit_id = self.create_deposition(safe=True).json["deposit_id"]

        req = self.commit_deposition(deposit_id, self.generic_metadata)
        self.assertEqual(req.status_code, 400,
                         "deposition should not have been accepted without \
                         any file")

    def test_create_and_submit_deposition_with_files(self):
        """Check that submitting a deposition with files succeeds"""

        files = [("test_file_1.txt", "test content 1"),
                 ("test_file_2.txt", "test content 2")]
        record_id = self.create_valid_record(files, self.generic_metadata)
        # Check that the files are the same by retrieving them internally (not
        # though B2Deposit REST API)
        for file in files:
            record_file = self.get_record_file_content(record_id, file[0])
            self.assertEquals(file[1], record_file)

    def test_get_deposition_files(self):
        """Test listing a deposition's files"""
        # create a deposition
        deposit_id = self.create_deposition(safe=True).json["deposit_id"]
        files = [("test_file_1.txt", "test content 1"),
                 ("test_file_2.txt", "test my content 2")]

        # retrieve the list of deposition's files
        req_before = self.get_deposition_files(deposit_id, safe=True)
        # check that the result is a list
        self.assertTrue(isinstance(req_before.json["files"], list),
                        "result is not a list")
        # check that the list is empty
        self.assertEqual(len(req_before.json["files"]), 0,
                         "number of files do not match 0 (expected)!={0}"
                         .format(len(req_before.json)))
        # upload files
        for f in files:
            self.upload_deposition_file(deposit_id,
                                        file_name=f[0],
                                        file_stream=StringIO(f[1]),
                                        safe=True)

        # retrieve the list of deposition's files
        req_after = self.get_deposition_files(deposit_id, safe=True)
        # check that the result is a list
        self.assertTrue(isinstance(req_after.json["files"], list),
                        "result is not a list")
        files_after = req_after.json["files"]
        # check that the number of files match
        self.assertEqual(len(files_after), len(files),
                         "number of files do not match {0} (expected)!={1}"
                         .format(len(files), len(files_after)))
        # for each sent file
        for file in files:
            # search for the first corresponding file in the returned list
            found = next(ifilter(lambda f: f["name"] == file[0], files_after), None)
            # test if the file was found
            self.assertNotEqual(found, None,
                                "file {0} not found".format(file[0]))
            # check that the file size matches
            self.assertEqual(found["size"], len(file[1]),
                             "file {0} length is different".format(file[0]))

    def test_get_record(self):
        """Check that getting a record works"""
        files = [("test_file.txt", "test content")]
        record_id = self.create_valid_record(files, self.generic_metadata)

        record_request = self.get_record(record_id, safe=True)
        record_content = record_request.json
        # check that the returned record ID matches
        self.assertEquals(record_content["record_id"],
                          int(record_id))
        # check that every metadata field is here
        for key in self.generic_metadata:
            expected_value = self.generic_metadata[key]
            self.assertEquals(record_content[key], expected_value)

        # check the number of files
        self.assertTrue("files" in record_content and
                        isinstance(record_content["files"], list),
                        "files list is not set or not a list")
        self.assertEqual(len(record_content["files"]), len(files),
                         "number of files do not match {0} (expected) != {1}"
                         .format(len(files), len(record_content["files"])))

        # check files metadata
        for file in files:
            # search for the first corresponding file in the returned list
            found = next(ifilter(lambda f: f["name"] == file[0],
                                 record_content["files"]), None)
            # test if the file was found
            self.assertNotEqual(found, None,
                                "file {0} not found".format(file[0]))
            # check that the file size matches
            self.assertEqual(found["size"], len(file[1]),
                             "file {0} length is different".format(file[0]))

    def test_get_records(self):
        """Check that listing records works"""
        # list records before adding new records
        records_before = self.scan_records()

        # create two records with different domains
        files = [("test_file.txt", "test content")]
        gen_record_id = self.create_valid_record(files, self.generic_metadata)
        rda_record_id = self.create_valid_record(files, self.rda_metadata)

        gen_record_request = self.get_record(gen_record_id, safe=True)
        rda_record_request = self.get_record(rda_record_id, safe=True)

        # list records after adding new records
        records_after = self.scan_records()

        # both records should appear in the list
        records_before.append(gen_record_request.json)
        records_before.append(rda_record_request.json)

        # sort the records on record_id
        records_after.sort(key=lambda rec: rec["record_id"])
        records_before.sort(key=lambda rec: rec["record_id"])
        self.assertEquals(records_after, records_before,
                          "records list did not update properly")

    def test_get_records_by_domain(self):
        """Check that listing records by domain works"""
        # list records before adding new records
        records_before = self.scan_records("generic")

        # create two records with different domains
        files = [("test_file.txt", "test content")]
        gen_record_id = self.create_valid_record(files, self.generic_metadata)
        rda_record_id = self.create_valid_record(files, self.rda_metadata)

        gen_record_request = self.get_record(gen_record_id, safe=True)
        self.get_record(rda_record_id, safe=True)

        # list records after adding new records
        records_after = self.scan_records("generic")

        # the "generic" record should appear in the list but not the "rda" one
        records_before.append(gen_record_request.json)

        # sort the records on record_id
        records_after.sort(key=lambda rec: rec["record_id"])
        records_before.sort(key=lambda rec: rec["record_id"])

        self.assertEquals(records_after, records_before,
                          "records list did not update properly")

    #
    # Helpers
    #
    def create_valid_record(self, files, metadata):
        """Create a valid record and check the server answer.

        :Parameters:
            - `files` (list) - list of files as tuples (file_name, file_content)
            - `metadata` (dict) - record"s metadata
        :Returns: record id
        :Returns Type: int
        """
        # create the deposition
        deposit_id = self.create_deposition(safe=True).json["deposit_id"]

        # upload files
        for f in files:
            self.upload_deposition_file(deposit_id,
                                        file_name=f[0],
                                        file_stream=StringIO(f[1]),
                                        safe=True)

        # commit the deposition
        request_commit = self.commit_deposition(deposit_id, metadata, safe=True)
        # return the record
        return request_commit.json["record_id"]

    def scan_records(self, domain=None):
        """Retrieve all records or all records related to a given domain

        :Parameters:
            - `domain` (str): if set, only records matching the given domain will
            be returned.
        :Returns: a list of records
        :Returns Type: list
        """
        # FIXME there is no way currently to have the number of available records
        scan_end = False
        results = []
        current_page = 0
        while not scan_end:
            if domain is None:
                req = self.get_records(page_offset=current_page,
                                       safe=True)
            else:
                req = self.get_records_by_domain(domain,
                                                 page_offset=current_page,
                                                 safe=True)
            # check result format
            self.assertTrue("records" in req.json and
                            isinstance(req.json["records"], list))
            # add the result list and continue if it is not empty
            if len(req.json["records"]) > 0:
                current_page += 1
                results.append(req.json["records"])
            else:
                scan_end = True
        # merge all the result lists in one list
        return list(chain.from_iterable(results))

TEST_SUITE = make_test_suite(TestB2DepositRESTAPI)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
