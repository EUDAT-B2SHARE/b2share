import {fromJS, OrderedMap, List} from 'immutable';
import {ajaxGet, ajaxPost, ajaxPut, ajaxPatch, ajaxDelete, errorHandler} from './ajax'
import {Store} from './store'
import {objEquals, expect, pairs} from './misc'
import {browserHistory} from 'react-router'
import _ from 'lodash';

const urlRoot = ""; // window.location.origin;

export const loginURL = `${urlRoot}/api/oauth/login/b2access`;

const apiUrls = {
    root()                            { return `${urlRoot}/api/` },

    user()                            { return `${urlRoot}/api/user` },
    userTokens()                      { return `${urlRoot}/api/user/tokens` },
    manageToken(id)                   { return `${urlRoot}/api/user/tokens/${id}` },

    users(queryString)                { return `${urlRoot}/api/users` + (queryString ? `?q=${queryString}` : ``) },
    userListWithRole(id)              { return `${urlRoot}/api/roles/${id}/users` },
    userWithRole(roleid, userid)      { return `${urlRoot}/api/roles/${roleid}/users/${userid}` },

    records()                         { return `${urlRoot}/api/records/` },
    recordsVersion(versionOf)         { return `${urlRoot}/api/records/?version_of=${versionOf}` },
    record(id)                        { return `${urlRoot}/api/records/${id}` },
    draft(id)                         { return `${urlRoot}/api/records/${id}/draft` },
    fileBucket(bucket, key)           { return `${urlRoot}/api/files/${bucket}/${key}` },

    abuse(id)                         { return `${urlRoot}/api/records/${id}/abuse` },
    accessrequests(id)                { return `${urlRoot}/api/records/${id}/accessrequests` },

    communities()                     { return `${urlRoot}/api/communities/` },
    communitySchema(cid, version)     { return `${urlRoot}/api/communities/${cid}/schemas/${version}` },

    schema(id, version)               { return `${urlRoot}/api/schemas/${id}/versions/${version}` },

    remotes(remote)                   { return `${urlRoot}/api/remotes` + (remote ? `/${remote}` : ``) },
    remotesJob()                      { return `${urlRoot}/api/remotes/jobs` },
    b2drop(path_)                     { return `${urlRoot}/api/remotes/b2drop` + (path_ ? `/${path_}` : ``) },

    languages()                       { return `${urlRoot}/suggest/languages.json` },
    disciplines()                     { return `${urlRoot}/suggest/disciplines.json` },

    statistics()                      { return `${urlRoot}/api/stats` },
    b2handle_pid_info(file_pid)       { return `${urlRoot}/api/handle/${file_pid}` },

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

    clear(){
        this.pool = {};
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
            ajaxPost({
                url: this.url,
                params: params,
                successFn: successFn,
                errorFn: errorFn,
                completeFn: () => { this.requestSent = false; },
            });
        }
    }

    put(params, successFn, errorFn) {
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxPut({
                url: this.url,
                params: params,
                successFn: successFn,
                errorFn: errorFn,
                completeFn: () => { this.requestSent = false; },
            });
        }
    }

    patch(params, successFn, errorFn) {
        if (!this.requestSent) {
            this.requestSent = true;
            ajaxPatch({
                url: this.url,
                params: params,
                successFn: successFn,
                errorFn: errorFn,
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

function processSchema(schema) {
    if (!schema) {
        return;
    }
    if (schema.allOf) {
        schema.allOf.forEach(processSchema);
    } else if (schema.anyOf) {
        schema.anyOf.forEach(processSchema);
    } else if (schema.oneOf) {
        schema.oneOf.forEach(processSchema);
    } else if (schema.type === 'object') {
        const required = schema.required || [];
        required.forEach(id => {
            if (schema.properties && schema.properties[id]) {
                schema.properties[id].isRequired = true;
            }
        });
        pairs(schema.properties).forEach(([id, p]) => processSchema(p));
    } else if (schema.type === 'array') {
        processSchema(schema.items);
    }
}

class ServerCache {
    constructor() {
        this.store = new Store({
            info: {
                version: "",
                site_function: "",
                training_site_link: "",
                b2access_registration_link: "",
                b2note_url: "",
                terms_of_use_link: "",
            },
            user: null,

            latestRecords: [], // latest records with params
            searchRecords: null, // searched records view, with params
            recordCache: {}, // map of record IDs to records
            draftCache: {}, // map of draft IDs to drafts

            communities: {}, // ordered map of community IDs to communities
            communitySchemas: {}, // map of community schema IDs to versions to schemas
            blockSchemas: {}, // map of block schema IDs to versions to schemas

            languages: null,
            disciplines: null,

            communityUsers: {}, // list of users belong to a specific community
            tokens: null, // list of user's tokens
        });

        this.store.setIn(['communities'], OrderedMap());

        this.getters = {};

        this.getters.tokens = new Getter(
            apiUrls.userTokens(), null,
            (data) => {
                var tokens = data.hits.hits.map(c =>  { return c })
                this.store.setIn(['tokens'], tokens);
            },
            (xhr) => this.store.setIn(['tokens'], new Error(xhr)) );

        this.getters.communityUsers = new Pool(roleid => new Getter(
        	apiUrls.userListWithRole(roleid), null,
            (users) => {
            	this.store.setIn(['communityUsers', roleid], fromJS(users.hits.hits));
            },
            null ));

        this.getters.latestRecords = new Getter(
            apiUrls.records(), {sort:"mostrecent"},
            (data) => this.store.setIn(['latestRecords'], fromJS(data.hits.hits)),
            (xhr) => this.store.setIn(['latestRecords'], new Error(xhr)) );

        this.getters.searchRecords = new Getter(
            apiUrls.records(), null,
            (data) => this.store.setIn(['searchRecords'], fromJS(data.hits)),
            (xhr) => this.store.setIn(['searchRecords'], new Error(xhr)) );

        this.getters.communities = new Getter(
            apiUrls.communities(), null,
            (data) => {
                let map = OrderedMap();
                data.hits.hits.forEach(c => { map = map.set(c.id, fromJS(c)); } );
                this.store.setIn(['communities'], map);
            },
            (xhr) => this.store.setIn(['communities'], new Error(xhr)) );

        this.getters.languages = new Getter(
            apiUrls.languages(), null,
            (data) => {
                const langs = data.languages.map(([id, name]) => ({id, name}));
                this.store.setIn(['languages'], langs);
            },
            (xhr) => this.store.setIn(['languages'], new Error(xhr)) );

        this.getters.disciplines = new Getter(
            apiUrls.disciplines(), null,
            (data) => {
                const transform = id => {
                    return {id, name:id};
                }
                const disciplines = data.disciplines ?
                    data.disciplines.map(transform) : null;
                this.store.setIn(['disciplines'], disciplines);
            },
            (xhr) => this.store.setIn(['disciplines'], new Error(xhr)) );

        function retrieveVersions(store, links, cachePath) {
            const versionsLink = links && links.versions;
            if (!versionsLink) {
                return
            }
            store.setIn(cachePath, null);
            ajaxGet({
                url: versionsLink,
                successFn: (data) => {
                    const v = data.versions.map((item, index) => {
                        item.index = index;
                        return item;
                    });
                    store.setIn(cachePath, fromJS(v).reverse());
                },
            });
        }

        function fetchFileStats(store, recordID, bucketID) {
            var data = {
                "fileDownloads": {
                    "stat": "bucket-file-download-total",
                    "params": {
                        "bucket_id": bucketID,
                    }
                }
            };
            ajaxPost({
                url: apiUrls.statistics(),
                params: data,
                successFn: response => {
                    const fileDownloads = response && response.fileDownloads;
                    if (!fileDownloads) {
                        return;
                    }
                    fileDownloads.buckets.forEach(kv => {
                        const index = store.getIn(['recordCache', recordID, 'files']).findIndex(f => f.get('key') == kv.key);
                        if (index >= 0) {
                            store.setIn(['recordCache', recordID, 'files', index, 'downloads'], kv.value);
                        } else {
                            console.error('cannot find file with key: ', kv.key);
                        }
                    });
                },
            });
        }

        this.getters.record = new Pool(recordID =>
            new Getter(apiUrls.record(recordID), null,
                (data) => {
                    if (data.files) { data.files = data.files.map(this.fixFile); }
                    this.store.setIn(['recordCache', recordID], fromJS(data));
                    if (data.files && data.files[0]) {
                        fetchFileStats(this.store, recordID, data.files[0].bucket);
                    } else if (!data.files && data.links.files) {
                        // private or embargoed record, needs manual file fetching
                        ajaxGet({
                            url: data.links.files,
                            successFn: (filedata) => {
                                const files = filedata.contents.map(this.fixFile);
                                for(var file_idx=0; file_idx<files.length; file_idx++){
                                    var current_file = files[file_idx];
                                    var external_pids = data.metadata.external_pids
                                    for(var ext_file_idx=0; ext_file_idx<data.metadata.external_pids.length; ext_file_idx++){
                                        var ext_file = data.metadata.external_pids[ext_file_idx];
                                        if(ext_file.key == current_file.key){
                                            current_file.b2safe = true;
                                            break;
                                        }
                                    }
                                }
                                this.store.setIn(['recordCache', recordID, 'files'], fromJS(files));
                                // do not fetch file statistiscs for private files
                                // (these files are missing the 'bucket' field)
                            },
                            errorFn: (xhr) => this.store.setIn(['recordCache', recordID, 'files'], new Error(xhr)),
                        });
                    }
                    retrieveVersions(this.store, data.links, ['recordCache', recordID, 'versions']);
                },
                (xhr) => this.store.setIn(['recordCache', recordID], new Error(xhr)) ));

        this.getters.draft = new Pool(draftID =>
            new Getter(apiUrls.draft(draftID), null,
                (data) => {
                    let files = this.store.getIn(['draftCache', draftID, 'files']);
                    if (data.files) {
                        files = fromJS(data.files.map(this.fixFile));
                    }
                    this.store.setIn(['draftCache', draftID], fromJS(data));
                    this.store.setIn(['draftCache', draftID, 'files'], files);
                    this.getters.fileBucket.get(draftID).fetch();
                    retrieveVersions(this.store, data.links, ['draftCache', draftID, 'versions']);
                },
                (xhr) => this.store.setIn(['draftCache', draftID], new Error(xhr)) ));

        this.getters.fileBucket = new Pool(draftID => {
            const fileBucketUrl = this.store.getIn(['draftCache', draftID, 'links', 'files']);
            if (!fileBucketUrl) {
                console.error("accessing fileBucketUrl before draft fetch", draftID);
                return null;
            }
            const placeDataFn = (data) => {
                var current_files = this.store.getIn(['draftCache', draftID, 'files']);
                this.store.setIn(['draftCache', draftID, 'files'], fromJS(data.contents.map(this.fixFile)));
            };
            const errorFn = (xhr) => this.store.setIn(['draftCache', draftID, 'files'], new Error(xhr));
            return new Getter(fileBucketUrl, null, placeDataFn, errorFn);
        });

        this.getters.communitySchema = new Pool( communityID =>
            new Pool ( version => {
                const placeDataFn = (data) => {
                    expect(communityID == data.community);
                    processSchema(data.json_schema);
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
                    processSchema(data.json_schema);
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
        this.posters.record = new Pool(recordID => new Poster(apiUrls.record(recordID)));
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
        this.posters.tokens = new Pool(tokenName => new Poster(apiUrls.userTokens()));
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

    // info and user can only be set once during a UI view; they will both be
    // refreshed when the page reloads (including when following hrefs)
    // user can be: null (uninitialized), {} (anonymous user), or {name,...}
    init(successFn) {
        ajaxGet({
            url: apiUrls.root(),
            successFn: (data, linkHeader, etag) => {
                this.store.setIn(['info'], fromJS(data));
                successFn(this.store.getIn(['info']));
            },
        });
        ajaxGet({
            url: apiUrls.user(),
            successFn: data => this.store.setIn(['user'], fromJS(data)),
        });
    }

    getInfo() {
        return this.store.getIn(['info']);
    }

    getUser() {
        return this.store.getIn(['user']);
    }

    getLatestRecords() {
        this.getters.latestRecords.autofetch();
        return this.store.getIn(['latestRecords']);
    }

    searchRecords({q, community, sort, page, size, drafts, submitted}) {
        if (community) {
            q = (q ? '(' + q + ') && ' : '') + ' community:' + community;
        }
        if (drafts) {
            const publication_state = submitted ? 'publication_state:submitted' : 'publication_state:draft';
            q = (q ? '(' + q + ') && ' : '') + publication_state;
        }
        (drafts == 1) ? this.getters.searchRecords.fetch({q, sort, page, size, drafts}) : this.getters.searchRecords.fetch({q, sort, page, size});
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
        return this.store.getIn(['recordCache', id]);
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
            blockRefs.entrySeq().forEach(
                ([id,ref]) => {
                    const ver = apiUrls.extractSchemaVersionFromUrl(ref.get('$ref'));
                    blockSchemas.push([id, this.getBlockSchema(id, ver)]);
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

    newUserToken(tokenName, successFn) {
        var param = {token_name:tokenName};
        this.posters.tokens.get().post(param, (token)=>{
            this.getters.tokens.forceFetch(null);
            successFn(token);
        });
    }

    getUserTokens(){
        this.getters.tokens.autofetch();
        return this.store.getIn(['tokens']);
    }

    removeUserToken(tokenID) {
        ajaxDelete({
            url: apiUrls.manageToken(tokenID),
            successFn: ()=>{
                notifications.success("Token is successfully deleted");
                this.getters.tokens.forceFetch(null);
            },
        });
    }

    getLanguages() {
        const langs = this.store.getIn(['languages']);
        if (!langs) {
            this.getters.languages.autofetch();
        }
        return langs;
    }

    getDisciplines() {
        const disciplines = this.store.getIn(['disciplines']);
        if (!disciplines) {
            this.getters.disciplines.autofetch();
        }
        return disciplines;
    }

    createRecord(initialMetadata, successFn) {
        this.posters.records.post(initialMetadata, successFn);
    }

    createRecordVersion(versionOfRecord, successFn) {
        ajaxPost({
            url: apiUrls.recordsVersion(versionOfRecord.get('id')),
            successFn: response => successFn(response.id),
            errorFn: (xhr) => {
                if (xhr.responseText) {
                    const json = JSON.parse(xhr.responseText);
                    if (json.goto_draft) {
                        notifications.info("A draft already exists for this record.")
                        successFn(json.goto_draft);
                    }
                } else {
                    onAjaxError(xhr);
                }
            }
        });
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

    updateDraft(id, metadata, successFn) {
        this.posters.draft.get(id).put(metadata, successFn);
    }

    patchDraft(id, patch, successFn, errorFn) {
        this.posters.draft.get(id).patch(patch, successFn, errorFn);
    }

    updateRecord(id, metadata, successFn) {
        this.posters.record.get(id).put(metadata, successFn);
    }

    patchRecord(id, patch, successFn, errorFn) {
        this.posters.record.get(id).patch(patch, successFn, errorFn);
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

    reportAbuse(id, data, successFn, errorFn) {
        ajaxPost({
            url: apiUrls.abuse(id),
            params: data,
            successFn: successFn,
            errorFn: errorFn,
        });
    }

    accessRequest(id, data, successFn, errorFn) {
        // TODO: This function will be changed later when we start using Zenodo_accessrequests module
        ajaxPost({
            url: apiUrls.accessrequests(id),
            params: data,
            successFn: successFn,
            errorFn: errorFn,
        });
    }


    // List users with a specific role
    getCommunityUsers(roleid){
        this.getters.communityUsers.get(roleid).autofetch();
        if(this.store.getIn(['communityUsers']).size > 0){
            return this.store.getIn(['communityUsers', roleid]);
        }
    	return {};
    }

    // Assign a role to the user by email
    registerUserRole(email, roleid, successFn, errorFn){
        ajaxGet({
            url: apiUrls.users(email),
            successFn: (user) => {
                    if(user.hits.hits[0]){
                        ajaxPut({
                            url: apiUrls.userWithRole( roleid , fromJS(user.hits.hits[0].id) ),
                            successFn: ()=> {
                                        this.getters.communityUsers.get(roleid).autofetch();
                                        ajaxGet({
                                            url: apiUrls.user(),
                                            successFn: data => this.store.setIn(['user'], fromJS(data)),
                                        });
                                        notifications.success("The new role was assigned to the user");
                            },
                            errorFn: () => {
                                    notifications.danger("User not found");
                                },
                        });
                    }
                    else{
                        notifications.danger("User not found");
                    }
                },
            errorFn: errorFn,
        });
    }

    // Unassign a role from a user
    deleteRoleOfUser(roleid, userid){
        ajaxDelete({
            url: apiUrls.userWithRole(roleid, userid),
            successFn: () => {
                this.getters.communityUsers.get(roleid).autofetch();
                ajaxGet({
                    url: apiUrls.user(),
                    successFn: data => this.store.setIn(['user'], fromJS(data)),
                });
                notifications.success("The role was removed");
            },
            errorFn: () => {
                notifications.danger("An error occured while trying to the role");
            },
        });
    }

    getB2HandlePidInfo(file_pid, successFn){
        ajaxGet({
            url: apiUrls.b2handle_pid_info(file_pid),
            successFn: response => {
                console.log(response);
                successFn(response);
            },
        });
    }

    addB2SafePid(file_pid, successFn){
        ajaxPatch({
            url: apiUrls.addB2SafeFile(file_pid),
            successFn: response => {
                console.log(response);
                successFn(response);
            },
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

    isNotEmpty() {
        const n = this.store.getIn(['notifications']);
        return n.get('danger').count() || n.get('warning').count() || n.get('info').count();
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

function encode(obj) {
    var a = [];
    for (var p in obj) {
        if (obj.hasOwnProperty(p)) {
            const x = obj[p];
            if (x !== undefined && x !== null && x !== '') {
                a.push(encodeURIComponent(p) + "=" + encodeURIComponent(x));
            }
        }
    }
    return a.join('&');
};

export const browser = {
    getRecordURL(recordId) {
        return `${window.location.origin}/records/${recordId}`;
    },

    gotoSearch({q, community, sort, page, size, drafts, submitted}) {
        const queryString = encode({q, community, sort, page, size, drafts, submitted});
        // trigger a route reload which will do the new search, see SearchRecordRoute
        browserHistory.push(`/records/?${queryString}`);
    },

    gotoRecord(recordId) {
        browserHistory.push(`/records/${recordId}`);
    },

    gotoEditRecord(recordId) {
        browserHistory.push(`/records/${recordId}/edit`);
    },
}
