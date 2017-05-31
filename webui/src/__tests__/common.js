import Nightmare from 'nightmare';

jasmine.DEFAULT_TIMEOUT_INTERVAL=60*1000;

export const nightmareConfig = {
    // show: true,
    switches: {
        'ignore-certificate-errors': true,
    },
};

export const B2ACCESS_AUTH_URL = "https://unity.eudat-aai.fz-juelich.de/oauth2-as/oauth2-authz-web-entry";

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

export async function getBodyText() {
    return document.body.innerText.trim();
}

export async function getElementText(selector) {
    return document.querySelector(selector).innerText.trim();
}

export async function getElementsJoinedText(selector) {
    const ret = [];
    for (var el in document.querySelectorAll(selector)) {
        ret.push(el.innerText.trim());
    }
    return ret.join("\n")
}

export async function login(page) {
    console.log("login started");
    expect(page).toBeInstanceOf(Nightmare);

    await page.wait('#header-navbar-collapse > .user > li > a')
            .click('#header-navbar-collapse > .user > li > a');

    const url = await page.url();
    expect(url).toEqual(B2ACCESS_AUTH_URL);

    await page.wait('#AuthenticationUI\\.username');
    const body = await page.evaluate(getBodyText);
    expect(body).toContain("Login to UNITY OAuth2 Authorization Server");

    await page.type('#AuthenticationUI\\.username', USER_NAME)
            .type('#WebPasswordRetrieval\\.password', USER_PASS)
            .click('#AuthenticationUI\\.authnenticateButton')
            .wait('#IdpButtonsBar\\.confirmButton')
            .click('#IdpButtonsBar\\.confirmButton')
            .wait('#header-navbar-collapse > .user > li > a');

    expect(await page.title()).toEqual('B2SHARE');

    const emailText = await page.evaluate(getElementText, '#header-navbar-collapse > .user > li > a');
    expect(emailText).toEqual(USER_EMAIL);

    console.log("login succeeded");
}
