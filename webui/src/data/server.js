import React from 'react';
import {fromJS} from 'immutable';
import {ajaxGet, ajaxPost} from './ajax'
import {objEquals} from './misc'

const urlRoot = window.location.origin;


const apiUrls = {
    users:          `${urlRoot}/api/users/`,
    userLogin:      `${urlRoot}/api/users/login/`,

    communities:    `${urlRoot}/api/communities/`,

    schemas:        `${urlRoot}/api/schemas/`,
    records:        `${urlRoot}/api/xrecords/`,
};


const SECONDS = 1000;
const MINUTES = 60 * SECONDS;
const FAR_FUTURE = 100 * 365 * 24 * 60 * MINUTES; // 100 years or so


const LATEST_RECORDS_CACHE_PERIOD = 1 * MINUTES;
const COMMUNITIES_CACHE_PERIOD = 1 * MINUTES;


class Timer {
    constructor(period) {
        // initially tick is 0, so ticking() returns false
        this.tick = 0;
        this.period = period || -1;
    }
    restart() {
        this.tick = Date.now()+this.period;
    }
    ticking() {
        return this.tick > Date.now();
    }
}


class Fetcher {
    constructor(url, timerPeriod) {
        this.url = url;
        this.requestSent = false;
        this.timer = new Timer(timerPeriod);
    }

    fetch(params, callback) {
        if (this.requestSent) {
            return;
        }
        if (this.timer.ticking()) {
            // cache considered still valid
            return;
        }
        if (this.params !== undefined && objEquals(params, this.params)) {
            // !! GET call considered idempotent
            return;
        }
        this.params = params;
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxGet(this.url, this.params,
                (dataJS) => {
                    callback(dataJS);
                    this.timer.restart();
                },
                () => { this.requestSent = false; }
            );
        }
    }
}


class Poster {
    constructor(url) {
        this.url = url;
        this.requestSent = false;
    }

    post(params, successFn) {
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxPost(this.url, params,
                successFn,
                () => { this.requestSent = false; }
            );
        }
    }
}


class Server {
    constructor() {
        this.store = null;
        this.latestRecords = new Fetcher(apiUrls.records, LATEST_RECORDS_CACHE_PERIOD);
        this.records = new Fetcher(apiUrls.records);
        this.communities = new Fetcher(apiUrls.communities, COMMUNITIES_CACHE_PERIOD);
        this.schemas = new Fetcher(apiUrls.schemas);

        this.newRecord = new Poster(apiUrls.records);
    }

    setStore(store) {
        this.store = store;
    }

    fetchLatestRecords() {
        const binding = store.branch('latestRecords');
        if (!binding.valid()) {
            return;
        }
        const params = {start:0, stop:10, sortBy:'date', order:'descending'};
        this.latestRecords.fetch(params, (json)=>{binding.set(fromJS(json.records))});
    }

    fetchRecords({start, stop, sortBy, order}) {
        const binding = store.branch('records');
        if (!binding.valid()) {
            return;
        }
        const params = {start:start, stop:stop, sortBy:sortBy, order:order};
        this.records.fetch(params, (json)=>{binding.set(fromJS(json.records))});
    }

    fetchRecord({id}) {
        const binding = store.branch('currentRecord');
        if (!binding.valid()) {
            return;
        }
        const params = {id:id};
        this.records.fetch(params, (json)=>{binding.set(fromJS(json.records))});
    }

    fetchCommunities() {
        const binding = store.branch('communities');
        if (!binding.valid()) {
            return;
        }
        this.communities.fetch(null, (json)=>{binding.set(fromJS(json.communities))});
    }

    fetchCommunitySchemas(communityID) {
        const findFn = (x) => x.get('id') == communityID || x.get('name') == communityID;
        const community = store.branch('communities').find(findFn);
        if (!community.valid()) {
            return ;
        }
        const schema_id_list = community.get('schema_id_list');
        const schemaIDs = schema_id_list ? schema_id_list.toJS() : [];
        if (schemaIDs.length) {
            const params = {schemaIDs:schemaIDs};
            this.schemas.fetch(params, (json)=>{community.setIn(['schema_list'], fromJS(json.schemas))});
        } else {
            community.setIn(['schema_list'], fromJS([]))
        }
    }

    createRecord(successFn) {
        this.newRecord.post(null, successFn);
    }
};


export const server = new Server();
