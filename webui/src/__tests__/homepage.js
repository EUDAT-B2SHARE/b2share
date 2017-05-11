import Nightmare from 'nightmare'

jasmine.DEFAULT_TIMEOUT_INTERVAL=20*1000;

const B2ACCESS_AUTH_URL = "https://unity.eudat-aai.fz-juelich.de:8443/oauth2-as/oauth2-authz-web-entry"

const user = process.env.AUTOTEST_USER;
const pass = process.env.AUTOTEST_PASS;
const email = process.env.AUTOTEST_EMAIL;

if (!user || !pass || !email) {
    console.log("user, pass and email environment variables not defined!");
    console.log(user, pass, email);
}

var nightmare = Nightmare({
    show: true,
    switches: {
        'ignore-certificate-errors': true,
    },
});

function step(msg) {
    console.log(msg, "...")
}

async function assertPageContains(page, text) {
    let body = await page.evaluate(()=>document.body.textContent).end();
    expect(body).toContain(text);
}

async function assertElementText(page, selector, text) {
    const fn = (selector) => {
        document.querySelector(selector).innerText
    };
    let elementText = await page.evaluate(fn).end();
    expect(elementText == text);
}

describe('Smoke test', function () {
    let page = nightmare.goto('https://localhost/');

    test('well formed homepage', async function () {
        step("test homepage title")
        expect(page.title() == 'B2SHARE');

        step("wait for menu")
        await page.wait('#header-navbar-collapse a');

        step("wait for records")
        await page.wait('#page .home-page .record a');
    });

    test('user can login', async function () {
        step("click on Login")
        await page.click('#header-navbar-collapse > .user > li > a');

        step("check if redirected to B2ACCESS")
        await expect(page.url() == B2ACCESS_AUTH_URL);

        step("check if we are on B2ACCESS unity auth page")
        await page.wait('#AuthenticationUI\\.username');
        await assertPageContains(page, "Login to UNITY OAuth2 Authorization Server");

        step("authenticate")
        await page.type('#AuthenticationUI\\.username', user)
            .type('#WebPasswordRetrieval\\.password', pass)
            .click('#AuthenticationUI\\.authnenticateButton');

        step("check if we are on B2ACCESS unity confirmation page")
        await assertPageContains(page, "A remote client has requested your authorization");

        step("confirm")
        await page.click('#IdpButtonsBar\\.confirmButton');

        step("check if we are back to B2SHARE")
        expect(page.title() == 'B2SHARE');

        step("wait for menu")
        await page.wait('#header-navbar-collapse a');

        step("check that the test user is logged in")
        await assertElementText(page, '#header-navbar-collapse > .user > li > a', email);
    });
})
