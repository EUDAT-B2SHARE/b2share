import Nightmare from 'nightmare';
import { B2ACCESS_AUTH_URL, B2SHARE_URL, USER_NAME, USER_PASS, USER_EMAIL,
         nightmareConfig, step, print_obj, assertPageContains, assertElementText, login } from './common';

describe('A published record', function () { 
    test('can be loaded and download the file', async function () { 
        let page = Nightmare(nightmareConfig).goto(B2SHARE_URL+'/records/47077e3c4b9f4852a40709e338ad4620');
        await expect(await page.title() == 'B2SHARE');

        await assertElementText(page, '.col-lg-6  .well  .fileList  .file  .row  .col-sm-9 ', 'myfile'); //file name exists
        await assertElementText(page, '.col-lg-6  .well  .fileList  .file  .row  .col-sm-3 ', '9 B'); // file size exists 

        await page.wait('.col-lg-6  .well  .fileList  .file  .row  .col-sm-9 > a')
            .click('.col-lg-6  .well  .fileList  .file  .row  .col-sm-9 > a')
            // .end()
            .then(function (result) {
                console.log(result)
            })
            .catch(function (error) {
                console.error('Error:', error);
            });
    });

    // test('should have a report abuse link', async function () { 
    //     let page = Nightmare(nightmareConfig).goto(B2SHARE_URL+'/records/47077e3c4b9f4852a40709e338ad4620');
    //     await expect(await page.title() == 'B2SHARE');
    //     await page.wait('.large-record  .row  .col-lg-12  a.btn.btn-default')
    //               .click('.large-record  .row  .col-lg-12  a.btn.btn-default')

    //     await expect(page.url() == B2SHARE_URL+'/records/47077e3c4b9f4852a40709e338ad4620/abuse');

    //     await page.click(' .form-horizontal  .row  .col-sm-1 > #abusecontent ') //checked
    //                 .type(' .form-horizontal  .row  .col-sm-8 > textarea ', 'message')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > input#name', 'firstname lastname')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > input#affiliation', 'affiliation')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > input#email', 'a@a.com')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > input#address', 'address')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > input#city', 'Stockholm')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > select#country', 'Sweden')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > input#zipcode', '12345')
    //                 .type(' .form-horizontal  .row  .col-sm-8  > input#phone', '6392615304')
    //                 .click(' .form-horizontal  .row  .col-sm-offset-2.col-sm-8  .btn.btn-primary.btn-default.btn-block')
    //               // .end()
    // });


    test('have basic metadata like open access, file size, file name', async function(){
        let page = Nightmare(nightmareConfig).goto(B2SHARE_URL+'/records/47077e3c4b9f4852a40709e338ad4620');

        await page.wait('.col-lg-6  .well  .col-sm-12.list-unstyled  li  .col-sm-8') //Open Access
                    .evaluate(function () {
                        return document.querySelector('.col-lg-6  .well  .col-sm-12.list-unstyled  li  .col-sm-8').innerText
                    })
                    .then(function(el) {
                        expect(el).toEqual('True');
                    })

        await page.wait('.col-lg-6  .well  .fileList  .file  .row  .col-sm-9 a') // File Name
                    .evaluate(function () {
                        console.log("value = ", document.querySelector('.col-lg-6  .well  .fileList  .file  .row  .col-sm-9 a').innerText)
                        return document.querySelector('.col-lg-6  .well  .fileList  .file  .row  .col-sm-9 a').innerText
                    })
                    .then(function(el) {
                        expect(el).toEqual('myfile');
                    })

        await page.wait('.col-lg-6  .well  .fileList  .file  .row  .col-sm-9 a') // File size
                    .evaluate(function () {
                        console.log("value = ", document.querySelector('.col-lg-6  .well  .fileList  .file  .row  .col-sm-3').innerText)
                        return document.querySelector('.col-lg-6  .well  .fileList  .file  .row  .col-sm-3').innerText
                    })
                    .then(function(el) {
                        expect(el.replace( /\s/g, "")).toEqual('9B');
                    })
    });
});

// Should move it after creating a new record with restrict access! 
// describe('A restricted published record', function () { 
//     test('have open access equal to false, have a request file link and send the request file form', async function(){
//         let page = Nightmare(nightmareConfig).goto(B2SHARE_URL+'/records/5e025f1af344444498ec555e7732fc7c');
//         await page.wait('.col-lg-6  .well  .col-sm-12.list-unstyled  li  .col-sm-8')
//                     .evaluate(function () {
//                         return document.querySelector('.col-lg-6  .well  .col-sm-12.list-unstyled  li  .col-sm-8').innerText
//                     })
//                     .then(function(el) {
//                         expect(el).toEqual('False');
//                     });

//         await page.wait('.large-record .row .col-lg-6  .well  a')
//                     .click('.large-record .row .col-lg-6  .well  a');

//         await expect(page.url() == B2SHARE_URL+'/records/5e025f1af344444498ec555e7732fc7c/accessrequest');

//         await page.type(' .form-horizontal  .row  .col-sm-8 > textarea ', 'message')
//                     .type(' .form-horizontal  .row  .col-sm-8  > input#name', 'firstname lastname')
//                     .type(' .form-horizontal  .row  .col-sm-8  > input#affiliation', 'affiliation')
//                     .type(' .form-horizontal  .row  .col-sm-8  > input#email', 'a@a.com')
//                     .type(' .form-horizontal  .row  .col-sm-8  > input#address', 'address')
//                     .type(' .form-horizontal  .row  .col-sm-8  > input#city', 'Stockholm')
//                     .type(' .form-horizontal  .row  .col-sm-8  > select#country', 'Sweden')
//                     .type(' .form-horizontal  .row  .col-sm-8  > input#zipcode', '12345')
//                     .type(' .form-horizontal  .row  .col-sm-8  > input#phone', '6392615304')
//                     .click(' .form-horizontal  .row  .col-sm-offset-2.col-sm-8  .btn.btn-primary.btn-default.btn-block')
//     });
// });

