import React from 'react';
import Immutable from 'immutable';
import reqwest from 'reqwest'


export let errorHandler = function(text){};


export function ajaxGet(url, params, successFn, completeFn) {
    console.log("ajaxGet:", url, params);
    const aobj = {
        url: url,
        type: 'json',
        contentType: 'application/json',
        success: successFn,
        complete: completeFn,
    }
    if (params) {
        aobj.data = params;
    }
    if (!aobj.complete) {
        aobj.complete = function(){};
    }
    return ajaxWithError(aobj);
}


function ajaxWithError(ajaxObject) {
    if (!ajaxObject.error) {
        ajaxObject.error = function(xhr) {
            console.error("ajax error, xhr: ", xhr);
            if (!xhr) {
                errorHandler("Unexpected error");
                return;
            }
            if (xhr.readyState === 0) {
                errorHandler("Network error, please check your internet connection");
            } else {
                errorHandler(`Error: ${xhr.statusText}`);
            }
        };
    }

    ajaxWithToken(ajaxObject);
};


let userToken = "";
function getSessionUserToken() { return userToken; }
function setSessionUserToken(token) { userToken = token; }


function ajaxWithToken(ajaxObject) {
    let request = null;

    const token = getSessionUserToken();
    if (token && ajaxObject.url.startsWith("http")) {
        ajaxObject.headers = ajaxObject.headers || {};
        ajaxObject.headers['Authorization'] = 'B2SHARE ' + token;
    }

    const oldSuccess = ajaxObject.success;
    ajaxObject.success = function(data) {
        const prefix = "B2SHARE";
        if (ajaxObject.url.startsWith("http")) {
            var token = request.getResponseHeader('x-token');
            if (token && token.startsWith(prefix)) {
                token = token.substring(prefix.length +1, token.length);
                setSessionUserToken(token);
            }
        }
        console.log('ajaxRet:', ajaxObject.url, data);
        return oldSuccess(data);
    }

    const oldError = ajaxObject.error;
    ajaxObject.error = function(xhr) {
        if (xhr.status == 401) {
            setSessionUserToken("");
        }
        return oldError(xhr);
    }

    request = reqwest(ajaxObject).request;
};
