import Nightmare from 'nightmare';

jasmine.DEFAULT_TIMEOUT_INTERVAL=20*1000;

export const nightmareConfig = {
    // show: true,
    switches: {
        'ignore-certificate-errors': true,
    },
};

export const B2ACCESS_AUTH_URL = "https://unity.eudat-aai.fz-juelich.de:8443/oauth2-as/oauth2-authz-web-entry";

export const B2SHARE_URL = process.env.B2SHARE_URL || process.env.B2SHARE_JSONSCHEMAS_HOST;
export const USER_NAME = process.env.AUTOTEST_USER;
export const USER_PASS = process.env.AUTOTEST_PASS;
export const USER_EMAIL = process.env.AUTOTEST_EMAIL;

if (!B2SHARE_URL) {
    console.log("B2SHARE_URL environment variables not defined!");
}

if (!USER_NAME || !USER_PASS || !USER_EMAIL) {
    console.log("username or password or email environment variables not defined!");
}

export function step(msg) {
    console.log(msg, "...");
}

export function print_obj(o) {
    for (var p in o) {
        console.log(p);
    }
}

export async function assertPageContains(page, text) {
    let body = await page.evaluate(()=>document.body.textContent);
    await expect(body).toContain(text);
}

export async function assertElementText(page, selector, text) {
    const fn = (selector) => {
        document.querySelectorAll(selector).innerText
    };
    let elementText = await page.evaluate(fn, selector);
    await expect(elementText == text);
}

export async function login(page) {
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
              
    await expect(await page.title() == 'B2SHARE');

    await page.wait('#header-navbar-collapse a');

    await assertElementText(page, '#header-navbar-collapse > .user > li > a', USER_EMAIL);
    // await page.end();
}
