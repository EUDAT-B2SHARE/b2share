# -*- coding: utf-8 -*-
"""Tests for access control"""

from invenio.testsuite import make_test_suite, run_test_suite

from .helpers import B2ShareAPITestCase, TemporaryDirectory, create_file

from flask import current_app

class TestB2ShareRecordAccessControl(B2ShareAPITestCase):
    """Unit testing access control per record"""

    def metadata(self, open_access):
        return {
            'domain': "generic",
            'title': 'UnitTest: Record Access Control ' +
                ('public' if open_access else 'private'),
            'description':  'This record is automatically created '
                            'for the purpose of testing Record Access Control',
            'open_access': open_access,
        }

    def make_record(self, open_access):
        create_json = self.create_deposition(safe=True).json
        deposit_id = create_json['deposit_id']

        with TemporaryDirectory() as tmp_dir:
            file = create_file(tmp_dir, "testfile.txt", "test file 1")
            self.upload_deposition_file(deposit_id, file_path=file, safe=True)

        commit_json = self.commit_deposition(deposit_id,
                            self.metadata(open_access), safe=True).json
        record_id = commit_json['record_id']
        record_json = self.get_record(record_id, safe=True).json
        return record_json.get('record_id')

    def test_record_access_for_edit(self):
        from invenio.b2share.modules.b2deposit.edit import is_record_editable,\
                                                    get_domain_admin_group
        current_app.config.update(PRESERVE_CONTEXT_ON_EXCEPTION = False)

        self.create_and_login_user("the_owner")
        public_record = self.make_record(open_access=True)
        private_record = self.make_record(open_access=False)
        self.assertFalse(is_record_editable(public_record))
        self.assertTrue(is_record_editable(private_record))
        self.remove_user()

        self.create_and_login_user("the_domain_admin")
        admin_group = get_domain_admin_group(self.metadata(True).get('domain'))
        self.add_current_user_to_group(admin_group)
        self.assertFalse(is_record_editable(public_record))
        self.assertTrue(is_record_editable(private_record))
        self.remove_current_user_from_group(admin_group)
        self.remove_user()

        self.create_and_login_user("the_third")
        self.assertFalse(is_record_editable(public_record))
        self.assertFalse(is_record_editable(private_record))
        self.remove_user()


TEST_SUITE = make_test_suite(TestB2ShareRecordAccessControl)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
