import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router';
import Toggle from 'react-toggle';

import { Map, List, OrderedMap } from 'immutable';
import { keys, timestamp2str, pairs } from '../data/misc';
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';
import { ReplaceAnimate } from './animate.jsx';
import { getType } from './schema.jsx';

export const NewRecordRoute = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    getInitialState() {
        return {
            community_id: null,
            title: "",
            errors: {},
        }
    },

    setError(id, msg) {
        const err = this.state.errors;
        err[id] = msg;
        this.setState({errors: this.state.errors});
    },

    createAndGoToRecord(event) {
        event.preventDefault();
        if (!this.state.title.length) {
            this.setError('title', "Please add a (temporary) record title");
            return;
        }
        if (!this.state.community_id) {
            this.setError('community', "Please select a target community");
            return;
        }
        serverCache.createRecord(
            { community: this.state.community_id, title: this.state.title, open_access: true },
            record => { window.location.assign(`${window.location.origin}/records/${record.id}/edit`); }
        );
    },

    selectCommunity(community_id) {
        this.setState({community_id: community_id});
    },

    renderCommunity(community) {
        const cid = community.get('id');
        const active = cid === this.state.community_id;
        return (
            <div className="col-lg-2 col-sm-3 col-xs-6" key={community.get('id')}>
                { renderSmallCommunity(community, active, this.selectCommunity.bind(this, cid)) }
            </div>
        );
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
        const stitle = {marginTop:'1em'};
        if (this.state.errors.title) {
            stitle.color = "red";
        }
        const scomm = {marginTop:'1em'};
        if (this.state.errors.community) {
            scomm.color = "red";
        }
        return (
            <div className="new-record">
                <div className="row">
                    <form className="form" onSubmit={this.createAndGoToRecord}>
                        <div className="form-group row">
                            <label htmlFor="title" className="col-sm-3 control-label" style={stitle}>Title</label>
                            <div className="col-sm-9" style={gap}>
                                <input type="text" className="form-control" id="title" valueLink={this.linkState('title')} />
                            </div>
                        </div>

                        <div className="form-group row">
                            <label htmlFor="community" className="col-sm-3 control-label" style={scomm}>
                                <div style={{fontWeight:'bold'}}>Community</div>
                            </label>
                            <div className="col-sm-9">
                                {this.renderCommunityList(communities)}
                            </div>
                        </div>

                        <div className="form-group submit row">
                            {this.state.errors.title ?
                                <div className="col-sm-9 col-sm-offset-3">{this.state.errors.title} </div>: false }
                            {this.state.errors.community ?
                                <div className="col-sm-9 col-sm-offset-3">{this.state.errors.community} </div> : false }
                            <div className="col-sm-offset-3 col-sm-9" style={gap}>
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
        const [rootSchema, blockSchemas] = serverCache.getRecordSchemas(record);
        const community = serverCache.getCommunity(record.getIn(['metadata', 'community']));

        return (
            <ReplaceAnimate>
                <EditRecord record={record} community={community} rootSchema={rootSchema} blockSchemas={blockSchemas}/>
            </ReplaceAnimate>
        );
    }
});


const EditRecord = React.createClass({
    getInitialState() {
        return {
            errors: {},
            record: null,
        };
    },

    renderFileZone() {
        return (
            <div className="row">
                <div className="col-md-12">
                    <div className="deposit-step">
                        <p>Step 01</p>
                        <h4>Drag and drop files here</h4>
                    </div>
                </div>
            </div>
        );
    },

    getValue(blockID, fieldID) {
        const r = this.state.record;
        if (!r) {
            return null;
        }
        const v = blockID ? r.getIn(['community_specific', blockID, fieldID]) : r.get(fieldID);
        // console.log('get field ' + blockID +"/"+ fieldID + " = ", v);
        return v;
    },

    setValue(blockID, fieldID, value) {
        let r = this.state.record;
        if (blockID) {
            if (!r.has('community_specific')) {
                r = r.set('community_specific', Map());
            }
            if (!r.hasIn(['community_specific'], blockID)) {
                r = r.setIn(['community_specific', blockID], Map());
            }
        }

        r = blockID ? r.setIn(['community_specific', blockID, fieldID], value) : r.set(fieldID, value);
        // console.log('set field ' + blockID +"/"+ fieldID + " to:", value);
        this.setState({record:r});
    },

    onChangeField(blockID, fieldID, event) {
        this.setValue(blockID, fieldID, event.target.value);
    },

    renderFieldText(blockID, fieldID, fieldSchema) {
        return (
            <div className="form-group row" key={fieldID} style={{marginTop:'1em'}} title={fieldSchema.get('description')}>
                <label htmlFor={fieldID} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                    {fieldSchema.get('title') || fieldID}</label>
                <div className="col-sm-9">
                    <input type="text" className="form-control" id={fieldID}
                        value={this.getValue(blockID, fieldID)} onChange={this.onChangeField.bind(this, blockID, fieldID)} />
                </div>
            </div>
        );
    },

    renderFieldDateTime(blockID, fieldID, fieldSchema) {
        return (
            <div className="form-group row" key={fieldID} style={{marginTop:'1em'}} title={fieldSchema.get('description')}>
                <label htmlFor={fieldID} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                    {fieldSchema.get('title') || fieldID}</label>
                <div className="col-sm-9">
                    <input type="text" className="form-control" id={fieldID}
                        value={this.getValue(blockID, fieldID)} onChange={this.onChangeField.bind(this, blockID, fieldID)} />
                </div>
            </div>
        );
    },

    renderFieldBoolean(blockID, fieldID, fieldSchema) {
        return (
            <div className="form-group row" key={fieldID} style={{marginTop:'1em'}} title={fieldSchema.get('description')}>
                <label htmlFor={fieldID} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                    {fieldSchema.get('title') || fieldID}</label>
                <div className="col-sm-9">
                     <Toggle defaultChecked={this.getValue(blockID, fieldID)} onChange={this.onChangeField.bind(this, blockID, fieldID)} />
                </div>
            </div>
        );
    },

    renderFieldCommunity(blockID, fieldID, fieldSchema) {
        return (
            <div className="form-group row" key={fieldID} style={{marginTop:'1em'}} title={fieldSchema.get('description')}>
                <label htmlFor={fieldID} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                    {fieldSchema.get('title') || fieldID}</label>
                <div className="col-sm-9">
                    {this.props.community ? renderSmallCommunity(this.props.community, false) : <Wait/>}
                </div>
            </div>
        );
    },

    renderField(blockID, fieldID, fieldSchema) {
        const plugin = null;
        if (!fieldSchema) {
            return false;
        }
        const type = getType(fieldSchema);
        if (!blockID && fieldID === 'community') {
            return this.renderFieldCommunity(blockID, fieldID, fieldSchema, type.isArray);
        } else if (type.type === 'boolean') {
            return this.renderFieldBoolean(blockID, fieldID, fieldSchema, type.isArray);
        } else if (type.type === 'string' && type.format === 'date-time') {
            return this.renderFieldDateTime(blockID, fieldID, fieldSchema, type.isArray);
        }
        return this.renderFieldText(blockID, fieldID, fieldSchema, type.isArray);
    },

    renderFieldBlock(schemaID, schema) {
        if (!schema) {
            return <Wait key={schemaID}/>;
        }
        const except = {'$schema':true, 'community_specific':true, '_internal':true};
        const properties = schema.get('properties');
        const plugins = schema.getIn(['b2share', 'plugins']);
        const presentation = schema.getIn(['b2share', 'presentation']);

        const majorIDs = presentation ? presentation.get('major') : null;
        const minorIDs = presentation ?  presentation.get('minor') : null;

        let minors = OrderedMap(minorIDs ? minorIDs.map(id => [id, properties.get('id')]) : []);
        let majors = OrderedMap(majorIDs ? majorIDs.map(id => [id, properties.get('id')]) : []);
        properties.entrySeq().forEach(([id, def]) => {
            if (majors.has(id)) {
                majors = majors.set(id, def);
            } else if (minors.has(id)) {
                minors = minors.set(id, def);
            } else if (!except.hasOwnProperty(id)) {
                majors = majors.set(id, def);
            }
        });

        const majorFields = majors.entrySeq().map(([id, f]) => this.renderField(schemaID, id, f));
        const minorFields = minors.entrySeq().map(([id, f]) => this.renderField(schemaID, id, f));

        return (
            <div className="row" key={schemaID} style={{marginTop:'1em', paddingTop:'1em', borderTop:'1px solid #eee'}}>
                { majorFields }
            </div>
        );
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(props) {
        if (props.record && !this.state.record) {
            this.setState({record:props.record.get('metadata')});
        }
    },

    render() {
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas;
        if (!this.state.record || !rootSchema) {
            return <Wait/>;
        }
        return (
            <div className="edit-record">
                <div className="row">
                    <form className="form" onSubmit={this.updateRecord}>
                        { this.renderFieldBlock(null, rootSchema) }

                        { blockSchemas ? blockSchemas.map(([id, blockSchema]) =>
                            this.renderFieldBlock(id, blockSchema ? blockSchema.get('json_schema') : null)
                          ) : false }

                        <div className="form-group submit row" style={{marginTop:'1em', paddingTop:'1em', borderTop:'1px solid #eee'}}>
                            {pairs(this.state.errors).map( ([id, msg]) =>
                                <div className="col-sm-9 col-sm-offset-3">{msg} </div>) }
                            <div className="col-sm-offset-3 col-sm-9">
                                <button type="submit" className="btn btn-primary btn-default btn-block">
                                    Update Draft/Record</button>
                            </div>
                        </div>

                    </form>
                </div>
            </div>
        );
    }
});

///////////////////////////////////////////////////////////////////////////////

export function renderSmallCommunity(community, active, onClickFn) {
    const activeClass = active ? " active": " inactive";
    return (
        <div key={community.get('id')}>
            <div className={"community-small" + activeClass} title={community.get('description')}
                    onClick={onClickFn ? onClickFn : ()=>{}}>
                <p className="name">{community.get('name')}</p>
                <img className="logo" src={community.get('logo')}/>
            </div>
        </div>
    );
}


