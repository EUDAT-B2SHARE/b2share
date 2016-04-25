import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';
import { keys, timestamp2str } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';


export const RecordRoute = React.createClass({
    render() {
        const { id } = this.props.params;
        const record = serverCache.getRecord(id);
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

    renderDates(record) {
        const created = timestamp2str(record.get('created'));
        const updated = timestamp2str(record.get('updated'));
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
        const sr = {marginBottom:0, padding:'0.5em', float:'right'};
        return (
            <div>
                <div className="row">
                    <div className="col-md-12">
                        <Link to={`/records/${record.get('id')}/edit`} style={sr}>Edit Record</Link>
                        <h3 className="name">{metadata.get('title')}</h3>
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

    renderFieldType(id, name, type, value) {
        if (type === 'array') {
            value = value.map(v => <span key={v}>{v}; </span>);
        } else if (type === 'boolean') {
            value = value ? "True":"False";
        } else if (type === 'date-time') {
            value = timestamp2str(value);
        }
        return (
            <div className={"row "+id} key={id} style={{marginTop:'0.5em', marginBottom:'0.5em'}}>
                <div className="col-md-3" style={{fontWeight:'bold'}}>{name}: </div>
                <div className="col-md-9">{value}</div>
            </div>
        );
    },

    renderFieldBySchema(fieldName, fieldSchema, metadata) {
        let v = metadata.get(fieldName);
        if (!v) {
            return false;
        }
        if (v.toJS) {
            v = v.toJS();
        }
        const name = fieldSchema.get('title') || fieldName;
        const type = fieldSchema.get('type');
        const format = fieldSchema.get('format');
        return this.renderFieldType(fieldName, name, format ? format : type, v);
    },

    renderRootMetadata(record, rootSchema) {
        if (!rootSchema) {
            return false;
        }
        const except = {'$schema':true, 'community_specific':true,
            'title':true, 'description':true, 'keywords':true, 'community':true, 'creator':true};
        const metadata = record.get('metadata') || Map();

        const fields = [];
        rootSchema.get('properties').entrySeq().forEach( ([p, v]) => {
            if (!except.hasOwnProperty(p)) {
                const f = this.renderFieldBySchema(p, v, metadata);
                if (f) {
                    fields.push(f);
                }
            }
        });

        return (
            <div style={{marginTop:'1em', paddingTop:'1em', borderTop:'1px solid #eee'}}>
                {fields}
            </div>
        );
    },

    renderBlocksMetadata(record, blockSchemas) {
        if (!blockSchemas) {
            return false;
        }
        const except = {'$schema':true};
        const community_specific = record.getIn(['metadata', 'community_specific']) || Map();

        const fields = [];
        blockSchemas.forEach( ([schemaID, schemaBlock]) => {
            const metadataBlock = community_specific.get(schemaID);
            if (metadataBlock && schemaBlock) {
                schemaBlock.getIn(['json_schema', 'properties']).entrySeq().forEach( ([p, v]) => {
                    if (!except.hasOwnProperty(p)) {
                        const f = this.renderFieldBySchema(p, v, metadataBlock);
                        if (f) {
                            fields.push(f);
                        }
                    }
                });
            }
        });

        return (
            <div style={{marginTop:'1em', paddingTop:'1em', borderTop:'1px solid #eee'}}>
                {fields}
            </div>
        );
    },

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-md-12">
                        <div className="large-record">
                            {this.renderFixedFields(this.props.record, this.props.community)}
                            {this.renderRootMetadata(this.props.record, this.props.rootSchema)}
                            {this.renderBlocksMetadata(this.props.record, this.props.blockSchemas)}
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});
