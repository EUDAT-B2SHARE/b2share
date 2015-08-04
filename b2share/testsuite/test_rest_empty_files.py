# -*- coding: utf-8 -*-
"""Tests for REST API: empty files"""

from invenio.testsuite import make_test_suite, run_test_suite

from .helpers import B2ShareAPITestCase, TemporaryDirectory, create_file

from flask import current_app

class TestB2ShareEmptyFiles(B2ShareAPITestCase):
    """Unit tests for the REST API: empty files should be rejected"""

    def setUp(self):
        super(TestB2ShareEmptyFiles, self).setUp()
        self.create_and_login_user()

    def tearDown(self):
        self.remove_user()

    def test_rest_api_error_on_empty_file(self):
        current_app.config.update(PRESERVE_CONTEXT_ON_EXCEPTION = False)

        create_json = self.create_deposition(safe=True).json
        deposit_id = create_json['deposit_id']

        valid_file_name = "valid.txt"
        with TemporaryDirectory() as tmp_dir:
            # valid file
            file1 = create_file(tmp_dir, valid_file_name, "test file 1")
            self.upload_deposition_file(deposit_id, file_path=file1, safe=True)

            # empty file
            file2 = create_file(tmp_dir, "empty.txt", "")
            request = self.upload_deposition_file(deposit_id, file_path=file2)
            self.assertTrue(request.status_code == 400)
            self.assertTrue(request.json['errors'])

        metadata = {
            'domain': "generic",
            'title': 'Empty file test',
            'description': "Test of empty file rejection via RestAPI",
            'open_access': "true"
        }

        # commit deposition
        commit_json = self.commit_deposition(deposit_id, metadata,
                                             safe=True).json
        record_id = commit_json['record_id']

        # get record and test files
        record_json = self.get_record(record_id, safe=True).json
        record_files = [f.get('name') for f in record_json['files']]
        self.assertEquals(record_files, [valid_file_name])


TEST_SUITE = make_test_suite(TestB2ShareEmptyFiles)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
