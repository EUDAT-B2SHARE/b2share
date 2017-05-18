import Nightmare from 'nightmare'

jasmine.DEFAULT_TIMEOUT_INTERVAL=20*1000;

const B2SHARE_URL = "https://b2share.local/"
const B2ACCESS_AUTH_URL = "https://unity.eudat-aai.fz-juelich.de:8443/oauth2-as/oauth2-authz-web-entry"

const user = process.env.AUTOTEST_USER;
const pass = process.env.AUTOTEST_PASS;
const email = process.env.AUTOTEST_EMAIL;

if (!user || !pass || !email) {
    console.log("user, pass and email environment variables not defined!");
    console.log(user, pass, email);
}

var nightmare = Nightmare({
    // show: true,
    switches: {
        'ignore-certificate-errors': true,
    },
});

function step(msg) {
    console.log(msg, "...")
}
function print_obj(o) {
    for (var p in o) {
        console.log(p)
    }
}

async function assertPageContains(page, text) {
    let body = await page.evaluate(()=>document.body.textContent);
    await expect(body).toContain(text);
}

async function assertElementText(page, selector, text) {
    const fn = (selector) => {
        document.querySelector(selector).innerText
    };
    let elementText = await page.evaluate(fn, selector);
    return expect(elementText == text);
}

describe('Smoke test', function () {
    test('well formed homepage', async function () {
        let page = nightmare.goto(B2SHARE_URL);

        step("test homepage title");
        expect(await page.title() == 'B2SHARE');

        step("wait for menu")
        await page.wait('#header-navbar-collapse a');

        step("wait for records")
        await page.wait('#page .home-page .record a');
    });
});

describe('Smoke test2', function () {
    test('user can login', async function () {
        let page = nightmare.goto(B2SHARE_URL);

        step("click on Login");
        await page.wait('#header-navbar-collapse > .user > li > a')
                  .click('#header-navbar-collapse > .user > li > a');

        step("check if redirected to B2ACCESS");
        await expect(page.url() == B2ACCESS_AUTH_URL);

        step("check if we are on B2ACCESS unity auth page");
        await page.wait('#AuthenticationUI\\.username');
        await assertPageContains(page, "Login to UNITY OAuth2 Authorization Server");

        step("authenticate with user1");
        await page.type('#AuthenticationUI\\.username', user)
                  .type('#WebPasswordRetrieval\\.password', pass)
                  .click('#AuthenticationUI\\.authnenticateButton')
                  .wait('#IdpButtonsBar\\.confirmButton')
                  .click('#IdpButtonsBar\\.confirmButton');

        step("check if we are back to B2SHARE");
        expect(page.title() == 'B2SHARE');

        step("wait for menu");
        await page.wait('#header-navbar-collapse a');

        step("check that the test user is logged in");
        await assertElementText(page, '#header-navbar-collapse > .user > li > a', email);
    });
});
