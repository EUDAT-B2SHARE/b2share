import {fromJS, OrderedMap, List} from 'immutable';
import {ajaxGet, ajaxPost, ajaxPut, ajaxPatch, ajaxDelete, errorHandler} from './ajax'
import {Store} from './store'
import {objEquals, expect} from './misc'

const urlRoot = ""; // window.location.origin;

export const loginURL = `${urlRoot}/api/oauth/login/b2access`;

const apiUrls = {
    users()                           { return `${urlRoot}/api/users/` },
    userLogin()                       { return `${urlRoot}/api/users/login/` },

    records()                         { return `${urlRoot}/api/records/` },
    record(id)                        { return `${urlRoot}/api/records/${id}` },
    draft(id)                         { return `${urlRoot}/api/records/${id}/draft` },
    fileBucket(bucket, key)           { return `${urlRoot}/api/files/${bucket}/${key}` },

    communities()                     { return `${urlRoot}/api/communities/` },
    community(id)                     { return `${urlRoot}/api/communities/${id}` },
    communitySchema(cid, version)     { return `${urlRoot}/api/communities/${cid}/schemas/${version}` },

    schema(id, version)               { return `${urlRoot}/api/schemas/${id}/versions/${version}` },

    user()                            { return `${urlRoot}/api/users/current` },
    userTokens()                      { return `${urlRoot}/api/users/current/tokens` },

    remotes(remote)                   { return `${urlRoot}/api/remotes` + (remote ? `/${remote}` : ``) },
    remotesJob()                      { return `${urlRoot}/api/remotes/jobs` },
    b2drop(path_)                     { return `${urlRoot}/api/remotes/b2drop` + (path_ ? `/${path_}` : ``) },

    languages()                       { return `${urlRoot}/languages.json` },

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
    constructor(url, params, fetchSuccessFn, fetchErrorFn) {
        this.url = url;
        this.params = params;
        this.etag = null;
        this.timer = new Timer(GETTER_HYSTERESIS_INTERVAL_MS);
        this.fetchSuccessFn = fetchSuccessFn;
        this.fetchErrorFn = fetchErrorFn;
    }

    autofetch() {
        this.fetch(this.params);
    }

    fetch(params) {
        if (this.timer.ticking() && this.equals(params, this.params)) {
            return;
        }
        this.forceFetch(params);
    }

    forceFetch(params) {
        this.timer.restart();
        this.params = params;
        ajaxGet({
            url: this.url,
            params: this.params,
            etag: this.etag,
            successFn: (data, linkHeader, etag) => {
                this.etag = etag;
                this.fetchSuccessFn(data, linkHeader);
            },
            errorFn: this.fetchErrorFn,
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

    put(params, successFn) {
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxPut({
                url: this.url,
                params: params,
                successFn: successFn,
                completeFn: () => { this.requestSent = false; },
            });
        }
    }

    patch(params, successFn) {
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxPatch({
                url: this.url,
                params: params,
                successFn: successFn,
                completeFn: () => { this.requestSent = false; },
            });
        }
    }
}

class FilePoster {
    constructor(url) {
        this.url = url;
        this.xhr = null;
    }

    put(file, progressFn) {
        if (this.xhr) {
            console.error("already uploading file");
            return ;
        }

        const xhr = new XMLHttpRequest();
        this.xhr = xhr;
        xhr.upload.addEventListener("progress", (e) => {
            progressFn('uploading', 1 + (e.loaded / e.total * 99));
        }, false);

        xhr.open("PUT", this.url);
        xhr.onreadystatechange = () => {
            if (XMLHttpRequest.DONE !== xhr.readyState) {
                return;
            }
            this.xhr = null;
            if (400 <= xhr.status) {
                progressFn('error', xhr);
            } else {
                progressFn('done', xhr);
                this.xhr = null;
            }
        };

        progressFn('uploading', 0);
        xhr.send(file);
        return xhr;
    }

    delete(successFn) {
        if (this.xhr && this.xhr.abort) {
            this.xhr.abort();
        }
        const completeFn = () => {this.xhr = null};
        ajaxDelete({
            url: this.url,
            successFn: (data) => { completeFn(); successFn(data); },
            completeFn: completeFn,
        });
    }
}


class ServerCache {
    constructor() {
        this.store = new Store({

            latestRecords: [], // latest records with params
            searchRecords: [], // searched records view, with params
            recordCache: {}, // map of record IDs to records
            draftCache: {}, // map of draft IDs to drafts

            communities: {}, // ordered map of community IDs to communities
            communitySchemas: {}, // map of community schema IDs to versions to schemas
            blockSchemas: {}, // map of block schema IDs to versions to schemas

            languages: null,
        });

        this.store.setIn(['communities'], OrderedMap());

        this.getters = {};

        this.getters.latestRecords = new Getter(
            apiUrls.records(), {sort:"mostrecent"},
            (data) => this.store.setIn(['latestRecords'], fromJS(data.hits.hits)),
            (xhr) => this.store.setIn(['latestRecords'], new Error(xhr)) );

        this.getters.searchRecords = new Getter(
            apiUrls.records(), null,
            (data) => this.store.setIn(['searchRecords'], fromJS(data.hits.hits)),
            (xhr) => this.store.setIn(['searchRecords'], new Error(xhr)) );

        this.getters.communities = new Getter(
            apiUrls.communities(), null,
            (data) => {
                let map = OrderedMap();
                data.hits.hits.forEach(c => { map = map.set(c.id, fromJS(c)); } );
                this.store.setIn(['communities'], map);
            },
            (xhr) => this.store.setIn(['communities'], new Error(xhr)) );

        this.getters.record = new Pool(recordID =>
            new Getter(apiUrls.record(recordID), null,
                (data) => {
                    if (data.files) { data.files = data.files.map(this.fixFile); }
                    return this.store.setIn(['recordCache', recordID], fromJS(data));
                },
                (xhr) => this.store.setIn(['recordCache', recordID], new Error(xhr)) ));

        this.getters.draft = new Pool(draftID =>
            new Getter(apiUrls.draft(draftID), null,
                (data) => {
                    if (data.files) { data.files = data.files.map(this.fixFile); }
                    return this.store.setIn(['draftCache', draftID], fromJS(data));
                },
                (xhr) => this.store.setIn(['draftCache', draftID], new Error(xhr)) ));

        this.getters.fileBucket = new Pool(draftID => {
            const fileBucketUrl = this.store.getIn(['draftCache', draftID, 'links', 'files']);
            if (!fileBucketUrl) {
                console.error("accessing fileBucketUrl before draft fetch", draftID);
                return null;
            }
            const placeDataFn = data =>
                this.store.setIn(['draftCache', draftID, 'files'], fromJS(data.contents.map(this.fixFile)));
            const errorFn = (xhr) => this.store.setIn(['draftCache', draftID, 'files'], new Error(xhr));
            return new Getter(fileBucketUrl, null, placeDataFn, errorFn);
        });

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
                const errorFn = (xhr) => this.store.setIn(['communitySchemas', communityID, version], new Error(xhr));
                return new Getter(apiUrls.communitySchema(communityID, version), null, placeDataFn, errorFn);
            })
        );

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
                const errorFn = (xhr) => this.store.setIn(['blockSchemas', schemaID, version], new Error(xhr));
                return new Getter(apiUrls.schema(schemaID, version), null, placeDataFn, errorFn);
            })
        );

        this.posters = {};
        this.posters.records = new Poster(apiUrls.records());
        this.posters.draft = new Pool(draftID => new Poster(apiUrls.draft(draftID)));
        this.posters.files = new Pool(draftID =>
            new Pool(fileName => {
                const fileBucketUrl = this.store.getIn(['draftCache', draftID, 'links', 'files']);
                if (!fileBucketUrl) {
                    console.error("accessing fileBucketUrl poster before draft fetch", draftID);
                    return null;
                }
                return new FilePoster(fileBucketUrl + '/' + fileName);
            })
        );
    }

    fixFile(file) {
        if (!file.url) {
            if (file.links && file.links.self) {
                file.url = file.links.self;
            } else if (file.key && file.bucket) {
                file.url = apiUrls.fileBucket(file.bucket, file.key);
            }
        }
        return file;
    }


    getLatestRecords() {
        this.getters.latestRecords.autofetch();
        return this.store.getIn(['latestRecords']);
    }

    searchRecords({q, sort, page, size, community}) {
        const params = {};
        if (community) {
            q = (q || "") + ' community:' + community;
        }
        this.getters.searchRecords.fetch({q, sort, page, size});
        return this.store.getIn(['searchRecords']);
    }

    getCommunities() {
        this.getters.communities.autofetch();
        const communities = this.store.getIn(['communities']);
        if (!communities || communities instanceof Error) {
            return communities
        }
        return List(communities.valueSeq());
    }

    getCommunity(communityIDorName) {
        this.getters.communities.autofetch();
        const communities = this.store.getIn(['communities']);
        if (!communities) {
            return null;
        }
        if (communities instanceof Error) {
            return communities;
        }
        let c = communities.get(communityIDorName);
        if (!c) {
            c = communities.valueSeq().find(x => x.get('name') == communityIDorName);
        }
        return c;
    }

    getRecord(id) {
        this.getters.record.get(id).fetch();
        this.fetchRecordFiles(id);
        return this.store.getIn(['recordCache', id]);
    }

    fetchRecordFiles(id) {
        const record = this.store.getIn(['recordCache', id]);
        if (!record || !record.get) {
            return null;
        }
        const files = record.get('files');
        if (files) {
            return files;
        }
        const url = record.getIn(['links', 'files']);
        if (url) {
            ajaxGet({
                url: url,
                successFn: (data) =>
                    this.store.setIn(['recordCache', id, 'files'], fromJS(data.contents.map(this.fixFile))),
                errorFn: (xhr) => this.store.setIn(['recordCache', id, 'files'], new Error(xhr)),
            });
        }
    }

    getDraft(id) {
        this.getters.draft.get(id).fetch();
        return this.store.getIn(['draftCache', id]);
    }

    getDraftFiles(draftID, useForce) {
        if (!draftID) {
            return [];
        }
        if (useForce) {
            this.getters.fileBucket.get(draftID).forceFetch();
        } else {
            this.getters.fileBucket.get(draftID).fetch();
        }
        return this.store.getIn(['draftCache', draftID, 'files']);
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
        if (cs instanceof Error) {
            return [cs, null]
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
        const user = this.store.getIn(['user']);
        if (user) {
            return user;
        }
        ajaxGet({
            url: apiUrls.user(),
            successFn: (data) => this.store.setIn(['user'], fromJS(data)),
            errorFn: (xhr) => this.store.setIn(['user'], new Error(xhr)),
        });
    }

    getUserTokens(successFn) {
        ajaxGet({
            url: apiUrls.userTokens(),
            successFn: (data) => successFn(data.hits.hits),
        });
    }

    newUserToken(tokenName, successFn) {
        ajaxPost({
            params: {token_name:tokenName},
            url: apiUrls.userTokens(),
            successFn: successFn,
        });
    }

    getLanguages() {
        const langs = this.store.getIn(['languages']);
        if (!langs) {
            ajaxGet({
                url: apiUrls.languages(),
                successFn: (data) => {
                    const langs = data.languages.map(([id, name]) => ({id, name}));
                    console.log('got languages: ', langs.length);
                    this.store.setIn(['languages'], langs);
                },
                errorFn: (xhr) => this.store.setIn(['languages'], new Error(xhr)),
            });
        }
        return langs;
    }

    createRecord(initialMetadata, successFn) {
        this.posters.records.post(initialMetadata, successFn);
    }

    putFile(draft, fileObject, progressFn) {
        const progFn = (status, param) => {
            if (status === 'done') {
                this.getDraftFiles(draft.get('id'), true); // force fetch files
            }
            progressFn(status, param)
        };
        return this.posters.files.get(draft.get('id')).get(fileObject.name).put(fileObject, progFn);
    }

    deleteFile(draft, fileKey) {
        return this.posters.files.get(draft.get('id')).get(fileKey).delete(() => {
            this.getDraftFiles(draft.get('id'), true); // force fetch files
        });
    }

    updateRecord(id, metadata, successFn) {
        this.posters.draft.get(id).put(metadata, successFn);
    }

    patchRecord(id, patch, successFn) {
        this.posters.draft.get(id).patch(patch, successFn);
    }

    b2dropInit(username, password, successFn, errorFn) {
        ajaxPut({
            url: apiUrls.b2drop(),
            params: { username, password },
            successFn,
            errorFn
        });
    }

    b2dropList(path, successFn, errorFn) {
        ajaxGet({
            url: apiUrls.b2drop(path),
            successFn,
            errorFn,
        });
    }

    b2dropCopyFile(draft, b2dropPath, fileName, progressFn) {
        let fileBucketUrl = draft.getIn(['links', 'files']) ||
            this.store.getIn(['draftCache', draft.get('id'), 'links', 'files']);
        if (!fileBucketUrl) {
            console.error("cannot find fileBucketUrl", draft.toJS());
            return null;
        }
        const successFn = x => {
            progressFn('done', x);
            this.getDraftFiles(draft.get('id'), true); // force fetch files
        }
        const errorFn = x => progressFn('error', x);
        progressFn('uploading', 1);
        ajaxPost({
            url: apiUrls.remotesJob(),
            params: {
                source_remote_url: apiUrls.b2drop(b2dropPath),
                destination_file_url: fileBucketUrl + '/' + fileName,
            },
            successFn,
            errorFn,
        });
    }
};


class Notifications {
    constructor() {
        this.store = new Store({
            notifications: {}, // alert level -> { alert text -> x }
        });
        this.emptyState = OrderedMap([
            ['danger', OrderedMap()], ['warning', OrderedMap()], ['info', OrderedMap()]
        ]);
        this.store.setIn(['notifications'], this.emptyState);
    }

    getAll() {
        return this.store.getIn(['notifications']);
    }

    clearAll() {
        this.store.setIn(['notifications'], this.emptyState);
    }

    notify(level, text) {
        this.store.setIn(['notifications', level, text], Date.now());
    }

    danger(text) {
        this.notify('danger', text);
    }

    warning(text) {
        this.notify('warning', text);
    }

    success(text) {
        this.notify('success', text);
    }

    info(text) {
        this.notify('info', text);
    }
};


export class Error {
    constructor({status, statusText, responseText}) {
        this.code = status;
        this.text = statusText;
        this.data = null;
        try {
            this.data = JSON.parse(responseText); }
        catch (err) {
            this.data = responseText;
        };
    }
}

errorHandler.fn = function(text) {
    notifications.danger(text);
}

export const serverCache = new ServerCache();
export const notifications = new Notifications();
