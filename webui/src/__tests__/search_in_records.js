import Nightmare from 'nightmare';
import { B2ACCESS_AUTH_URL, B2SHARE_URL, USER_NAME, USER_PASS, USER_EMAIL,
         nightmareConfig, step, print_obj, assertPageContains, assertElementText, login } from './common';

describe('Searching in the records', function () { 
    test('for a common term',  async function() {
        let queries = ['paper','ChiP-seq','Daniel Zeman', 'RDA', 'wrong_query'];

        for (let query of queries) {
            let page = Nightmare(nightmareConfig).goto(B2SHARE_URL);
            await page.wait('#header-navbar-collapse  form  .nav-search  .form-control')
                        .type('#header-navbar-collapse  form  .nav-search  .form-control', query)
                        .click('#header-navbar-collapse  form  .nav-search .input-group-btn  button.btn.btn-primary')

            await expect(page.url() == B2SHARE_URL+'/records/?q='+query+'#');
            switch(query){
                case 'wrong_query': 
                    await page.evaluate(()=>document.body.textContent)
                                .then(function(body){
                                    expect(body).toContain('No results');    
                                })
                    page.end();
                    break;
                default:
                    await page.wait('.record.col-lg-12')
                                .evaluate(()=>document.body.textContent)
                                .then(function(body){
                                    expect(body).toContain('1 - 1 of 1 results');    
                                })
                    page.end();                
            }

        }  
    });

});