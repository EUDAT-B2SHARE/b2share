import React from 'react/lib/ReactWithAddons';
import 'whatwg-fetch';
import { Badge } from 'react-bootstrap';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import { DateTimePicker, Multiselect, DropdownList, NumberPicker } from 'react-widgets';
import moment from 'moment';
import { timestamp } from '../data/ajax';
import { serverCache, notifications, browser, Error } from '../data/server';
import { keys, humanSize } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';
import { ImplodedList } from './common.jsx';
import { Wait, Err } from './waiting.jsx';
import { FileRecordHeader, FileRecordRow, PersistentIdentifier, copyToClipboard } from './editfiles.jsx';
import { Versions } from './versions.jsx';
import { getSchemaOrderedMajorAndMinorFields } from './schema.jsx';


const PT = React.PropTypes;


export const RecordRoute = React.createClass({
    getRecordOrDraft() {
        const { id } = this.props.params;
        let record = serverCache.getRecord(id);
        if (record instanceof Error && record.code == 404) {
            record = serverCache.getDraft(id);
        }
        return record;
    },

    render() {
        const record = this.getRecordOrDraft();
        const b2noteUrl = serverCache.getInfo().get('b2note_url');
        if (!record || !b2noteUrl) {
            return <Wait/>;
        }
        if (record instanceof Error) {
            return <Err err={record}/>;
        }
        const [rootSchema, blockSchemas] = serverCache.getRecordSchemas(record);
        const community = serverCache.getCommunity(record.getIn(['metadata', 'community']));

        return (
            <ReplaceAnimate>
                <Record record={record} community={community} rootSchema={rootSchema} blockSchemas={blockSchemas} b2noteUrl={b2noteUrl}/>
            </ReplaceAnimate>
        );
    }
});


const B2NoteWidget = React.createClass({
    mixins: [React.addons.PureRenderMixin],
    propTypes: {
        record: PT.object.isRequired,
        file: PT.object,
        showB2NoteWindow: PT.func.isRequired,
        //notes: PT.object.isRequired,
        b2noteUrl: PT.string.isRequired,
        smallButton: PT.bool
    },

    handleSubmit(e) {
        e.stopPropagation();
        this.props.showB2NoteWindow();
    },

    render() {
        var record = this.props.record.toJS ? this.props.record.toJS() : this.props.record;
        var notes = this.props.notes || [];
        var title = record.metadata.titles[0].title || "";

        const record_url = (record.links.self || "").replace('/api/records/', '/records/');

        if (this.props.file) {
            var file = this.props.file.toJS ? this.props.file.toJS() : this.props.file;
            var pid = file.ePIC_PID;
            var object_url = (file.url.indexOf('/api') == 0) ? (window.location.origin + file.url) : file.url;
            var source = file.key || "";

            // filter notes for given file
            notes = notes.filter(n => n.target.id == pid) || [];
        } else {
            var pid = record.metadata.ePIC_PID;
            var object_url = record.links.self || ""
            var source = '';
        }

        return (
            <form id="b2note_form_" action={this.props.b2noteUrl + '/widget'} method="post" target="b2note_iframe" style={this.props.style} onSubmit={this.handleSubmit}>
                <input type="hidden" name="recordurl_tofeed" value={record_url} className="field left" readOnly="readonly"/>
                <input type="hidden" name="pid_tofeed" value={pid} className="field left" readOnly="readonly"/>
                <input type="hidden" name="subject_tofeed" value={object_url} className="field left" readOnly="readonly"/>
                <input type="hidden" name="keywords_tofeed" value={record.metadata.keywords||""} className="field left" readOnly="readonly"/>
                <input type="hidden" name="pidName_tofeed" value={title} className="field left" readOnly="readonly"/>
                <input type="hidden" name="sourceName_tofeed" value={source} className="field left" readOnly="readonly"/>
                { this.props.smallButton
                    ? <button type="submit" className="btn btn-warning btn-xs" title="Click to annotate file using B2NOTE"><i className="fa fa-edit"/>&nbsp;<Badge>{ notes.length }</Badge></button>
                    : <button type="submit" className="btn btn-warning" title="Click to annotate record using B2NOTE"><i className="fa fa-edit"/>&nbsp;Annotate <Badge>{ notes.length }</Badge></button>
                }
            </form>
        );
    }
});


const Record = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    getInitialState() {
        var state = {
            showB2NoteWindow: false,
            record_notes: [],
            files_notes: [],
            b2noteUrl: this.props.b2noteUrl
        }

        return state;
    },

    getB2Notes(host, target, pids, sources) {
        var self = this;

        const pid_parameters = pids.join("&target-id[]=");
        const source_parameters = sources.join("&target-source[]=");

        // do not use inline ${var} here, it will unwrap the array
        var url = host + '/api/annotations?type[]=semantic&type[]=keyword&type[]=comment&target-id[]=' + pid_parameters + '&target-source[]=' + source_parameters;
        console.log('--- B2NOTE get:', timestamp(), `${pids}, ${sources}`);
        fetch(url)
          .then(function(response) {
            return response.json();
          }).then(function(json) {
            console.log('  > B2NOTE ret:', timestamp(), json);
            self.setState({
                [target]: json
            });
          }).catch(function(ex) {
            console.log('B2NOTE request failed: ' + ex)
          });
    },

    showB2NoteWindow() {
        this.setState({showB2NoteWindow: true})
    },

    componentDidMount() {
        // this is set async in parent
        if (this.state.b2noteUrl == "") {
            return;
        }

        window.addEventListener('message', this.catchB2NoteEvent);

        this.updateNotes();
    },

    updateNotes() {
        this.updateRecordNotes('record_notes');
        this.updateFileNotes('files_notes');
    },

    updateRecordNotes(target) {
        this.getB2Notes(this.props.b2noteUrl, target, [this.props.record.get('metadata').get('ePIC_PID')], [this.props.record.get('links').get('self')]);
    },

    updateFileNotes(target) {
        var bucket_id = this.props.record.get('links').get('files');
        this.getB2Notes(this.props.b2noteUrl, target, this.props.record.get('files').map(file => file.get('ePIC_PID')), this.props.record.get('files').map(file => bucket_id + '/' + file.get('key')));
    },

    catchB2NoteEvent(event) {
        if (event.origin != this.state.b2noteUrl) {
            return;
        }

        switch (typeof event.data || undefined) {
            case 'string':
                if (event.data != "B2NOTE loaded") {
                    console.log("B2NOTE init failed");
                }
                break;

            case 'object':
                switch (event.data.action || "") {
                    case 'create': case 'delete': case 'edit':
                        this.updateNotes();
                        break;
                }
                break;
        }
    },

    renderFixedFields(record, community) {
        function renderTitle(title, i) {
            return i === 0 ?
                <h2 key={i} className="name">{title.get('title')}</h2> :
                <h3 key={i} className="name">{title.get('title')}</h3>
        }
        function renderCreator(creator) {
            const c = creator.get('creator_name');
            return (
                <span>
                    <Link to={{pathname:'/records', query:{q:c}}} className="creator" key={c}>{c}</Link>
                </span>
            );
        }
        function renderDates(record) {
            const created = moment(record.get('created')).format('ll');
            const updated = moment(record.get('updated')).format('ll');
            return (
                <div className="dates">
                    <p>{created}</p>
                    { created != updated
                        ? <p>
                            <span>Last updated at </span>{updated}
                          </p>
                        : false }
                </div>
            );
        }
        function renderDescription(description, i) {
            const dt = description.get('description_type');
            const descriptionType = (dt == 'Other') ? 'Description' : dt;
            return (
                <p className="description" key={i}>
                    <span style={{fontWeight:'bold'}}>{descriptionType}: </span>
                    <ImplodedList data={description.get('description').split('\n')} delim='<br/>'/>
                </p>
            );
        }
        function renderSmallCommunity(community) {
            return !community ? false :
                (community instanceof Error) ? <Err err={community}/> :
                (
                    <div key={community.get('id')}>
                        <Link to={"/communities/"+community.get('name')}>
                            <div className="community-small passive" title={community.get('description')}>
                                <p className="name">{community.get('name')}</p>
                                <img className="logo" src={community.get('logo')}/>
                            </div>
                        </Link>
                    </div>
                );
        }

        function testget(map, key) {
            const x = map.get(key);
            return (x && x.count && x.count()) ? x : null;
        }

        const metadata = record.get('metadata') || Map();

        const descriptions = testget(metadata, 'descriptions');
        const disciplines = testget(metadata, 'disciplines');
        const keywords = testget(metadata, 'keywords');
        const creators = testget(metadata, 'creators');
        const pid = metadata.get('ePIC_PID');
        const doi = metadata.get('DOI');
        const state = metadata.get('publication_state');

        return (
            <div>
                <Versions isDraft={state == 'draft'} recordID={record.get('id')} versions={record.get('versions')}/>

                <div className="row">
                    <div className="col-sm-12">
                        { metadata.get('titles').map(renderTitle)}
                        { state != 'draft' ? false :
                        <h4 style={{color: '#CCC'}}>(draft preview)</h4>
                        }
                    </div>
                </div>

                <div className="row">
                    <div className="col-sm-8 col-md-10">
                        { creators ?
                            <p><span style={{color:'black'}}> by </span>
                            <ImplodedList data={creators.map(renderCreator)}/>;</p>
                            : false
                        }

                        { renderDates(record) }

                        { descriptions ? descriptions.map(renderDescription) : false }

                        { !disciplines ? false :
                            <p className="discipline">
                                <span style={{fontWeight:'bold'}}>Disciplines: </span>
                                <ImplodedList data={disciplines.map(k => <Link to={{pathname:'/records', query:{q:k}}} key={k}>{k}</Link>)}/>;
                            </p>
                        }

                        { !keywords ? false :
                            <p className="keywords">
                                <span style={{fontWeight:'bold'}}>Keywords: </span>
                                <ImplodedList data={keywords.map(k => <Link to={{pathname:'/records', query:{q:k}}} key={k}>{k}</Link>)}/>;
                            </p>
                        }

                        {doi ?
                            <p className="pid">
                                <span>DOI: </span>
                                <PersistentIdentifier pid={doi} doi={true}/>
                            </p> : false
                        }
                        {pid ?
                            <p className="pid">
                                <span>PID: </span>
                                <PersistentIdentifier pid={pid} />
                            </p> : false
                        }
                    </div>

                    <div className="col-sm-4 col-md-2">
                        { renderSmallCommunity(community) }
                    </div>
                </div>
            </div>
        );
    },

    fixedFields: {
        'community': true, 'titles': true, 'descriptions': true,
        'creators': true, 'keywords': true, 'disciplines': true, 'publication_state': true,
    },

    renderFileList(files, b2noteUrl, showDownloads) {
        const openAccess = this.props.record.getIn(['metadata', 'open_access']);
        const showAccessRequest = (!openAccess && !isRecordOwner(this.props.record));

        let fileComponent = false;
        if (!(files && files.count && files.count())) {
            fileComponent = <div>No files available.</div>;
        } else {
            const fileRecordRowFn = f => {
                let b2noteWidget = false;
                if (b2noteUrl) {
                    b2noteWidget = <B2NoteWidget file={f} record={this.props.record} notes={this.state.files_notes} showB2NoteWindow={this.showB2NoteWindow} b2noteUrl={b2noteUrl} smallButton={true}/>;
                }
                return <FileRecordRow key={f.get('key')} file={f} b2noteWidget={b2noteWidget} showDownloads={showDownloads} />
            }
            fileComponent =
                <div className='fileList'>
                    <FileRecordHeader/>
                    { files.map(fileRecordRowFn) }
                </div>;
        }
        return (
            <div className="well">
                <div className="row">
                    <h3 className="col-sm-9">
                        { 'Files' }
                    </h3>
                </div>
                { fileComponent }
                { showAccessRequest ?
                    <Link to={`/records/${this.props.record.get('id')}/accessrequest`}>
                        Request data access
                    </Link> : false }
            </div>
        );
    },

    renderField(id, schema, value, vtype=null) {
        function renderScalar(schema, value) {
            const type = schema.get('type');
            if (type === 'string' && schema.get('format') === 'date-time') {
                value = moment(value).format("LLLL");
            } else if (type === 'boolean') {
                const markClass = "glyphicon glyphicon-" + (value ? "ok":"remove");
                return (
                    <label>
                        <span className="metadata-boolean">{value ? "True":"False"}</span>
                        <span className={markClass} aria-hidden="true"/>
                    </label>
                );
            } else if (vtype) {
                switch (vtype) {
                    case 'DOI':
                        return <Link to={"https://dx.doi.org/" + value} target="_blank">{value}</Link>
                    case 'Handle':
                        return <Link to={"https://hdl.handle.net/" + value} target="_blank">{value}</Link>
                    case 'URL':
                        return <Link to={value} target="_blank">{value}</Link>
                }
            }

            return value;
        }

        if (value === undefined || value === null) {
            return false;
        }
        //console.log(id, value);
        const type = schema.get('type');
        const title = schema.get('title');
        let inner = null;

        if (type === 'array') {
            inner = (
                <ul className="list-unstyled">
                    { value.map((v,i) => this.renderField(`#${i}`, schema.get('items'), v)) }
                </ul>
            );
        } else if (type === 'object') {
            // determine if object parent has '_type' element that is a string
            const mainid = schema.get('properties').keys().next().value;
            const maintype = schema.get('properties').has(mainid + "_type") ? schema.get('properties').get(mainid + "_type") : null;
            const vtype = (maintype && maintype.get('type') == 'string') ? value.get(mainid + "_type") : null;

            inner = (
                <ul className="list-unstyled">
                    { schema.get('properties').entrySeq().map(
                        ([pid, pschema]) => this.renderField(pid, pschema, value.get(pid), pid == mainid ? vtype : null)) }
                </ul>
            );
        } else {
            inner = <span key={id}>{renderScalar(schema, value)}</span>
        }

        return (
            <li key={id} className="row">
                { !title ? false :
                    <div className="col-sm-4">
                        <label>{title}</label>
                    </div>
                }
                <div className={
                    (title ? "col-sm-8" : "col-sm-12") + " " + (type === 'object' ? "metadata-object" : "metadata")}>
                     {inner} </div>
            </li>
        );
    },


    renderFieldBlock(schemaID, schema, excludeFields) {
        if (!schema) {
            return <Wait key={schemaID}/>;
        }

        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(schema);
        const metadata_block = this.props.record.get('metadata');
        const metadata = !schemaID ? metadata_block : metadata_block.getIn(['community_specific', schemaID]);

        function renderBigField(excludeFields, [pid, pschema], i) {
            if (excludeFields[pid]) {
                return false;
            }
            const f = this.renderField(pid, pschema, metadata.get(pid));
            if (!f) {
                return false;
            }

            return <div className="metadata-field" key={pid}> {f} </div>;
        }
        const majorFields = majors.entrySeq().map(renderBigField.bind(this, excludeFields));
        const minorFields = minors.entrySeq().map(renderBigField.bind(this, excludeFields));

        return (
            <div key={schemaID||"_"} className={"well " + (schemaID ? "block" : "")}>
                <div className="row">
                    <h3 className="col-sm-9">
                        { schemaID ? schema.get('title') : 'Basic metadata' }
                    </h3>
                    { !schemaID ? false :
                        <span style={{float: 'right'}}>
                            <a className="btn btn-xs btn-default" onClick={() => copyToClipboard(schemaID)}
                               title="Copy community block schema identifier used for this record">
                                <i className="fa fa-clipboard"/>
                            </a>
                        </span>
                    }
                </div>
                <div className="row">
                    <ul className="col-sm-12 list-unstyled">
                        { majorFields }
                    </ul>
                </div>
                <div className="row">
                    <ul className="col-sm-12 list-unstyled">
                        { minorFields }
                    </ul>
                </div>
            </div>
        );
    },

    render() {
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas;
        const record = this.props.record;
        const b2noteUrl = this.props.b2noteUrl;
        if (!record || !rootSchema || !b2noteUrl) {
            return <Wait/>;
        }

        const recordID = record.get('id');
        const files = record.get('files') || record.getIn(['metadata', '_files']);
        const isLatestVersion = !record.has('versions') || recordID == record.getIn(['versions', 0, 'id']);
        function onNewVersion (e) {
            e.preventDefault();
            serverCache.createRecordVersion(record, newRecordID => browser.gotoEditRecord(newRecordID));
        }
        const state = record.get('metadata').get('publication_state');

        return (
            <div className="container-fluid">
                <div className="large-record bottom-line">
                    <div className="row metadata-main">
                        <div className="col-lg-12">
                            {this.renderFixedFields(record, this.props.community)}
                        </div>
                        {this.props.b2noteUrl ?
                            <div className={"well b2note " + (!this.state.showB2NoteWindow ? "hidden" : "")}>
                                <button type="button" className="close" aria-label="Close" onClick={e => this.setState({showB2NoteWindow:false})}>
                                    <span aria-hidden="true">&times;</span>
                                </button>
                                <iframe id="b2note_iframe" name="b2note_iframe"
                                    src={`data:text/html, <style type="text/css">
                                        .center-div {
                                            width: 100%;
                                            height: 100%;
                                            position: absolute;
                                            margin: auto;
                                            top: 0;
                                            right: 0;
                                            bottom: 0;
                                            left: 0;
                                        }
                                        .loader {
                                            position: absolute;
                                            margin: auto;
                                            top: 0;
                                            right: 0;
                                            bottom: 0;
                                            left: 0;
                                            border: 16px solid %23e3e3e3; /* Light grey */
                                            border-top: 16px solid %233498db; /* Blue */
                                            border-radius: 50%;
                                            width: 60px;
                                            height: 60px;
                                            animation: spin 2s linear infinite;
                                        }
                                        /* Safari */
                                        @-webkit-keyframes spin {
                                            0% { -webkit-transform: rotate(0deg); }
                                            100% { -webkit-transform: rotate(360deg); }
                                        }
                                        @keyframes spin {
                                            0% { transform: rotate(0deg); }
                                            100% { transform: rotate(360deg); }
                                        }
                                        </style>
                                        <div class="center-div"><div class="loader"></div></div>`
                                    }
                                    className="frame"/>
                            </div> : false
                        }
                    </div>
                    <div className="row">
                        <div className="col-lg-6">
                            { this.renderFileList(files, this.props.b2noteUrl, true) }
                        </div>

                        <div className="col-lg-6">
                            { this.renderFieldBlock(null, rootSchema, this.fixedFields) }

                            { !blockSchemas ? false :
                                blockSchemas.map(([id, blockSchema]) =>
                                    this.renderFieldBlock(id, (blockSchema||Map()).get('json_schema'), {})) }
                        </div>
                    </div>

                    <div className="row bottom-buttons">
                        <div className="col-lg-12">
                            <div>
                                <Link to={`/records/${recordID}/abuse`} className="btn btn-default abuse"><i className="glyphicon glyphicon-exclamation-sign"/> Report Abuse</Link>
                                { this.props.b2noteUrl ?
                                    <B2NoteWidget record={record} showB2NoteWindow={this.showB2NoteWindow} notes={this.state.record_notes} b2noteUrl={this.props.b2noteUrl} b2noteCount={this.state.record_notes || {}} style={{display: 'inline-block', margin: '0px 7px'}}/>
                                    : false
                                }
                                { canEditRecord(record) ?
                                    <Link to={`/records/${recordID}/edit`} className="btn btn-warning" style={{margin: '0 0.5em'}}><i className="fa fa-pencil"/>&nbsp;
                                        { state == 'draft' ? 'Edit draft metadata' : 'Edit metadata' }</Link>
                                    : false
                                }
                                { isRecordOwner(record) && isLatestVersion ?
                                    <a href='#' onClick={onNewVersion} className="btn btn-warning"><i className="fa fa-plus"/>&nbsp;
                                        Create New Version</a>
                                    : false
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


function canEditRecord(record) {
    if (isRecordOwner(record)) {
        return true;
    }
    if (isCommunityAdmin(record.getIn(['metadata', 'community']))) {
        return true;
    }
    return false;
}

function isRecordOwner(record) {
    if (!serverCache.getUser()) {
        return false;
    }
    const userId = serverCache.getUser().get('id');
    if (userId === undefined || userId === null) {
        return false;
    }
    return record.getIn(['metadata', 'owners']).indexOf(userId) >= 0;
}

export function isCommunityAdmin(communityId) {
    if (!serverCache.getUser()) {
        return false;
    }
    const roles = serverCache.getUser().get('roles');
    if (!roles) {
        return false;
    }
    const community = serverCache.getCommunity(communityId);
    if (community && community.hasIn(['roles', 'admin'])) {
        const communityAdminRoleId = community.getIn(['roles', 'admin', 'id']);
        return roles.find(r => r.get('id') === communityAdminRoleId);
    }
    return false
}
