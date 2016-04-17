import {fromJS, OrderedMap, List} from 'immutable';
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

    extractCommunitySchemaInfoFromUrl(communitySchemaURL) {
        if (!communitySchemaURL) {
            return [];
        }
        const m = communitySchemaURL.match(/.*\/api\/communities\/([^\/]+)\/schemas\/(\d+).*/);
        if (m) {
            return [m[1], m[2]];
        }
        const mlast = communitySchemaURL.match(/.*\/api\/communities\/([^\/]+)\/schemas\/last.*/);
        if (mlast) {
            return [mlast[1], 'last'];
        }
        return [];
    },

    extractSchemaVersionFromUrl(schemaURL) {
        if (!schemaURL) {
            return null;
        }
        const m = schemaURL.match(/.*\/versions\/(\d+).*/);
        if (m && m[1]) {
            return m[1]
        }
        if (/\/versions\/last.*/.match(schemaURL)) {
            return 'last';
        }
        return null;
    },
};


const GETTER_HYSTERESIS_INTERVAL_MS = 500; // half a second


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
        if (this.timer.ticking() && this.equals(params, this.params)) {
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

    equals(o1, o2) {
        if ((o1 === null || o1 === undefined) && (o2 === null || o2 === undefined)) {
            return true;
        }
        return objEquals(o1, o2)
    }
}


class Pool {
    constructor(newFn) {
        this.newFn = newFn;
        this.pool = {};
    }
    get(x) {
        let r = this.pool[x];
        if (!r) {
            r = this.newFn(x);
            this.pool[x] = r;
        }
        return r;
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

            communities: {}, // ordered map of community IDs to communities
            communitySchemas: {}, // map of community schema IDs to versions to schemas
            blockSchemas: {}, // map of block schema IDs to versions to schemas
        });
        this.store.setIn(['communities'], OrderedMap());

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
            apiUrls.communities(), null,
            (data) => {
                let map = OrderedMap();
                data.communities.forEach(c => { map = map.set(c.id, fromJS(c)); } );
                this.store.setIn(['communities'], map);
            });

        this.getters.record = new Pool(recordID => {
            const placeDataFn = (data) => {
                expect(recordID == data.id);
                const updater = (records) => records.set(data.id, fromJS(data));
                this.store.updateIn(['recordCache'], updater);
            };
            return new Getter(apiUrls.record(recordID), null, placeDataFn);
        }),

        this.getters.communitySchema = new Pool( communityID =>
            new Pool ( version => {
                const placeDataFn = (data) => {
                    expect(communityID == data.community);
                    const ischema = fromJS(data);
                    const updater = (schemas) => {
                        let s = schemas.get(communityID) || fromJS({});
                        s = s.set(version, ischema);
                        if (version === 'last') {
                            s = s.set(data.version, ischema);
                        }
                        return schemas.set(communityID, s);
                    };
                    this.store.updateIn(['communitySchemas'], updater);
                };
                return new Getter(apiUrls.communitySchema(communityID, version), null, placeDataFn);
            })
        ),

        this.getters.blockSchema = new Pool(schemaID =>
            new Pool(version => {
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
                    this.store.updateIn(['blockSchemas'], updater);
                };
                return new Getter(apiUrls.schema(schemaID, version), null, placeDataFn);
            })
        ),

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

    getCommunities() {
        this.getters.communities.autofetch();
        const communities = this.store.getIn(['communities']);
        return communities ? List(communities.valueSeq()) : communities;
    }

    getCommunity(communityIDorName) {
        this.getters.communities.autofetch();
        const communities = this.store.getIn(['communities']);
        if (!communities) {
            return null;
        }
        const c = communities.get(communityIDorName);
        return c ? c : communities.valueSeq().find(x => x.get('name') == communityIDorName);
    }

    getRecord(id) {
        this.getters.record.get(id).fetch();
        return this.store.getIn(['recordCache', id]);
    }

    getBlockSchema(schemaID, version) {
        const s = this.store.getIn(['blockSchemas', schemaID, version]);
        if (!s) {
            this.getters.blockSchema.get(schemaID).get(version).fetch();
        }
        return s;
    }

    getCommunitySchemas(communityID, version) {
        const cs = this.store.getIn(['communitySchemas', communityID, version]);
        if (!cs) {
            this.getters.communitySchema.get(communityID).get(version).fetch();
            return [];
        }
        const allOf = cs.getIn(['json_schema', 'allOf']);
        if (!allOf) {
            return [];
        }
        const rootSchema = allOf.get(0);
        let blockSchemas = [];
        const blockRefs = allOf.getIn([1, 'properties', 'community_specific', 'properties']);
        // blockRefs must be : { id: {$ref:url} }

        if (blockRefs) {
            blockSchemas = blockRefs.entrySeq().map(
                ([id,ref]) => {
                    const ver = apiUrls.extractSchemaVersionFromUrl(ref.get('$ref'));
                    return [id, this.getBlockSchema(id, ver)];
                }
            );
        }
        return [rootSchema, blockSchemas];
    }

    getRecordSchemas(record) {
        if (!record) {
            return [];
        }
        const [communityID, ver] = apiUrls.extractCommunitySchemaInfoFromUrl(record.getIn(['metadata', '$schema']));
        return this.getCommunitySchemas(communityID, ver);
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
