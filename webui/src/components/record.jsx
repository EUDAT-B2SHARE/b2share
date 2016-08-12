import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import moment from 'moment';
import { serverCache, Error } from '../data/server';
import { keys, humanSize } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';
import { Wait, Err } from './waiting.jsx';
import { FileRecordHeader, FileRecordRow, EpicPid } from './editfiles.jsx';
import { getSchemaOrderedMajorAndMinorFields, getType } from './schema.jsx';


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


const excludeFields = {
    'title': true, 'description': true, 'keywords': true, 'community': true,
    'creators': true, 'publication_state': true,
};


const Record = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderDates(record) {
        const created = moment(record.get('created')).format('ll');
        const updated = moment(record.get('updated')).format('ll');
        return (
            <div>
                <p>
                    <span style={{color:'#225'}}>{created}</span>
                </p>
                { created != updated
                    ? <p>
                        <span style={{color:'#aaa'}}>Last updated at </span>
                        <span style={{color:'#225'}}>{updated}</span>
                      </p>
                    : false }
            </div>
        );
    },

    renderCreators(metadata) {
        const creators = metadata.get('creator');
        if (!creators) {
            return false;
        }

        return (
            <p>
                <span style={{color:'black'}}> by </span>
                { creators && creators.count()
                    ? creators.map(c => <a className="creator" key={c}> {c}</a>)
                    : <span style={{color:'black'}}> [Unknown] </span>
                }
            </p>
        );
    },

    renderSmallCommunity(community) {
        if (!community) {
            return false;
        }
        if (community instanceof Error) {
            return <Err err={community}/>;
        }
        return (
            <div key={community.get('id')}>
                <div className="community-small passive" title={community.get('description')}>
                    <p className="name">{community.get('name')}</p>
                    <img className="logo" src={community.get('logo')}/>
                </div>
            </div>
        );
    },

    renderFixedFields(record, community) {
        const metadata = record.get('metadata') || Map();
        const description = metadata.get('description') ||"";
        const keywords = metadata.get('keywords') || List();
        const pid = metadata.get('PID');
        const sr = {marginBottom:0, padding:'0.5em', float:'right'};
        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">
                        {   // do not allow record editing, for now
                            //<Link to={`/records/${record.get('id')}/edit`} style={sr}>Edit Record</Link>
                        }
                        <h2 className="name">{metadata.get('title')}</h2>
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-8 col-md-10">
                        { this.renderCreators(metadata) }
                        { this.renderDates(record) }

                        <p className="description">
                            <span style={{fontWeight:'bold'}}>Abstract: </span>
                            {description}
                        </p>

                        <p className="keywords">
                            <span style={{fontWeight:'bold'}}>Keywords: </span>
                            {keywords.map(k => <Link to={{pathname:'/records', query:{query:k}}} key={k}>{k}; </Link>)}
                        </p>

                        {pid ?
                            <p className="pid">
                                <span style={{fontWeight:'bold'}}>PID: </span>
                                <EpicPid style={{marginLeft:'1em'}} pid={pid} />
                            </p> : false
                        }
                    </div>

                    <div className="col-sm-4 col-md-2">
                        <div style={{float:'right', width:'10em'}}>
                        { this.renderSmallCommunity(community) }
                        </div>
                    </div>
                </div>
            </div>
        );
    },

    renderFieldByType(type, value) {
        if (type.isArray) {
            const innerType = Object.assign({}, type, {isArray:false});
            value = value.map((v,i) => <span key={i}>{this.renderFieldByType(innerType, v)}; </span>);
        } else if (type === 'date-time') {
            value = moment(value).format;
        }

        if (type.type === 'boolean') {
            const markClass = "glyphicon glyphicon-" + (value ? "ok":"remove");
            const markStyle = {color: value ? "green":"red"};
            return (
                <label> <span style={{fontWeight:'normal', marginRight:'0.5em'}}>{value ? "True":"False"}</span>
                        <span className={markClass} style={markStyle} aria-hidden="true"/></label>);
        }

        return value;
    },

    renderField(blockID, fieldID, fieldSchema, blockSchema) {
        let v = blockID ? this.props.record.getIn(['metadata', 'community_specific', blockID, fieldID]) :
                            this.props.record.getIn(['metadata', fieldID]);
        if (v === undefined || v === null || v === "") {
            return false;
        }
        if (v.toJS) {
            v = v.toJS();
        }
        const type = getType(fieldSchema, fieldID, blockSchema);
        return (
            <div key={fieldID} style={{marginTop:'0.5em', marginBottom:'0.5em'}}>
                <label style={{fontWeight:'bold'}}>{fieldSchema.get('title') || fieldID}: </label>
                <span> {this.renderFieldByType(type, v)}</span>
            </div>
        );
    },

    renderFieldBlock(schemaID, schema) {
        if (!schema) {
            return <Wait key={schemaID}/>;
        }

        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(schema);

        const majorFields = majors.entrySeq().map(
            ([id, f]) => excludeFields[id] ? false : this.renderField(schemaID, id, f, schema));
        const minorFields = minors.entrySeq().map(
            ([id, f]) => this.renderField(schemaID, id, f, schema));

        const blockStyle=schemaID ? {marginTop:'1em', paddingTop:'1em'} : {};
        return (
            <div style={blockStyle} key={schemaID} className="well">
                <div className="row">
                    <h3 className="col-sm-9" style={{marginTop:0}}>
                        { schemaID ? schema.get('title') : 'Basic metadata' }
                    </h3>
                </div>
                <div className="row">
                    <div className="col-sm-12">
                        { majorFields }
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-12">
                        { minorFields }
                    </div>
                </div>
            </div>
        );
    },

    renderFileList(files) {
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
                            { this.renderFieldBlock(null, rootSchema) }

                            { blockSchemas ? blockSchemas.map(([id, blockSchema]) =>
                                this.renderFieldBlock(id, blockSchema ? blockSchema.get('json_schema') : null)
                              ) : false }
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});

