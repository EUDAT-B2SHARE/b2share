import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import moment from 'moment';
import Toggle from 'react-toggle';
import { serverCache, Error } from '../data/server';
import { keys, humanSize } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';
import { Wait, Err } from './waiting.jsx';
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
                    <div className="col-md-12">
                        <Link to={`/records/${record.get('id')}/edit`} style={sr}>Edit Record</Link>
                        <h2 className="name">{metadata.get('title')}</h2>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-8">
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
                                <code>{pid}</code>
                            </p> : false
                        }
                    </div>

                    <div className="col-md-4">
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
            return <label><span style={{fontWeight:'normal', marginRight:'0.5em'}}>{value ? "True":"False"}</span><Toggle defaultChecked={value} disabled="disabled" /></label>;
        }

        return value;
    },

    renderField(blockID, fieldID, fieldSchema, blockSchema) {
        let v = blockID ? this.props.record.getIn(['metadata', 'community_specific', blockID, fieldID]) :
                            this.props.record.getIn(['metadata', fieldID]);
        if (v != undefined && v != null) {
            if (v.toJS){
                v = v.toJS();
            }
        }
        if (!v) {
            return false;
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
            <div style={blockStyle} key={schemaID}>
                <div className="row">
                    <h3 className="col-sm-9" style={{marginBottom:'1em'}}>
                        { schemaID ? schema.get('title') : 'Basic fields' }
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
        if (!files || !files.count()) {
            return false;
        }
        if (files instanceof Error) {
            return <Err err={files}/>;
        }
        const renderFile = file => {
            return (
                <dl className="dl-horizontal file" key={file.get('uuid')} style={{marginTop:'0.5em', marginBottom:'0.5em'}}>
                    <dt>Name</dt><dd><a href={file.get('url')}>{file.get('key')}</a></dd>
                    <dt>PID</dt><dd>{file.get('PID') || "-"}</dd>
                    <dt>Media Type</dt><dd>{file.get('mimetype') || "-"}</dd>
                    <dt>Size</dt><dd>{humanSize(file.get('size'))}</dd>
                    <dt>Checksum</dt><dd>{file.get('checksum') || "-"}</dd>
                    <dt>Updated</dt><dd>{moment(file.get('updated')).format('ll')}</dd>
                </dl>
            );
        };
        return (
            <div>
                <div className="row">
                    <h3 className="col-sm-9">
                        { 'Files' }
                    </h3>
                </div>
                <div className='fileList'>
                    { files.map(renderFile) }
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
                <div className="row">
                    <div className="col-md-12">
                        <div className="large-record">
                            {this.renderFixedFields(this.props.record, this.props.community)}

                            { this.renderFieldBlock(null, rootSchema) }

                            { blockSchemas ? blockSchemas.map(([id, blockSchema]) =>
                                this.renderFieldBlock(id, blockSchema ? blockSchema.get('json_schema') : null)
                              ) : false }

                            { this.renderFileList(files) }
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});
