from invenio.testutils import (make_test_suite, run_test_suite, InvenioTestCase,
                               test_web_page_content)
from invenio.config import CFG_SITE_SECURE_URL


class DepositTest(InvenioTestCase):

    def testMustLogIn(self):
        res = test_web_page_content(CFG_SITE_SECURE_URL + '/deposit',
                                    username="guest",
                                    password="",
                                    expected_text="Please Sign In")
        self.assertEqual(res, [])
        res = test_web_page_content(CFG_SITE_SECURE_URL + '/deposit',
                                    username="admin",
                                    password="",
                                    unexpected_text="Please Sign In")
        self.assertEqual(res, [])


TEST_SUITE = make_test_suite(DepositTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
