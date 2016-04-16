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
                        <span style={bland}>Last updated at </span>
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

    renderFixedFields(record, community) {
        const metadata = record.get('metadata') || Map();
        const description = metadata.get('description') ||"";
        const keywords = metadata.get('keywords') || List();
        return (
            <div>
                <h3 className="name">{metadata.get('title')}</h3>

                { this.renderCreators(metadata) }
                { this.renderDates(record) }

                <p className="description">
                    <span style={{fontWeight:'bold'}}>Abstract: </span>
                    {description}
                </p>

                { community ?
                    <p className="community">
                        <span style={{fontWeight:'bold'}}>Community: </span>
                        {community.get('name')}
                    </p> : false }

                <p className="keywords">
                    <span style={{fontWeight:'bold'}}>Keywords: </span>
                    {keywords.map(k => <Link to='/records' params={{query:k}} key={k}>{k}; </Link>)}
                </p>
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


///////////////////////////////////////////////////////////////////////////////

export const NewRecordRoute = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    getInitialState() {
        return {
            community_id: null,
            title: "",
        }
    },

    createAndGoToRecord(event) {
        event.preventDefault();
        serverCache.createRecord(
            { community: this.state.community_id, title: this.state.title, open_access: true },
            record => { window.location.assign(`${window.location.origin}/records/${record.id}/edit`); }
        );
    },

    selectCommunity(community_id) {
        this.setState({community_id: community_id});
    },

    renderCommunity(community) {
        const active = community.get('id') === this.state.community_id;
        return renderCommunity(community, active, this.selectCommunity.bind(this, community.get('id')));
    },

    renderCommunityList(communities) {
        if (!communities) {
            return <Wait/>;
        }
        return (
            <div className="container-fluid">
                <div className="row">
                    { communities.map(this.renderCommunity) }
                </div>
            </div>
        );
    },

    render() {
        const communities = serverCache.getCommunities();
        const gap = {marginTop:'1em'};
        const biggap = {marginTop:'2em'};
        return (
            <div className="new-record">
                <div className="row">
                    <form className="form" onSubmit={this.createAndGoToRecord}>
                        <div className="form-group row">
                            <label htmlFor="title" className="col-sm-3 control-label" style={gap}>Title</label>
                            <div className="col-sm-9" style={gap}>
                                <input type="text" className="form-control" id="title" valueLink={this.linkState('title')} />
                            </div>
                        </div>

                        <div className="form-group row">
                            <label htmlFor="community" className="col-sm-3 control-label" style={gap}>
                                <div style={{fontWeight:'bold'}}>Community</div>
                            </label>
                            <div className="col-sm-9">
                                {this.renderCommunityList(communities)}
                            </div>
                        </div>

                        <div className="form-group submit row">
                            <div className="col-sm-offset-3 col-sm-9" style={biggap}>
                                <button type="submit" className="btn btn-primary btn-default btn-block">
                                    Create Draft Record</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
});


export const EditRecordRoute = React.createClass({
    render() {
        const { id } = this.props.params;
        const record = serverCache.getRecord(id);
        if (!record) {
            return <Wait/>;
        }

        const community_id = record.get('metadata').get('community');
        const community = serverCache.getCommunity(community_id);
        if (!community) {
            return <Wait/>;
        }

        return <EditRecord record={record} community={community} />;
    }
});


const EditRecord = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    getInitialState() {
        return {};
    },

    componentWillMount() {
        this.record = this.props.record;
        this.community = this.props.community;
        this.schema = this.props.schema || defaultSchema;
        this.fields = keys(this.schema.properties);
        this.metadata = this.record.get('metadata') || Map();

        let state = {};
        if (this.fields && this.metadata) {
            for (const i in this.fields) {
                const f = this.fields[i];
                state[f] = this.metadata.get(f);
            }
        }
        this.setState(state);
    },

    rnd() {
        const BIG = 1024 * 1024 * 1024;
        return Math.floor((Math.random() * BIG) + BIG);
    },

    renderField(id, field) {
        const gap = {marginTop:'1em'};
        return (
            <div className="form-group row" key={id} style={gap} title={field.description}>
                <label htmlFor={id} className="col-sm-3 control-label" style={{marginTop:10}}>{field.title}</label>
                <div className="col-sm-9">
                    <input type="text" className="form-control" id={id} valueLink={this.linkState(id)} />
                </div>
            </div>
        );
    },

    render() {
        return (
            <div className="edit-record">
                <div className="row">
                    <div className="col-md-12">
                        <div className="deposit-step">
                            <p>Step 01</p>
                            <h4>Drag and drop files here</h4>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <form className="form" onSubmit={this.createAndGoToRecord}>
                            <div className="form-group row">
                                <label htmlFor="community" className="col-sm-3 control-label">
                                    <div style={{fontWeight:'bold'}}>Community</div>
                                </label>
                                <div className="col-sm-9">
                                    {renderCommunity(this.community, true)}
                                </div>
                            </div>

                            {this.fields.map(f => this.renderField(f, this.schema.properties[f]))}

                            <div className="form-group submit">
                                <div className="col-sm-offset-3 col-sm-6" style={{marginTop:'1em'}}>
                                    <button type="submit" className="btn btn-primary btn-default btn-block">
                                        Create Draft Record</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        );
    }
});

///////////////////////////////////////////////////////////////////////////////

function renderCommunity(community, active, onClickFn) {
    const activeClass = active ? " active": " inactive";
    const newpadding = {padding:'0 2px'};
    return (
        <div className="col-lg-2 col-sm-3 col-xs-6" style={newpadding} key={community.get('id')}>
            <div className={"community"+activeClass} title={community.get('description')}
                    onClick={onClickFn ? onClickFn : ()=>{}}>
                <p className="name">{community.get('name')}</p>
                <img className="logo" src={community.get('logo')}/>
            </div>
        </div>
    );
}


