from invenio.testutils import (make_test_suite, run_test_suite, InvenioTestCase,
                               test_web_page_content,
                               get_authenticated_mechanize_browser)
from invenio.config import CFG_SITE_SECURE_URL
from bs4 import BeautifulSoup
import requests


class DepositTest(InvenioTestCase):

    def test_must_login(self):
        """Checks users are asked to login before deposit."""
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

    def test_deposit(self):
        """Test "happy path" - deposit a new file with metadata"""

        br = get_authenticated_mechanize_browser(username="admin", password="")
        res = br.open(CFG_SITE_SECURE_URL + '/deposit')
        assert br.viewing_html()
        dep_soup = BeautifulSoup(res.get_data())
        sub_id = dep_soup.find_all(id='sub_id')[0]['value']
        form = {'nickname': 'admin',
                'password': ''}
        login = requests.post('%s/youraccount/login' % CFG_SITE_SECURE_URL,
                              data=form,
                              verify=False)
        form = {'name': "testfile"}
        files = {'file': "test data"}
        r = requests.post("%s/deposit/upload/%s" % (CFG_SITE_SECURE_URL, sub_id),
                          files=files,
                          data=form,
                          verify=False,
                          cookies=login.cookies)

        self.assertEqual(r.status_code, 200)

        #check we can get it back again
        r = requests.get("%s/deposit/get_file/%s?filename=%s"
                         % (CFG_SITE_SECURE_URL, sub_id, "testfile"),
                         verify=False,
                         cookies=login.cookies)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, "test data")

        #Do the submission
        br.select_form(nr=0)
        br['domain'] = ['Generic']
        resp = br.submit()

        self.assertIn('addmeta', resp.geturl())

        #add some metadata
        br.select_form(nr=0)
        br['creator'] = 'Test Bot'
        resp = br.submit()

        #check we got to the last page
        self.assertIn("Your submission will shortly be available", resp.read())


TEST_SUITE = make_test_suite(DepositTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
