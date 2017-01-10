import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import moment from 'moment';
import { serverCache, Error } from '../data/server';
import { keys, humanSize } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';
import { Wait, Err } from './waiting.jsx';
import { FileRecordHeader, FileRecordRow, PersistentIdentifier } from './editfiles.jsx';
import { getSchemaOrderedMajorAndMinorFields } from './schema.jsx';


export const RecordRoute = React.createClass({
    render() {
        const { id } = this.props.params;
        const record = serverCache.getRecord(id);
        if (record instanceof Error) {
            return <Err err={record}/>;
        }
        if (!record) {
            return <Wait/>;
        }
        const [rootSchema, blockSchemas] = serverCache.getRecordSchemas(record);
        const community = serverCache.getCommunity(record.getIn(['metadata', 'community']));

        return (
            <ReplaceAnimate>
                <Record record={record} community={community} rootSchema={rootSchema} blockSchemas={blockSchemas}/>
            </ReplaceAnimate>
        );
    }
});


const Record = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderFixedFields(record, community) {
        function renderTitle(title, i) {
            return (
                <h2 key={i} className="name">{title.get('title')}</h2>
            );
        }
        function renderCreator(creator) {
            const c = creator.get('creator_name');
            return (
                <span key={c}> <a className="creator" key={c}>{c}</a>; </span>
            );
        }
        function renderDates(record) {
            const created = moment(record.get('created')).format('ll');
            const updated = moment(record.get('updated')).format('ll');
            return (
                <div>
                    <p> <span style={{color:'#225'}}>{created}</span> </p>
                    { created != updated
                        ? <p>
                            <span style={{color:'#aaa'}}>Last updated at </span>
                            <span style={{color:'#225'}}>{updated}</span>
                          </p>
                        : false }
                </div>
            );
        }
        function renderDescription(description, i) {
            return (
                <p className="description" key={i}>
                    <span style={{fontWeight:'bold'}}>{description.get('description_type')}: </span>
                    {description.get('description')}
                </p>
            );
        }
        function renderSmallCommunity(community) {
            return !community ? false :
                (community instanceof Error) ? <Err err={community}/> :
                (
                    <div key={community.get('id')}>
                        <div className="community-small passive" title={community.get('description')}>
                            <p className="name">{community.get('name')}</p>
                            <img className="logo" src={community.get('logo')}/>
                        </div>
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
        const sr = {marginBottom:0, padding:'0.5em', float:'right'};

        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">
                        {   // do not allow record editing, for now
                            //<Link to={`/records/${record.get('id')}/edit`} style={sr}>Edit Record</Link>
                        }
                        <Link to={`/records/${record.get('id')}/abuse`} style={sr}>Report Abuse</Link>
                        { metadata.get('titles').map(renderTitle)}
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-8 col-md-10">
                        <p>
                            <span style={{color:'black'}}> by </span>
                            { !creators ? <span style={{color:'black'}}> [Unknown] </span> :
                                creators.map(renderCreator)
                            }
                        </p>

                        { renderDates(record) }

                        { descriptions ? descriptions.map(renderDescription) : false }

                        { !disciplines ? false :
                            <p className="discipline">
                                <span style={{fontWeight:'bold'}}>Disciplines: </span>
                                {disciplines.map(k => <span key={k}>{k}; </span>)}
                            </p>
                        }

                        { !keywords ? false :
                            <p className="keywords">
                                <span style={{fontWeight:'bold'}}>Keywords: </span>
                                {keywords.map(k => <Link to={{pathname:'/records', query:{q:k}}} key={k}>{k}; </Link>)}
                            </p>
                        }

                        {doi ?
                            <p className="pid" style={{marginBottom:0}}>
                                <span style={{fontWeight:'bold'}}>DOI: </span>
                                <PersistentIdentifier style={{marginLeft:'1em'}} pid={doi} doi={true}/>
                            </p> : false
                        }
                        {pid ?
                            <p className="pid">
                                <span style={{fontWeight:'bold'}}>PID: </span>
                                <PersistentIdentifier style={{marginLeft:'1em'}} pid={pid} />
                            </p> : false
                        }
                    </div>

                    <div className="col-sm-4 col-md-2">
                        <div style={{float:'right', width:'10em'}}>
                            { renderSmallCommunity(community) }
                        </div>
                    </div>
                </div>
            </div>
        );
    },

    fixedFields: {
        'community': true, 'titles': true, 'descriptions': true,
        'creators': true, 'keywords': true, 'disciplines': true, 'publication_state': true,
    },

    renderFileList(files) {
        const show_accessrequest = (this.props.record.getIn(['metadata', 'open_access']) === false &&
            this.props.record.getIn(['metadata', 'owners', 0]) != serverCache.getUser().get('id'));

        let fileComponent = false;
        if (!(files && files.count && files.count())) {
            fileComponent = <div>No files available.</div>;
        } else {
            fileComponent =
                <div className='fileList'>
                    <FileRecordHeader/>
                    { files.map(f => <FileRecordRow key={f.get('key')} file={f}/>) }
                </div>;
        }
        return (
            <div className="well">
                <div className="row">
                    <h3 className="col-sm-9" style={{marginTop:0}}>
                        { 'Files' }
                    </h3>
                </div>
                { fileComponent }
                { show_accessrequest ?
                    <Link to={`/records/${this.props.record.get('id')}/accessrequest`}>
                        Request data access
                    </Link> : false }
            </div>
        );
    },

    renderField(id, schema, value) {
        function renderScalar(schema, value) {
            const type = schema.get('type');
            if (type === 'string' && schema.get('format') === 'date-time') {
                value = moment(value).format("LLLL");
            } else if (type === 'boolean') {
                const markClass = "glyphicon glyphicon-" + (value ? "ok":"remove");
                const markStyle = {color: value ? "green":"red"};
                return (
                    <label>
                        <span style={{fontWeight:'normal', marginRight:'0.5em'}}>{value ? "True":"False"}</span>
                        <span className={markClass} style={markStyle} aria-hidden="true"/>
                    </label>
                );
            }
            return value;
        }

        if (value === undefined || value === null) {
            return false;
        }
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
            inner = (
                <ul className="list-unstyled">
                    { schema.get('properties').entrySeq().map(
                        ([pid, pschema]) => this.renderField(pid, pschema, value.get(pid))) }
                </ul>
            );
        } else {
            inner = <span key={id}>{renderScalar(schema, value)}</span>
        }

        const leftcolumn = !title ? false :
            <div className="col-sm-4">
                <span style={{fontWeight:'bold'}}>{title}</span>
            </div>;
        const rightcolumnsize = leftcolumn ? "col-sm-8" : "col-sm-12";
        const style = {marginBottom:'0.25em'};
        if (type === 'object') {
            style.borderLeft = '1px solid #ccc';
            style.borderRadius = '4px';
            style.marginBottom = '0.5em';
        }

        return (
            <li key={id} className="row">
                {leftcolumn}
                <div className={rightcolumnsize} style={style}> {inner} </div>
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
            const style = {
                marginTop:'0.25em',
                marginBottom:'0.25em',
                paddingTop:'0.25em',
                paddingBottom:'0.25em',
            };
            return <div style={style} key={pid}> {f} </div>;
        }
        const majorFields = majors.entrySeq().map(renderBigField.bind(this, excludeFields));
        const minorFields = minors.entrySeq().map(renderBigField.bind(this, excludeFields));

        const blockStyle=schemaID ? {marginTop:'1em', paddingTop:'1em'} : {};
        blockStyle.overflow = 'scroll';
        return (
            <div style={blockStyle} key={schemaID||"_"} className="well">
                <div className="row">
                    <h3 className="col-sm-9" style={{marginTop:0}}>
                        { schemaID ? schema.get('title') : 'Basic metadata' }
                    </h3>
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
        const files = this.props.record.get('files') || this.props.record.getIn(['metadata', '_files']);
        if (!this.props.record || !rootSchema) {
            return <Wait/>;
        }
        return (
            <div className="container-fluid">
                <div className="large-record">
                    <div className="row">
                        <div className="col-lg-12">
                            {this.renderFixedFields(this.props.record, this.props.community)}
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-lg-6">
                            { this.renderFileList(files) }
                        </div>

                        <div className="col-lg-6">
                            { this.renderFieldBlock(null, rootSchema, this.fixedFields) }

                            { !blockSchemas ? false :
                                blockSchemas.map(([id, blockSchema]) =>
                                    this.renderFieldBlock(id, (blockSchema||Map()).get('json_schema'), {})) }
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});
