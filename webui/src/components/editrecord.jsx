import React from 'react/lib/ReactWithAddons';
import { Link, browserHistory } from 'react-router'
import { Map, fromJS } from 'immutable';
import { compare } from 'fast-json-patch';

import Toggle from 'react-toggle';
import { DateTimePicker, Multiselect, DropdownList, NumberPicker } from 'react-widgets';
import moment from 'moment';
import momentLocalizer from 'react-widgets/lib/localizers/moment';
import numberLocalizer from 'react-widgets/lib/localizers/simple-number';
momentLocalizer(moment);
numberLocalizer();

import { keys, timestamp2str, pairs } from '../data/misc';
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';
import { HeightAnimate, ReplaceAnimate } from './animate.jsx';
import { getSchemaOrderedMajorAndMinorFields, getType } from './schema.jsx';


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
            record => { browserHistory.push(`/records/${record.id}/edit`); }
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

    onTitleChange(event) {
        this.setState({title:event.target.value});
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
                                <input type="text" className="form-control" id='title' value={this.state.title} onChange={this.onTitleChange} />
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

    setError(id, msg) {
        const err = this.state.errors;
        err[id] = msg;
        this.setState({errors: this.state.errors});
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

    getValue(blockID, fieldID, type) {
        const r = this.state.record;
        if (!r) {
            return null;
        }
        let v = blockID ? r.getIn(['community_specific', blockID, fieldID]) : r.get(fieldID);
        if (v != undefined && v != null) {
            if (v.toJS){
                v = v.toJS();
            }
        }
        return v;
    },

    setValue(blockID, fieldID, type, value) {
        let r = this.state.record;
        if (blockID) {
            if (!r.has('community_specific')) {
                r = r.set('community_specific', Map());
            }
            if (!r.hasIn(['community_specific'], blockID)) {
                r = r.setIn(['community_specific', blockID], Map());
            }
        }

        if (type.isArray && !Array.isArray(value)) {
            console.error("array expected, instead got:", value);
        }
        if (type.isArray) {
            value = fromJS(value);
        }
        r = blockID ? r.setIn(['community_specific', blockID, fieldID], value) : r.set(fieldID, value);
        // console.log('set field ' + blockID +"/"+ fieldID + " to:", value);
        this.setState({record:r});
    },

    renderScalarField(type, getValue, setValue) {
        if (type.type === 'boolean') {
            return <Toggle defaultChecked={getValue()} onChange={event => setValue(event.target.checked)} />
        } else if (type.type === 'integer') {
            return <NumberPicker defaultValue={getValue()} onChange={setValue} />
        } else if (type.type === 'number') {
            return <NumberPicker defaultValue={getValue()} onChange={setValue} />
        } else if (type.type === 'string') {
            const value = ""+(getValue() || "");
            if (type.enum) {
                return <DropdownList defaultValue={getValue()} data={type.enum.toJS()} onChange={setValue} />
            } else if (type.format === 'date-time') {
                return <DateTimePicker defaultValue={moment(getValue()).toDate()}
                        initialView={"year"} onChange={date => setValue(moment(date).toISOString())} />
            } else if (type.format === 'email') {
                return <input type="text" className="form-control" placeholder="email@example.com"
                        value={getValue() || ""} onChange={event => setValue(event.target.value)} />
            } else {
                return <textarea className="form-control" rows={value.length > 100 ? 5 : 1}
                        value={getValue() || ""} onChange={event => setValue(event.target.value)} />
            }
        } else {
            console.error("Cannot render field of type:", type);
        }
    },

    renderArrayField(type, getValue, setValue, _, index) {
        const getV = () => {
            const values = getValue();
            return values ? values[index] : undefined;
        }
        const setV = (v) => {
            const values = getValue() || [];
            values[index] = v;
            setValue(values);
        }
        const btnOnClick = (ev) => {
            ev.preventDefault();
            let values = getValue();
            if (index === 0) {
                if (values) {
                    values.push("");
                } else {
                    values=[""];
                }
            } else {
                values.splice(index, 1);
            }
            setValue(values);
        }
        return (
            <div id={index} key={index} className="input-group" style={{marginTop:'0.25em', marginBottom:'0.25em'}}>
                {this.renderScalarField(type, getV, setV)}
                {index == 0 ?
                    <a className="input-group-addon" href="#" onClick={btnOnClick}  style={{backgroundColor:'white'}} >
                        <span className="glyphicon glyphicon-plus-sign" aria-hidden="true"/>
                    </a> :
                    <a className="input-group-addon" href="#" onClick={btnOnClick}  style={{backgroundColor:'white'}} >
                        <span className="glyphicon glyphicon-minus-sign" aria-hidden="true"/>
                    </a>
                }
            </div>
        );
    },

    renderField(blockID, fieldID, fieldSchema) {
        const plugin = null;
        if (!fieldSchema) {
            return false;
        }
        const type = getType(fieldSchema);
        const getValue = this.getValue.bind(this, blockID, fieldID, type);
        const setValue = this.setValue.bind(this, blockID, fieldID, type);

        let field = false;
        if (!blockID && fieldID === 'community') {
            field = this.props.community ? renderSmallCommunity(this.props.community, false) : <Wait/>
        } else if (!type.isArray) {
            field = this.renderScalarField(type, getValue, setValue);
        } else {
            let values = getValue() || [""];
            if (values.length === 0) {
                values.push("");
            }
            field = values.map(this.renderArrayField.bind(this, type, getValue, setValue));
        }

        const arrstyle= !type.isArray ? {} : {
            paddingLeft:'10px',
            borderLeft:'1px solid black',
            borderRadius:'4px',
        };

        return (
            <div className="form-group row" key={fieldID} style={{marginTop:'1em'}} title={fieldSchema.get('description')}>
                <label htmlFor={fieldID} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                    <span style={{float:'right'}}>
                        {fieldSchema.get('title') || fieldID}
                    </span>
                </label>
                <div className="col-sm-9" style={arrstyle}>
                    {field}
                </div>
            </div>
        );
    },

    renderFieldBlock(schemaID, schema) {
        if (!schema) {
            return <Wait key={schemaID}/>;
        }
        let open = this.state.folds ? this.state.folds[schemaID||""] : false;
        const plugins = schema.getIn(['b2share', 'plugins']);

        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(schema);

        const majorFields = majors.entrySeq().map(([id, f]) => this.renderField(schemaID, id, f));
        const minorFields = minors.entrySeq().map(([id, f]) => this.renderField(schemaID, id, f));

        const onMoreDetails = e => {
            e.preventDefault();
            const folds = this.state.folds || {};
            folds[schemaID||""] = !folds[schemaID||""];
            this.setState({folds:folds});
        }

        const foldBlock = minorFields.count() ? (
            <div className="col-sm-12">
                <div className="row">
                    <div className="col-sm-offset-3 col-sm-9" style={{marginTop:'1em', marginBottom:'1em'}}>
                        <a href="#" onClick={onMoreDetails} style={{padding:'0.5em'}}>
                            { !open ? "Show more details" : "Hide details" }
                        </a>
                    </div>
                </div>
                <HeightAnimate delta={20}>
                    { open ? minorFields : false }
                </HeightAnimate>
            </div>
        ) : false;

        const blockStyle=schemaID ? {marginTop:'1em', paddingTop:'1em', borderTop:'1px solid #eee'} : {};
        return (
            <div style={blockStyle} key={schemaID}>
                <div className="row">
                    <h3 className="col-sm-offset-3 col-sm-9" style={{marginBottom:'1em'}}>
                        { schemaID ? schema.get('title') : 'Basic fields' }
                    </h3>
                </div>
                <div className="row">
                    <div className="col-sm-12">
                        { majorFields }
                    </div>
                </div>
                <div className="row">
                    { foldBlock }
                </div>
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

    updateRecord(event) {
        event.preventDefault();
        const original = this.props.record.get('metadata').toJS();
        const updated = this.state.record.toJS();
        const patch = compare(original, updated);
        serverCache.patchRecord(this.props.record.get('id'), patch,
            record => { browserHistory.push(`/records/${record.id}`); }
        );
    },

    render() {
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas;
        if (!this.state.record || !rootSchema) {
            return <Wait/>;
        }
        return (
            <div className="edit-record">
                <div>
                    <form className="form-horizontal" onSubmit={this.updateRecord}>
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

function renderSmallCommunity(community, active, onClickFn) {
    const activeClass = active ? " active": " inactive";
    return (
        <a href="#" key={community.get('id')}
                className={"community-small" + activeClass} title={community.get('description')}
                onClick={onClickFn ? onClickFn : ()=>{}}>
            <p className="name">{community.get('name')}</p>
            <img className="logo" src={community.get('logo')}/>
        </a>
    );
}

