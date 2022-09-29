import Nightmare from 'nightmare';
import { B2ACCESS_AUTH_URL, B2SHARE_URL, USER_NAME, USER_PASS, USER_EMAIL,
         nightmareConfig, step, print_obj, assertPageContains, assertElementText } from './common';


describe('Homepage', function () {
    test('well formed homepage', async function () {
        let page = Nightmare(nightmareConfig).goto(B2SHARE_URL);
        expect(await page.title() == 'B2SHARE');

        await page.wait('#header-navbar-collapse a');
        await page.wait('#page .home-page .record a');
    });
});

describe('Login', function () {
    test('user can login', async function () {
        let page = Nightmare(nightmareConfig).goto(B2SHARE_URL);

        await page.wait('#header-navbar-collapse > .user > li > a')
                  .click('#header-navbar-collapse > .user > li > a');

        await expect(page.url() == B2ACCESS_AUTH_URL);

        await page.wait('#AuthenticationUI\\.username');
        await assertPageContains(page, "Login to UNITY OAuth2 Authorization Server");

        await page.type('#AuthenticationUI\\.username', USER_NAME)
                  .type('#WebPasswordRetrieval\\.password', USER_PASS)
                  .click('#AuthenticationUI\\.authnenticateButton')
                  .wait('#IdpButtonsBar\\.confirmButton')
                  .click('#IdpButtonsBar\\.confirmButton');

        expect(await page.title() == 'B2SHARE');

        await page.wait('#header-navbar-collapse a');

        await assertElementText(page, '#header-navbar-collapse > .user > li > a', USER_EMAIL);
    });
});
