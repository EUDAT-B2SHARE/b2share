import {fromJS} from 'immutable';
import {ajaxGet, ajaxPost, errorHandler} from './ajax'
import {Store} from './store'
import {objEquals, expect} from './misc'

const urlRoot = window.location.origin;


const apiUrls = {
    users()                           { return `${urlRoot}/api/users/` },
    userLogin()                       { return `${urlRoot}/api/users/login/` },

    records()                         { return `${urlRoot}/api/records/` },
    record(id)                        { return `${urlRoot}/api/records/${id}` },

    communities()                     { return `${urlRoot}/api/communities/` },
    community(id)                     { return `${urlRoot}/api/communities/${id}` },
    communitySchema(cid, version)     { return `${urlRoot}/api/communities/${cid}/schemas/${version}` },

    schema(id, version)               { return `${urlRoot}/api/schemas/${id}/versions/${version}` },

    extractSchemaVersionFromUrl(schemaURL) {
        const m = /\/versions\/(\d+).*/.match(schemaURL);
        if (m && m[1]) {
            return m[1]
        }
        if (/\/versions\/last.*/.match(schemaURL)) {
            return 'last';
        }
        return null;
    },
};


const GETTER_HYSTERESIS_INTERVAL_MS = 15; // one frame time


class Timer {
    constructor(period) {
        this.tick = 0;
        this.period = period || 0;
    }
    restart() {
        this.tick = Date.now();
    }
    ticking() {
        return Date.now() < this.tick + this.period;
    }
}


class Getter {
    constructor(url, params, fetchSuccessFn) {
        this.url = url;
        this.params = params;
        this.etag = null;
        this.timer = new Timer(GETTER_HYSTERESIS_INTERVAL_MS);
        this.fetchSuccessFn = fetchSuccessFn;
    }

    autofetch() {
        this.fetch(this.params);
    }

    fetch(params) {
        if (this.timer.ticking() && objEquals(params, this.params)) {
            console.log('hysteresis!');
            return;
        }
        this.timer.restart();
        this.params = params;
        ajaxGet({
            url: this.url,
            params: this.params,
            etag: this.etag,
            successFn: (data, etag) => {
                this.etag = etag;
                this.fetchSuccessFn(data);
            },
        });
    }
}


class Poster {
    constructor(url) {
        this.url = url;
        this.requestSent = false;
        console.log('new poster', url);
    }

    post(params, successFn) {
        console.log('post', this.url, params);
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxPost({
                url: this.url,
                params: params,
                successFn: successFn,
                completeFn: () => { this.requestSent = false; },
            });
        }
    }
}


// TODO: handle http error cases
// TODO: do memory profile
class ServerCache {
    constructor() {
        this.store = new Store({
            user: {
                name: null,
            },

            notifications: [],

            latestRecords: [], // latest records with params
            searchRecords: [], // searched records view, with params
            recordCache: {}, // map of record IDs to records

            communities: [], // communities view, with params
            communityCache: {}, // map of community IDs to communities
            blockSchemaCache: {}, // map of block schema IDs to schemas
        });

        this.getters = {};

        this.getters.latestRecords = new Getter(
            apiUrls.records(),
            {start:0, stop:10, sortBy:'date', order:'descending'},
            (data) => this.store.setIn(['latestRecords'], fromJS(data.hits.hits)) );

        this.getters.searchRecords = new Getter(
            apiUrls.records(),
            {query:'', start:0, stop:10, sortBy:'date', order:'descending'},
            (data) => this.store.setIn(['searchRecords'], fromJS(data.hits.hits)) );

        this.getters.communities = new Getter(
            apiUrls.communities(), {},
            (data) => {
                const icommunities = fromJS(data.communities);
                this.store.setIn(['communities'], icommunities);
                this.store.updateIn(['communityCache'], (cache) => {
                    icommunities.forEach( (icommunity) => {
                        const id = icommunity.get('id');
                        let c = cache.get(id);
                        c = c ? c.merge(icommunity) : icommunity;
                        cache = cache.set(id, c);
                    });
                    return cache;
                });
            });

        this.getters.record = (recordID) => {
            const placeDataFn = (data) => {
                expect(recordID == data.id);
                const updater = (records) => records.set(data.id, fromJS(data));
                this.store.updateIn(['recordCache'], updater);
            };
            return new Getter(apiUrls.record(recordID), {}, placeDataFn);
        },

        // this.getters.community = (communityID) => {
        //     const placeDataFn = (data) => {
        //         expect(communityID == data.id);
        //         const icommunity = fromJS(data);
        //         const updater = (communities) => {
        //             let c = communities.get(communityID);
        //             c = c ? c.merge(icommunity) : icommunity;
        //             return communities.set(communityID, c);
        //         };
        //         this.store.updateIn(['communityCache'], updater);
        //     };
        //     return new Getter(apiUrls.community(communityID), {}, placeDataFn);
        // },

        this.getters.communitySchema = (communityID, version) => {
            const placeDataFn = (data) => {
                expect(communityID == data.community);
                const ischema = fromJS(data);
                const updater = (communities) => {
                    let c = communities.get(communityID) || fromJS({});
                    let s = c.get('schemas') || fromJS({});
                    s = s.set(version, ischema);
                    if (version === 'last') {
                        s = s.set(data.version, ischema);
                    }
                    c = c.set('schemas', s)
                    return communities.set(communityID, c);
                };
                this.store.updateIn(['communityCache'], updater);
            };
            return new Getter(apiUrls.communitySchema(communityID, version), {}, placeDataFn);
        },

        this.getters.blockSchema = (schemaID, version) => {
            const placeDataFn = (data) => {
                expect(schemaID == data.id);
                const ischema = fromJS(data);
                const updater = (schemas) => {
                    let s = schemas.get(schemaID) || fromJS({});
                    s = s.set(version, ischema);
                    if (version === 'last') {
                        s = s.set(data.version, ischema);
                    }
                    return schemas.set(schemaID, s);
                };
                this.store.updateIn(['blockSchemaCache'], updater);
            };
            return new Getter(apiUrls.schemas(schemaID, version), {}, placeDataFn);
        },

        this.posters = {};

        this.posters.records = new Poster(apiUrls.records());

    }

    getLatestRecords() {
        this.getters.latestRecords.autofetch();
        return this.store.getIn(['latestRecords']);
    }

    searchRecords({query, start, stop, sortBy, order}) {
        this.getters.searchRecords.fetch(query, start, stop, sortBy, order);
        return this.store.getIn(['searchRecords']);
    }

    getRecord(id) {
        this.getters.record(id).fetch();
        return this.store.getIn(['recordCache', id]);
    }

    getCommunities() {
        this.getters.communities.autofetch();
        return this.store.getIn(['communities']);
    }

    getCommunity(communityIDorName) {
        this.getters.communities.autofetch();
        const c = this.store.getIn(['communityCache', communityIDorName])
        return c ? c :
            this.store.findIn(['communities'], x => (x.get('name') == communityIDorName));
    }

    getCommunityBlockSchemaIDs(communityID, version) {
        const c = this.store.getIn(['communityCache', communityID]);
        if (!c || !c.get('schema')) {
            this.getters.communitySchema(communityID, version).fetch();
            return null;
        }
        const blockRefs = c.getIn(['schema', version,
            'json_schema', 'allOf', 1, 'properties', 'community_specific', 'properties']);
        // blockRefs must be : { key: {$ref:url} }

        if (!blockRefs) {
            return null;
        }
        const ret = {};
        blockRefs.entries().forEach( ([k,v]) => ret[k] = apiUrls.extractSchemaVersionFromUrl(v.get('$ref')) );
        return ret;
    }

    getBlockSchema(schemaID, version) {
        const s = this.store.getIn(['blockSchemaCache', schemaID, version]);
        if (!s) {
            this.getters.blockSchema(schemaID, version).fetch();
        }
        return s;
    }

    getUser() {
        // TODO: call server for user info
        return this.store.getIn(['user']);
    }

    createRecord(initialMetadata, successFn) {
        this.posters.records.post(initialMetadata, successFn);
    }

    updateRecord(id, metadata) {
        this.posters.record(id).post(metadata, successFn);
    }

    notifyAlert(text) {
        console.log('notif', text);
        this.store.updateIn(['notifications'], n => n.push({level:'alert', text: text}));
        // TODO: purge alerts
    }
};


export const serverCache = new ServerCache();

errorHandler.fn = function(text) {
    serverCache.notifyAlert(text);
}
