import {fromJS} from 'immutable';
import {ajaxGet, ajaxPost} from './ajax'
import {Store} from './store'
import {objEquals} from './misc'

const urlRoot = window.location.origin;


const apiUrls = {
    users:          `${urlRoot}/api/users/`,
    userLogin:      `${urlRoot}/api/users/login/`,

    communities:    `${urlRoot}/api/communities/`,

    schemas:        `${urlRoot}/api/schemas/`,
    records:        `${urlRoot}/api/xrecords/`,
};


class Timer {
    constructor(period) {
        // initially tick is 0, so ticking() returns false
        this.tick = 0;
        this.period = period || -1;
    }
    restart() {
        this.tick = Date.now()+this.period;
    }
    elapsed() {
        return this.tick <= Date.now();
    }
}


class Getter {
    constructor(url) {
        this.url = url;
        this.requestSent = false;
    }

    get(params, callback) {
        return this.getWithPathParam("", params, callback);
    }

    getWithPathParam(pathParam, params, successFn, errorFn) {
        if (this.requestSent) {
            return;
        }
        this.requestSent = true;
        ajaxGet(this.url+pathParam, params,
            (dataJS) => { successFn(dataJS); },
            errorFn,
            () => { this.requestSent = false; }
        );
    }
}


class Poster {
    constructor(url) {
        this.url = url;
        this.requestSent = false;
    }

    post(params, successFn, errorFn) {
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxPost(this.url, params,
                successFn,
                errorFn,
                () => { this.requestSent = false; }
            );
        }
    }
}


const serverApi = {
    records : new Getter(apiUrls.records),
    communities : new Getter(apiUrls.communities),
    schemas : new Getter(apiUrls.schemas),
    newRecord : new Poster(apiUrls.records),
};


// todo: handle http error cases
class ServerCache {
    constructor() {
        this.store = new Store({
            user: {
                name: null,
            },

            latestRecords: [], // full list of latest records
            recordsCache: {}, // map of record IDs to records
            searchRecords: [], // full list of searched records

            communities: [], // full list of communities
        });

        this.user = store.branch(['user']);

        this.latestRecords = store.branch(['latestRecords']);
        this.recordsCache = store.branch(['recordsCache']);
        this.searchRecords = store.branch(['searchRecords']);

        this.communities = store.branch(['communities']);
    }

    _fetchLatestRecords() {
        const setter = (json) => { this.latestRecords.set(fromJS(json.records)) };
        const params = {start:0, stop:10, sortBy:'date', order:'descending'};
        serverApi.records.get(params, setter);
    }

    _fetchRecords({start, stop, sortBy, order}) {
        const setter = (json) => { this.searchRecords.set(fromJS(json.records)) };
        const params = {start:start, stop:stop, sortBy:sortBy, order:order};
        serverApi.records.get(params, setter);
    }

    _fetchRecord(id) {
        const setter = (json) => { this.recordsCache.update((a) => a.push(json)); };
        serverApi.records.getWithPathParam(id, {}, setter);
    }

    _fetchCommunities() {
        const setter = (json) => { this.communities.set(fromJS(json.communities)) };
        serverApi.communities.get(null, setter);
    }

    _fetchCommunitySchemas(communityID) {
        const findFn = (x) => x.get('id') == communityID || x.get('name') == communityID;
        const community = this.communities.find(findFn);
        if (!community) {
            console.error('fetchCommunitySchemas: unfetched community:', communityID);
            return ;
        }
        // todo: finish fetching community schemas
    }

    getLatestRecords() {
        const records = this.latestRecords.get();
        if (!records) {
            this._fetchLatestRecords();
        }
        return records;
    }

    getRecords({start, stop, sortBy, order}) {
        // todo: implement this
    }

    getRecord(id) {
        const findFn = (x) => x.get('id') == id;
        const record = this.recordsCache.find(findFn);
        if (!record) {
            this._fetchRecord(id);
        }
        return record;
    }

    getCommunities() {
        const communities = this.communities.get();
        if (!communities) {
            this._fetchCommunities();
        }
        return communities;
    }

    getCommunitySchemas(communityID) {
        //todo
    }

    getUser() {
        //todo: fix this
        return this.user.get();
    }

    createRecord(initialMetadata, successFn) {
        const json = {
            metadata: initialMetadata
        };
        serverApi.newRecord.post(json, successFn);
    }

    updateRecord(metadata) {
        const json = {
            metadata: metadata
        };
        this.recordsCache.update(records => {
            records.set(json);
        });
        serverApi.records.post(json, successFn);
    }
};


export const serverCache = new ServerCache();
