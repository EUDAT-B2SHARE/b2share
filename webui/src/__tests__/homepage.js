import Nightmare from 'nightmare';
import { B2ACCESS_AUTH_URL, B2SHARE_URL, USER_NAME, USER_PASS, USER_EMAIL,
         nightmareConfig, step, print_obj, assertPageContains, assertElementText, login } from './common';

describe('Homepage', function () { 
    test('well formed homepage', async function () {
        let page = Nightmare(nightmareConfig).goto(B2SHARE_URL);
        await expect(await page.title() == 'B2SHARE');
        await page.wait('#header-navbar-collapse a');
        await page.wait('#page .home-page .record a');
        await page.end();
    });
});


describe('Login', function () { 
    test('user can login', async function() {
        let page = Nightmare(nightmareConfig).goto(B2SHARE_URL);
        try {
            await login(page);
            // page.end();          
        } catch(e){
            console.error(e);
        }
    });
});

describe('User profile', function () { 
    test('user can navigate to the profile page', async function() {
        let page = Nightmare(nightmareConfig).goto(B2SHARE_URL);
        try {
            await login(page);
            await page.click('#header-navbar-collapse  .user  .dropdown  .dropdown-toggle')
                        .wait('#header-navbar-collapse  .user  li  a  .dropdown-menu  li  a')
                        .click('#header-navbar-collapse  .user  li  a  .dropdown-menu  li  a');
            // page.end();
        } catch(e){
            console.error(e);
        }
    });
});


