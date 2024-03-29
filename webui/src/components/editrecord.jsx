import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List, fromJS } from 'immutable';
import { compare } from 'fast-json-patch';

import Toggle from 'react-toggle';
import { DateTimePicker, Multiselect, DropdownList, NumberPicker } from 'react-widgets';
import moment from 'moment';
import momentLocalizer from 'react-widgets/lib/localizers/moment';
import numberLocalizer from 'react-widgets/lib/localizers/simple-number';
momentLocalizer(moment);
numberLocalizer();

import { serverCache, notifications, Error, browser } from '../data/server';
import { onAjaxError } from '../data/ajax';
import { keys, pairs, objEquals } from '../data/misc';
import { Wait, Err } from './waiting.jsx';
import { HeightAnimate, ReplaceAnimate } from './animate.jsx';
import { getSchemaOrderedMajorAndMinorFields, hiddenFields } from './schema.jsx';
import { EditFiles, PersistentIdentifier } from './editfiles.jsx';
import { canEditRecord } from './record.jsx';
import { Versions } from './versions.jsx';
import { SelectLicense } from './selectlicense.jsx';
import { SelectBig } from './selectbig.jsx';
import { renderSmallCommunity } from './common.jsx';


const invalidFieldMessage = field => `Please provide a correct value for field: ${field}`;


export const EditRecordRoute = React.createClass({
    isDraft: false,

    getRecordOrDraft() {
        const { id } = this.props.params;
        if (this.isDraft) {
            return serverCache.getDraft(id);
        }
        const record = serverCache.getRecord(id);
        if (record instanceof Error && record.code == 404) {
            this.isDraft = true;
            return serverCache.getDraft(id);
        }
        return record;
    },

    refreshCache() {
        const { id } = this.props.params;
        if (this.isDraft) {
            serverCache.getDraft(id);
        } else {
            serverCache.getRecord(id);
        }
    },

    patchRecordOrDraft(patch, onSuccessFn, onErrorFn) {
        const { id } = this.props.params;
        if (this.isDraft) {
            serverCache.patchDraft(id, patch, onSuccessFn, onErrorFn);
        } else {
            serverCache.patchRecord(id, patch, onSuccessFn, onErrorFn);
        }
    },

    render() {
        const record = this.getRecordOrDraft();
        if (!record) {
            return <Wait/>;
        }
        if (record instanceof Error) {
            return <Err err={record}/>;
        }
        const [rootSchema, blockSchemas] = serverCache.getRecordSchemas(record);
        if (rootSchema instanceof Error) {
            return <Err err={rootSchema}/>;
        }

        // need to be owner or community admin
        const canEdit = canEditRecord(record);
        if (canEdit === null) {
            return <Wait/>;
        } else if (!canEdit) {
            return <Err err={{code: 403, text: "Permission denied"}}/>;
        }

        return (
            <ReplaceAnimate>
                <EditRecord record={record}
                            rootSchema={rootSchema} blockSchemas={blockSchemas}
                            refreshCache={this.refreshCache}
                            patchFn={this.patchRecordOrDraft}
                            isDraft={this.isDraft} isVersion={true} />
            </ReplaceAnimate>
        );
    }
});

const EditRecordSmallCommunity = React.createClass({
    render() {
        if (!this.props.data) {
            return <Wait/>;
        }
        return (
            <a href="#" key={this.props.data.get('id')}
                    className={"community-small"}
                    title={this.props.data.get('description')}>
                <p className="name">{this.props.data.get('name')}</p>
                <img className="logo" src={this.props.data.get('logo')}/>
            </a>
        )
    }
});

const EditRecordDataElement = React.createClass({
    getInitialState() {
        if (this.props.args) {
            return {data: serverCache[this.props.load](...this.props.args, this.dataLoaded)};
        } else {
            return {data: serverCache[this.props.load](this.dataLoaded)};
        }
    },

    dataLoaded(data) {
        this.setState({data: data});
    },

    render() {
        if (this.state.data) {
            return React.cloneElement(this.props.children, this.state);
        }
        return null;
    }
});

const EditRecordFieldTree = React.createClass({
    getInitialState() {
        return {
            dirty: true,
            desc: "",
            opened: []  // itself and complex subfields
        };
    },

    shouldComponentUpdate(nextProps, nextState) {
        if (nextState.dirty) {
            this.state.dirty = false;
        }
        return nextState.dirty;
    },

    setValue(schema, path, value) {
        this.props.funcs.setValue(schema, path, value);
        this.setState({dirty: true});
    },

    addFieldButton(buttons, pathstr, name) {
        if (!(pathstr in buttons)) {
            buttons[pathstr] = []
        }
        buttons[pathstr].push(name)
        buttons[pathstr] = buttons[pathstr].filter((v, i, a) => a.indexOf(v) === i);
        return buttons;
    },

    renderScalarFieldButton(schema, path, buttonname) {
        const pathstr = path.join('/');

        const btnShowFieldDetails = (ev, pathstr) => {
            ev.preventDefault();
            let opened = this.state.opened;
            const index = opened.indexOf(pathstr);
            if (index > -1) {
                opened.splice(index, 1);
            } else {
                opened.push(pathstr)
            }
            this.setState({opened: opened, dirty: true});
        };

        const onSelectLicense = (license) => {
            console.assert(path.length >= 1);
            // get corresponding schema
            var pschema = this.getParentPathSchema(path);
            var pvalue = {}
            for (const [key, value] of Object.entries(license)) {
                if (pschema.hasIn(['properties', key])) {
                    pvalue[key] = value
                }
            }
            this.setValue(schema, path.slice(0, -1), fromJS(pvalue));
        };

        const buttons = {
            details: {'title': 'Show details for this field or entry', 'event': btnShowFieldDetails, 'icon': 'glyphicon-list-alt'}
        }

        switch (buttonname) {
            case 'license':
                return <SelectLicense title="Select License" onSelect={onSelectLicense} setModal={(modal) => this.props.setLicenseModal({modal: modal})} key={pathstr + "-" + buttonname} />
            default:
                return <span className="input-group-btn" key={pathstr + "-" + buttonname}>
                            <button className="btn btn-default btn-md" type="button" onClick={(ev) => (buttons[buttonname].event)(ev, pathstr)}
                                 title={buttons[buttonname].title}>
                                <span className={"glyphicon " + buttons[buttonname].icon} aria-hidden="true"/>
                            </button>
                        </span>
        }
    },

    renderButtonedScalarField(schema, path, buttons) {
        return (
            <div className="input-group">
                { this.renderScalarField(schema, path) }
                { buttons.map((name) => this.renderScalarFieldButton(schema, path, name)) }
            </div>
        )
    },

    getParentPathSchema(path) {
        // get schema path minus container and selector element
        const spath = path.slice(0, -1).map(x => Number.isInteger(x) ? ['items', 'properties'] : x).flat().slice(1);
        return this.props.schema.getIn(spath);
    },

    renderScalarField(schema, path, buttons={}, options={}) {
        const onDateChange = (date) => {
            const m = moment(date);
            this.setValue(schema, path, m.isValid() ? m.toISOString() : undefined);
        }

        const onEmbargoDateChange = date => {
            const m = moment(date);
            // true if embargo is in the past
            const access = m.isValid() ? (moment().diff(m) > 0) : true;
            this.setValue(null, ['open_access'], access);
            onDateChange(m)
        };

        const onVocabularySelect = (value, type) => {
            // if parent schema path is an object, map all values
            var pschema = this.getParentPathSchema(path);

            // if exists, we get the subfields for the element, not the definition of a single field (root schema v1)
            if (pschema && pschema.get('type') == undefined) {
                // apply all value elements
                var pvalue = {}
                for (const [key, value] of Object.entries(value)) {
                    if (pschema.has(key)) {
                        pvalue[key] = value;
                    } else if (pschema.has(type + "_" + key)) {
                        pvalue[type + "_" + key] = value;
                    }
                }
                this.setValue(schema, path.slice(0, -1), fromJS(pvalue));
            } else {
                // apply the identifier only (root schema v0)
                this.setValue(schema, path, value.identifier);
            }
        };

        const onFullNameChange = value => {
            var pschema = this.getParentPathSchema(path);
            // Check that only one name
            const re_check = /^([^,]*,){1}[^,;&:]*$/;
            const control_match = value.match(re_check);
            if (control_match === null && value.indexOf(',') > 0) {
                // If trying to add multiple, return
                return
            }
            // determine the values to be updated
            const re = /^([^,]+),?(.*)?$/;
            const matches = value.match(re);

            // update the other fields as well, if these fields are available and
            // all match groups have actual values
            if (pschema.has('given_name')) {
                // get the parent object path
                const ppath = path.slice(0, -1);
                if (matches && matches.filter(Boolean).length > 0) {
                    // define the new parent object value
                    var pvalue = Object.assign(this.props.funcs.getValue(ppath) || {}, {
                        [path.last()]: matches[0],
                        given_name: (matches[2] || "").trim(),
                        family_name: (matches[1] || "").trim()
                    });
                } else {
                    // remove all affected fields
                    var pvalue = Object.assign(this.props.funcs.getValue(ppath) || {});
                    [path.last(), 'given_name', 'family_name'].forEach((x) => { delete pvalue[x]; });
                }
                // set it
                this.setValue(schema, ppath, fromJS(pvalue));
            } else {
                // just set the value normally
                this.setValue(schema, path, value);
            }
        }

        const onPartialNameChange = (value, source, target) => {
            const ppath = path.slice(0, -1);
            // get the value of the other dependent field
            const other = source == 'given_name' ? 'family_name' : 'given_name';
            const ovalue = this.props.funcs.getValue(ppath.concat([other]));
            // if both values present, combine them for target
            if (value.length && ovalue.length) {
                var tvalue = source == 'given_name' ? `${ovalue}, ${value}` : `${value}, ${ovalue}`;
            } else {
                // otherwise take the value that is available or nothing
                var tvalue = value.length ? value : ovalue;
            }
            // define the new parent object value
            const pvalue = Object.assign(this.props.funcs.getValue(ppath) || {}, {
                [target]: tvalue,
                [source]: value
            });
            // set it
            this.setValue(schema, ppath, fromJS(pvalue));
        }

        const pathstr = path.join('/');
        if (pathstr in buttons) {
            return this.renderButtonedScalarField(schema, path, buttons[pathstr]);
        }

        const newpath = (last) => { const np = path.slice(); np.push(last); return np; };
        const lpath = path.last();
        const type = schema.get('type');
        const value = this.props.funcs.getValue(path);
        const format = schema.get('format') || "";

        if (['language', 'language_name'].includes(lpath)) {
            return <EditRecordDataElement load='getVocabulary' args={['languages']}>
                <SelectBig onSelect={x => onVocabularySelect(x, 'language')} value={value}
                           valueField={lpath == 'language_name' ? "name" : "id"} />
            </EditRecordDataElement>
        } else if (lpath == 'discipline_name' || (path[0] == 'disciplines' && path.length == 2 && type == 'string')) {
            return <EditRecordDataElement load='getVocabulary' args={['disciplines']}>
                <SelectBig onSelect={x => onVocabularySelect(x, 'discipline')} value={value} />
            </EditRecordDataElement>
        }

        const validClass = this.props.funcs.getError(pathstr) ? " invalid-field " : "";
        var setter = x => this.setValue(schema, path, x);
        if (type === 'boolean') {
            return (
                <div style={{lineHeight:"30px"}}>
                    <div className={validClass} style={{lineHeight:"30px"}}>
                        <Toggle checked={value} onChange={event => setter(event.target.checked)} disabled={options['disabled'] || false} />
                        <div style={{display:"inline", "verticalAlign":"super"}}>{value ? " True" : " False"}</div>
                    </div>
                </div>
            );
        } else if (type === 'integer' || type === 'number') {
            return <NumberPicker format={format=='coordinate' ? '-###.##' : null} className={validClass} value={value} onChange={setter} />
        } else if (type === 'string' || schema.get('enum')) {
            const value_str = "" + (value || "");
            // special handling for specific fields
            if (['creator_name', 'contributor_name'].includes(lpath)) {
                setter = x => onFullNameChange(x)
            } else if (['given_name', 'family_name'].includes(lpath)) {
                const pschema = this.getParentPathSchema(path);
                setter = x => onPartialNameChange(x, lpath, pschema.keySeq().toArray()[0]);
            }
            if (schema.get('enum')) {
                return <DropdownList className={validClass} value={value_str} data={schema.get('enum').toJS()} onChange={setter} />
            } else if (['date-time', 'date'].includes(format)) {
                const initial = (value_str && value_str !== "") ? moment(value_str).toDate() : null;
                return <DateTimePicker className={validClass} time={format == 'date-time'} value={initial}
                        format={"YYYY/MM/DD" + (format == 'date-time' ? " HH:mm" : "")} onChange={path == 'embargo_date' ? onEmbargoDateChange : onDateChange} />
            } else if (format === 'email') {
                return <input type="text" className={"form-control"+ validClass} placeholder="email@example.com"
                        value={value_str} onChange={event => setter(event.target.value)} />
            } else if (path[path.length-1] === 'description') {
                return <textarea className={"form-control"+ validClass} rows={value_str.length > 1000 ? 10 : 5}
                        value={value_str} onChange={event => setter(event.target.value)} />
            } else {
                return <input type="text" className={"form-control"+ validClass}
                        value={value_str} onChange={event => setter(event.target.value)} />
            }
        } else {
            console.error("Cannot render field of schema:", schema.toJS());
        }
    },

    renderComplexField(schema, path) {
        const newpath = (last) => { const np = path.slice(); np.push(last); return np; };

        let props = schema.get('properties').entrySeq();
        let required_props = props.filter(([pid, pschema]) => { return pschema.get('isRequired'); });
        let optional_props = props.filter(([pid, pschema]) => { return !pschema.get('isRequired'); });

        var buttons = {};
        var togglePath = togglePath = path.join('/');
        if (required_props.count()) {
            togglePath = newpath(required_props.toJS()[0][0]).join('/');
            if (optional_props.count()) {
                this.addFieldButton(buttons, togglePath, 'details');
            }
        }

        return (
            <div>
                { required_props.map(([pid, pschema]) => this.renderFieldTree(pid, pschema, newpath(pid), buttons)) }
                { (optional_props.count() && this.state.opened.includes(togglePath)) || !required_props.count() ?
                    <div className="container-fluid" style={{paddingLeft:0, paddingRight:0}}>
                        { optional_props.map(([pid, pschema]) => this.renderFieldTree(pid, pschema, newpath(pid))) }
                    </div>
                : false }
            </div>
        );
    },

    renderFieldTree(id, schema, path, buttons={}) {
        if (!schema) {
            return false;
        }
        const newpath = (last) => { const np = path.slice(); np.push(last); return np; };

        let field = false;
        if (objEquals(path, ['community'])) {
            field = <EditRecordDataElement load='getCommunity' args={[this.props.funcs.getValue(path)]}>
                <EditRecordSmallCommunity />
            </EditRecordDataElement>
        } else if (objEquals(path, ['license', 'license'])) {
            field = this.renderScalarField(schema, path, this.addFieldButton(buttons, path.join('/'), 'license'));
        } else if (objEquals(path, ['open_access'])) {
            const embargo = this.props.funcs.getValue(schema, newpath('embargo_date'));
            const disabled = embargo && moment(embargo).isValid();
            field = this.renderScalarField(schema, path, {}, {disabled: disabled});
        } else if (schema.get('type') === 'array') {
            const itemSchema = schema.get('items');
            const raw_values = this.props.funcs.getValue(path);
            const len = (raw_values && raw_values.length) || 1;
            const arrField = [...Array(len).keys()].map(i =>
                this.renderFieldTree(id+`[${i}]`, itemSchema, newpath(i)));
            const btnAddRemove = (ev, pos) => {
                ev.preventDefault();
                if (pos === 0) {
                    const itemType = itemSchema.get('type');
                    const values = this.props.funcs.getValue(path) || [];
                    const newItem = itemType === 'array' ? [] : itemType === 'object' ? {} : null;
                    values.push(newItem);
                    if (values.length == 1) {
                        // added value starting from an empty container; 2 values needed
                        values.push(newItem);
                    }
                    this.setValue(schema, path, fromJS(values));
                } else {
                    this.setValue(schema, newpath(pos), undefined);
                }
            }
            const btnClear = (ev) => {
                ev.preventDefault();
                this.props.funcs.removeErrors(path);
                this.setValue(schema, path, undefined);
            }
            field = arrField.map((f, i) =>
                <div className="container-fluid" key={id+`[${i}]`}>
                    <div className="row" key={i} style={{marginBottom:'0.5em'}}>
                        {f}
                        <div className={"col-sm-12"} style={{paddingLeft: 0, paddingRight:0}} />
                        <div className={"col-sm-12"} style={{paddingRight:0}}>
                            { i == 0 ?
                                <btn className="btn btn-default btn-xs" style={{float:'right'}} onClick={ev => btnClear(ev)}
                                     title="Clear all entries for this field">
                                    <span><span className="glyphicon glyphicon-remove-sign" aria-hidden="true"/> Clear </span>
                                </btn>
                                : false
                            }
                            <btn className="btn btn-default btn-xs" style={{float:'right'}} onClick={ev => btnAddRemove(ev, i)}
                                 title={(i == 0 ? "Add new entry" : "Remove this entry") + " for this field"}>
                                {i == 0 ?
                                    <span><span className="glyphicon glyphicon-plus-sign" aria-hidden="true"/> Add </span> :
                                    <span><span className="glyphicon glyphicon-minus-sign" aria-hidden="true"/> Remove </span>
                                }
                            </btn>
                            <hr style={{margin: '10px 5px 10px 0px', padding: '0px'}}/>
                        </div>
                    </div>
                </div> );
        } else if (schema.get('type') === 'object') {
            field = this.renderComplexField(schema, path);
        } else {
            field = this.renderScalarField(schema, path, buttons);
        }

        const pathstr = path.join('/');
        const isError = this.props.funcs.getError(pathstr);
        const onfocus = (e) => { this.setFieldDescription(path); e.stopPropagation(); }
        const onblur = () => { this.setFieldDescription(null); }
        const title = schema.get('title');
        const spath = path.slice((path.indexOf(this.props.schemaID) || -1) + 1)
        return (
            <div className="row" key={id}>
                <div style={{marginBottom:'0.5em'}}>
                    {!title ? false :
                        <label htmlFor={id} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                            <span style={{float:'right', color:isError?'red':'black'}}>
                                {title} {schema.get('isRequired') ? "*":""}
                            </span>
                        </label> }
                    <div className={"col-sm-" + (title ? "9" : "12") + (schema.get('type') == 'array' ? " field-array" : "")} onFocus={onfocus} onBlur={onblur}>
                        <div className="container-fluid" style={{paddingLeft:0, paddingRight:0}}>
                            {field}
                        </div>
                    </div>
                </div>
                <div className="col-sm-12 v-spacer"><input type="hidden" /></div>
                { spath.length == 1 &&
                <div className="col-sm-offset-3 col-sm-9">
                    <ReplaceAnimate>
                        <div className="field-description">
                            <p>{this.state.desc}</p>
                            {this.state.sdesc && <p>{this.state.sdesc}</p>}
                        </div>
                    </ReplaceAnimate>
                </div> }
            </div>
        );
    },

    getSchemaFieldDefinition(path, schema) {
        while (Number.isInteger(path[0])) {
            path = path.slice(1)
            if (schema.has('properties')) {
                schema = schema.get('properties');
            } else if (schema.has('items')) {
                schema = schema.get('items');
            }
        }
        var def = schema ? schema.get(path[0], schema) : null;
        if (def) {
            if (path.length < 2) {
                return def;
            } else if (def.get('type') == 'object') {
                return this.getSchemaFieldDefinition(path.slice(1), def.get('properties'));
            } else if (def.get('type') == 'array') {
                return this.getSchemaFieldDefinition(path.slice(1), def.get('items'));
            }
        }
        return null;
    },

    getFieldDescription(path) {
        var def = this.getSchemaFieldDefinition(path, this.props.schema);
        return def ? def.get('description') || "" : "";
    },

    setFieldDescription(path) {
        var desc = "", sdesc = "";
        if (path && path != null) {
            path = path.slice((path.indexOf(this.props.schemaID) || -1) + 1);
            sdesc = (sdesc = this.getFieldDescription(path)) ? "This subfield sets " + sdesc[0].toLowerCase() + sdesc.slice(1) : "";
            desc = path.length > 1 ? this.getFieldDescription(path.slice(0,1)) : "";
        }
        return this.setState({desc: desc, sdesc: sdesc, dirty: true});
    },

    render() {
        const datapath = this.props.schemaID ? ['community_specific', this.props.schemaID, this.props.id] : [this.props.id];
        const f = this.renderFieldTree(this.props.id, this.props.schema, datapath);
        if (!f) {
            return false;
        }
        return <div className="field-tree"> {f} </div>;
    }
});

const EditRecordBlock = React.createClass({
    getInitialState() {
        return {
            folds: true
        }
    },

    renderFieldBlock(schemaID, schema) {
        if (!schema) {
            return <Wait key={schemaID}/>;
        }

        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(schema, hiddenFields.concat(['dates', 'sizes', 'formats']));

        const majorFields = majors.entrySeq().map(([id, schema]) => <EditRecordFieldTree key={id} id={id} schemaID={schemaID} schema={schema} setLicenseModal={this.props.setModal } funcs={this.props.funcs} />);
        const minorFields = minors.entrySeq().map(([id, schema]) => <EditRecordFieldTree key={id} id={id} schemaID={schemaID} schema={schema} funcs={this.props.funcs} />);

        const onMoreDetails = e => {
            e.preventDefault();
            this.setState({folds:!this.state.folds});
        }

        const foldBlock = minorFields.count() ? (
            <div className="col-sm-12">
                <div className="row">
                    <div className="col-sm-offset-3 col-sm-9" style={{marginTop:'1em', marginBottom:'1em'}}>
                        <a href="#" onClick={onMoreDetails} style={{padding:'0.5em'}}>
                            { this.state.folds ?
                                <span>Show more details <span className="glyphicon glyphicon-chevron-right" style={{top:'0.1em'}} aria-hidden="true"/></span>:
                                <span>Hide details <span className="glyphicon glyphicon-chevron-down" style={{top:'0.2em'}} aria-hidden="true"/></span> }
                        </a>
                    </div>
                </div>
                <HeightAnimate delta={20}>
                    { !this.state.folds ? minorFields : false }
                </HeightAnimate>
            </div>
        ) : false;

        const blockStyle=schemaID ? {marginTop:'1em', paddingTop:'1em', borderTop:'1px solid #eee'} : {};
        return (
            <div style={blockStyle}>
                <div className="row">
                    <h3 className="col-sm-12" style={{marginBottom:0}}>
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

    render() {
        return this.renderFieldBlock(this.props.schemaID, this.props.schema);
    }
});

const EditRecord = React.createClass({
    getInitialState() {
        return {
            fileState: 'done',
            errors: {},
            dirty: false,
            waitingForServer: false,
            modal: false
        };
    },

    renderFileBlock() {
        const setState = (fileState, message) => {
            const errors = this.state.errors;
            if (fileState === 'done') {
                delete errors.files;
            } else if (fileState === 'error') {
                errors.files = message;
            } else {
                errors.files = 'Waiting for files to finish uploading';
            }
            this.setState({fileState, errors});
        }
        const files = this.props.record.get('files');
        if (files instanceof Error) {
            return <Err err={files}/>;
        }
        return (
            <EditFiles files={files ? files.toJS() : []}
                record={this.props.record}
                setState={setState}
                setModal={modal => this.setState({modal})} />
        );
    },

    setError(id, msg) {
        const err = this.state.errors;
        err[id] = msg;
        this.setState({errors: this.state.errors});
    },

    getError(pathstr) {
        return this.state.errors[pathstr]
    },

    getValue(path) {
        const r = this.state.record;
        if (!r) {
            return null;
        }
        let v = r.getIn(path);
        if (v != undefined && v != null && v.toJS) {
            v = v.toJS();
        }
        return v;
    },

    setValue(schema, path, value) {
        let r = this.state.record;
        if (!r) {
            return null;
        }
        if (schema === null) {
            schema = path[0] == 'community_specific' ? this.props.blockSchemas.get([0, 'json_schema']) : this.props.rootSchema;
        }
        if (value !== undefined) {
            var self = this;
            path.forEach((p, i) => {
                if (Number.isInteger(p)) {
                    console.assert(i > 0);
                    const subpath = path.slice(0, i);
                    const list = r.getIn(subpath);
                    if (!list || !list.size) {
                        r = r.setIn(subpath, List());
                    } else {
                        console.assert(p < 1000);
                        while (p >= list.count()) {
                            const x = Number.isInteger(path[i+1]) ? List() : Map();
                            const list2 = list.push(x);
                            r = r.setIn(subpath, list2);
                        }
                    }
                }
            });
            console.assert(!Array.isArray(value));
            if (typeof value === 'string' || value instanceof String) {
                value = value.replace(/^\s+/, '').replace(/(\s{2})\s+$/, '$1') ;
            }

            r = r.setIn(path, value);
            self.validateField(schema, path, value);
        } else {
            var p = [...path];
            while (l === undefined || !l.size) {
                r = r.deleteIn(p);
                p.pop();
                var l = r.getIn(p)
            }
            this.validateField(schema, path, value);
        }
        this.setState({record: r, dirty: true})
    },

    removeErrors(path) {
        var self = this;
        path.forEach((key) => {
            let matching = Object.keys(self.state.errors).filter(function(k) {
                    return ~k.indexOf(path)
                });
            matching.forEach((elem) => {
                delete self.state.errors[elem]
            });
        });
        this.setState({})
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(props) {
        if (props.record.size && !this.state.record) {
            let record = props.record.get('metadata');
            if (!record.has('community_specific')) {
                record = record.set('community_specific', Map());
            }
            this.state.record = addEmptyMetadataBlocks(record, props.blockSchemas) || record;
            this.setState({});
        } else if (this.state.record && props.blockSchemas) {
            const record = addEmptyMetadataBlocks(this.state.record, props.blockSchemas);
            if (record) {
                this.state.record = record;
                this.setState({});
            }
        }

        function addEmptyMetadataBlocks(record, blockSchemas) {
            if (!blockSchemas || !blockSchemas.length || !record) {
                return false;
            }
            let updated = false;
            blockSchemas.forEach(([blockID, _]) => {
                if (!record.get('community_specific').has(blockID)) {
                    record = record.setIn(['community_specific', blockID], Map());
                    updated = true;
                }
            });
            return updated ? record : null;
        }
    },

    validField(schema, value) {
        if (schema && schema.get('isRequired')) {
            if (!this.props.isDraft || this.isForPublication()) {
                // 0 is fine
                if (value === undefined || value === null || (""+value).trim() === "")
                    return false;
            }
        }
        return true;
    },

    validateField(schema, path, value) {
        // update errors
        const errors = this.state.errors;
        const pathstr = path.join('/');
        if (!this.validField(schema, value)) {
            errors[pathstr] = invalidFieldMessage(pathstr);
        } else {
            delete errors[pathstr];
        }
    },

    findValidationErrorsRec(errors, schema, path, value) {
        const isValue = (value !== undefined && value !== null && value !== "");
        if (schema.get('isRequired') && !isValue) {
            if (!this.props.isDraft || this.isForPublication()) {
                const pathstr = path.join("/");
                errors[pathstr] = invalidFieldMessage(pathstr);
                return;
            }
        }

        const newpath = (last) => { const np = path.slice(); np.push(last); return np; };
        const type = schema.get('type');
        if (type === 'array') {
            if (isValue && schema.get('items')) {
                value.forEach((v, i) =>
                    this.findValidationErrorsRec(errors, schema.get('items'), newpath(i), v));
            }
        } else if (type === 'object') {
            if (isValue && schema.get('properties')) {
                schema.get('properties').entrySeq().forEach(([pid, pschema]) =>
                    this.findValidationErrorsRec(errors, pschema, newpath(pid), value.get(pid)));
            }
        } else {
            this.validateField(schema, path, value);
        }
    },

    findValidationErrors() {
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas || [];
        if (!rootSchema) {
            return;
        }
        const errors = {};
        const r = this.state.record;

        this.findValidationErrorsRec(errors, rootSchema, [], r);
        blockSchemas.forEach(([blockID, blockSchema]) => {
            const schema = blockSchema.get('json_schema');
            const path = ['community_specific', blockID];
            this.findValidationErrorsRec(errors, schema, path, r.getIn(path));
        });

        if (this.state.errors.files) {
            errors.files = this.state.errors.files;
        }
        return errors;
    },

    updateRecord(event) {
        event.preventDefault();
        const errors = this.findValidationErrors();
        if (this.state.fileState !== 'done' || pairs(errors).length > 0) {
            this.setState({errors});
            return;
        }
        // always remove any existing errors displayed
        notifications.clearAll();
        // determine if there are any changes in the original and current record
        const original = this.props.record.get('metadata').toJS();
        const updated = this.state.record.toJS();
        const patch = compare(original, updated);
        if (!patch || !patch.length) {
            this.setState({dirty: false});
            return;
        }
        const afterPatch = (record) => {
            if (this.props.isDraft && !this.isForPublication()) {
                this.props.refreshCache();
                // TODO(edima): when a draft is published, clean the state of
                // records in versioned chain, to trigger a refetch of
                // versioning data
                this.setState({dirty: false, waitingForServer: false});
            } else {
                browser.gotoRecord(record.id);
            }
        }
        const onError = (xhr) => {
            this.setState({waitingForServer: false});
            onAjaxError(xhr);
            try {
                const errors = JSON.parse(xhr.responseText).errors;
                errors.map(err => {
                    notifications.warning(`Error in field '${err.field}': ${err.message}`);
                });
            } catch (_) {
            }
        }

        this.setState({waitingForServer: true});
        this.props.patchFn(patch, afterPatch, onError);
    },

    discardChanges(event) {
        event.preventDefault();
        if (confirm("Are you sure you discard all metadata changes to this record?")) {
            browser.gotoRecord(this.props.record.get('id'));
        }
    },

    isForPublication() {
        return this.state.record.get('publication_state') == 'submitted';
    },

    setPublishedState(e) {
        const state = e.target.checked ? 'submitted' : 'draft';
        const record = this.state.record.set('publication_state', state);
        this.setState({record});
    },

    renderUpdateRecordForm() {
        const klass = this.state.waitingForServer ? 'disabled' :
                      this.state.dirty ? 'btn-primary' : 'disabled';
        const dlass = this.state.waitingForServer || !this.state.dirty ? 'disabled' : '';
        const text = this.state.waitingForServer ? "Updating record, please wait...":
                     this.state.dirty ? "Update record" : "The record is up to date";
        const icon = this.state.waitingForServer ? 'time' :
                      this.isForPublication() ? 'send' :
                      this.state.dirty ? 'floppy-disk' : 'ok';
        return (
            <div className="col-sm-offset-3 col-sm-9">
                <p>This record is already published. Any changes you make will be directly visible to other people.</p>
                <div className="row buttons">
                    <div className="col-sm-9">
                        <button type="submit" className={"btn btn-default btn-block " + klass} onClick={this.updateRecord}><i className={"glyphicon glyphicon-" + icon}/>&nbsp;&nbsp;{text}</button>
                    </div>
                    <div className="col-sm-3">
                        <button type="submit" className={"btn btn-default discard " + dlass} onClick={this.discardChanges}><i className="glyphicon glyphicon-remove"/>&nbsp;Discard Changes</button>
                    </div>
                </div>
            </div>
        );
    },

    renderSubmitDraftForm() {
        const klass = this.state.waitingForServer ? 'disabled' :
                      this.isForPublication() ? 'btn-primary btn-danger' :
                      this.state.dirty ? 'btn-primary' : 'disabled';
        const dlass = this.state.waitingForServer || !this.state.dirty ? 'disabled' : '';
        const text = this.state.waitingForServer ? "Updating record, please wait..." :
                      this.isForPublication() ? 'Save and Publish' :
                      this.state.dirty ? 'Save Draft' : 'The draft is up to date';
        const icon = this.state.waitingForServer ? 'time' :
                      this.isForPublication() ? 'send' :
                      this.state.dirty ? 'floppy-disk' : 'ok';
        const future_doi = this.props.record.get('metadata', Map()).get('$future_doi', '') || "";
        return (
            <div className="col-sm-offset-3 col-sm-9">
                <label>
                    <input type="checkbox" value={this.isForPublication} onChange={this.setPublishedState}/>
                    {" "}Submit draft for publication
                </label>
                <p>When the draft is published it will be assigned a PID and a DOI, making it publicly citable.
                    Please note that the published record's files can no longer be modified by its owner. </p>
                { future_doi ?
                    <p>This publication will get the following DOI: <PersistentIdentifier pid={future_doi}/></p>
                  : false
                }
                <div className="row buttons">
                    <div className="col-sm-9">
                        <button type="submit" className={"btn btn-default btn-block " + klass} onClick={this.updateRecord}><i className={"glyphicon glyphicon-" + icon}/>&nbsp;&nbsp;{text}</button>
                    </div>
                    <div className="col-sm-3">
                        <button type="submit" className={"btn btn-default btn-block discard " + dlass} onClick={this.discardChanges}><i className="glyphicon glyphicon-remove"/>&nbsp;Discard Changes</button>
                    </div>
                </div>
            </div>
        );
    },

    removeDraft(e) {
        e.preventDefault();
        if (confirm("Are you sure you want to delete this draft record?\n\nThis cannot be undone!")) {
            serverCache.removeDraft(this.props.record.get('id'), browser.gotoProfile());
        }
    },

    getChildFuncs() {
        return {
            setValue: this.setValue,
            getValue: this.getValue,
            setError: this.setError,
            getError: this.getError,
            removeErrors: this.removeErrors
        }
    },

    render() {
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas;
        if (!this.props.record || !rootSchema) {
            return <Wait/>;
        }
        const editTitle = "Editing " + (this.props.isDraft ? "draft" : "record") + (this.props.isVersion ?  " version": "");
        return (
            <div className="edit-record">
                { this.state.modal &&
                <div style={{position:'absolute', width:'100%', zIndex: 1}}>
                    { this.state.modal }
                </div> }
                <Versions isDraft={this.props.isDraft}
                          recordID={this.props.record.get('id')}
                          versions={this.props.record.get('versions')}
                          editing={true}/>

                <div className="row">
                    <div className="col-xs-12">
                        <h2 className="name">
                            <span style={{color:'#aaa'}}>{editTitle}</span>
                            {this.state.record.get('title')}
                        { this.props.isDraft &&
                            <div className="pull-right">
                                <form className="form-inline" onSubmit={this.removeDraft}>
                                    <button className="btn btn-default" type="submit">
                                        <i className="fa fa-trash-o"></i> Delete draft
                                    </button>
                                </form>
                            </div>
                        }
                        </h2>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-12">
                        { this.props.isDraft && this.renderFileBlock() }
                    </div>
                    <div className="col-xs-12">
                        <form className="form-horizontal" onSubmit={this.updateRecord}>
                            <EditRecordBlock key={"root"} schemaID={null} schema={rootSchema} funcs={this.getChildFuncs()} setModal={s => { this.setState(s)}} />
                            { blockSchemas.map(([id, schema]) =>
                                <EditRecordBlock setModal={s => this.setState(s)} key={id} schemaID={id} schema={(schema||Map()).get('json_schema')} funcs={this.getChildFuncs()} />) }
                        </form>
                    </div>
                </div>
                <div className="row">
                    <div className="form-group submit">
                        { pairs(this.state.errors).map( ([id, msg]) =>
                            <div className="col-sm-offset-3 col-sm-9 alert alert-warning" key={id}>{msg} </div>) }
                        { this.props.isDraft ? this.renderSubmitDraftForm() : this.renderUpdateRecordForm() }
                    </div>
                </div>
            </div>
        );
    }
});
