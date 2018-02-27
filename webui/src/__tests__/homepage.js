import Nightmare from 'nightmare';
import { B2SHARE_URL, nightmareConfig, login } from './common';


describe('Homepage', function () {
    test('well formed homepage', async function () {
        const page = Nightmare(nightmareConfig).goto(B2SHARE_URL);

        const title = await page.title();
        expect(title).toEqual('B2SHARE');

        await page.wait('#header-navbar-collapse a');
        await page.wait('#page .home-page .record a');
        await page.end();
    });
});

describe('Login', function () {
    test('user can login', async function () {
        const page = Nightmare(nightmareConfig).goto(B2SHARE_URL);
        await expect(await page.title() == 'B2SHARE');
        await login(page);
        await page.end();
    });
});
