import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import moment from 'moment';
import { serverCache, Error } from '../data/server';
import { keys, humanSize } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';
import { Wait, Err } from './waiting.jsx';
import { FileRecordHeader, FileRecordRow } from './editfiles.jsx';
import { getSchemaOrderedMajorAndMinorFields, getType } from './schema.jsx';


export const DataCollectionRoute = React.createClass({
    render() {
        const { id } = this.props.params;
        const collection = serverCache.getDataCollection(id);
        if (collection instanceof Error) {
            return <Err err={collection}/>;
        }
        if (!collection) {
            return <Wait/>;
        }
        const [rootSchema, blockSchemas] = serverCache.getDataCollectionSchemas(collection);
        const community = serverCache.getCommunity(collection.getIn(['metadata', 'community']));

        return (
            <ReplaceAnimate>
                <DataCollection collection={collection} community={community} rootSchema={rootSchema} blockSchemas={blockSchemas}/>
            </ReplaceAnimate>
        );
    }
});


const excludeFields = {
    'title': true, 'description': true, 'keywords': true, 'community': true,
    'creators': true, 'publication_state': true,
};


const DataCollection = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderDates(collection) {
        const created = moment(collection.get('created')).format('ll');
        const updated = moment(collection.get('updated')).format('ll');
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

    renderFixedFields(collection, community) {
        const metadata = collection.get('metadata') || Map();
        const description = metadata.get('description') ||"";
        const keywords = metadata.get('keywords') || List();
        const pid = metadata.get('PID');
        const sr = {marginBottom:0, padding:'0.5em', float:'right'};
        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">
                        {   // do not allow data collection editing, for now
                            //<Link to={`/records/${collection.get('id')}/edit`} style={sr}>Edit Data Collection</Link>
                        }
                        <h2 className="name">{metadata.get('title')}</h2>
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-8 col-md-10">
                        { this.renderCreators(metadata) }
                        { this.renderDates(collection) }

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
        let v = blockID ? this.props.collection.getIn(['metadata', 'community_specific', blockID, fieldID]) :
                            this.props.collection.getIn(['metadata', fieldID]);
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
        if (!files || !files.count()) {
            return false;
        }
        if (files instanceof Error) {
            return <Err err={files}/>;
        }
        return (
            <div className="well">
                <div className="row">
                    <h3 className="col-sm-9" style={{marginTop:0}}>
                        { 'Files' }
                    </h3>
                </div>
                <div className='fileList'>
                    <FileRecordHeader/>
                    { files.map(f => <FileRecordRow key={f.get('key')} file={f}/>) }
                </div>
            </div>
        );
    },

    render() {
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas;
        const files = this.props.collection.get('files') || this.props.collection.getIn(['metadata', '_files']);
        if (!this.props.collection || !rootSchema) {
            return <Wait/>;
        }
        return (
            <div className="container-fluid">
                <div className="large-datacollection">
                    <div className="row">
                        <div className="col-lg-12">
                            {this.renderFixedFields(this.props.collection, this.props.community)}
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

