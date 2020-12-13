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
        const community = serverCache.getCommunity(record.getIn(['metadata', 'community']));
        if (community instanceof Error) {
            return <Err err={community}/>;
        }
        return (
            <ReplaceAnimate>
                <EditRecord record={record} community={community}
                            rootSchema={rootSchema} blockSchemas={blockSchemas}
                            refreshCache={this.refreshCache}
                            patchFn={this.patchRecordOrDraft}
                            isDraft={this.isDraft} isVersion={true} />
            </ReplaceAnimate>
        );
    }
});


const EditRecord = React.createClass({
    getInitialState() {
        return {
            record: null,
            fileState: 'done',
            modal: null,
            errors: {},
            dirty: false,
            waitingForServer: false,
            opened: []
        };
    },

    addFieldButton(buttons, pathstr, name) {
        if (!(pathstr in buttons)) {
            buttons[pathstr] = []
        }
        buttons[pathstr].push(name)
        buttons[pathstr] = buttons[pathstr].filter((v, i, a) => a.indexOf(v) === i);
        return buttons;
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
        for (let i = 0; i < path.length; ++i) {
            const el = path[i];
            if (Number.isInteger(el)) {
                console.assert(i > 0);
                const subpath = path.slice(0, i);
                const list = r.getIn(subpath);
                if (!list) {
                    r = r.setIn(subpath, List());
                } else {
                    console.assert(el < 1000);
                    while (el >= list.count()) {
                        const x = Number.isInteger(path[i+1]) ? List() : Map();
                        const list2 = list.push(x);
                        r = r.setIn(subpath, list2);
                    }
                }
            }
        }
        console.assert(!Array.isArray(value));
        if(typeof value === 'string' || value instanceof String) {
            value = value.replace(/^\s+/, '').replace(/(\s{2})\s+$/, '$1') ;
        }

        r = value !== undefined ? r.setIn(path, value) : r.deleteIn(path);
        const errors = this.state.errors;
        const pathstr = path.join('/');
        if (!this.validField(schema, value)) {
            errors[pathstr] = invalidFieldMessage(pathstr);
        } else {
            delete errors[pathstr];
        }
        this.setState({record:r, errors, dirty:true});
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
            this.setState({opened: opened});
        };

        const onSelectLicense = (license) => {
            console.assert(path.length >= 1);
            const licenseData = {
                'license': license.name,
                'license_uri': license.url,
            };
            this.setValue(schema, path.slice(0, -1), fromJS(licenseData));
        };

        const buttons = {
            details: {'title': 'Show details for this field or entry', 'event': btnShowFieldDetails, 'icon': 'glyphicon-list-alt'}
        }

        let field = false;
        let event = null;
        switch (buttonname) {
            case 'license':
                return <SelectLicense title="Select License" onSelect={onSelectLicense} setModal={modal => this.setState({modal})} key={pathstr + "-" + buttonname} />
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

    renderScalarField(schema, path, buttons={}, options={}) {
        const onDateChange = (date) => {
            const m = moment(date);
            this.setValue(schema, path, m.isValid() ? m.toISOString() : undefined);
        }

        const onEmbargoDateChange = date => {
            const m = moment(date);
            // true if embargo is in the past
            const access = m.isValid() ? (moment().diff(m) > 0) : true;
            this.state.record = this.state.record.set('open_access', access);
            // setValue will call setState
            onDateChange(m)
        };

        const pathstr = path.join('/');
        if (pathstr in buttons) {
            return this.renderButtonedScalarField(schema, path, buttons[pathstr]);
        }

        const newpath = (last) => { const np = path.slice(); np.push(last); return np; };

        if (path.slice(-1)[0] == 'language') {
            const languages = serverCache.getLanguages();
            return (languages instanceof Error) ? <Err err={languages}/> :
                <SelectBig data={languages}
                    onSelect={x=>this.setValue(schema, path, x)} value={this.getValue(path)} />;
        } else if (path.slice(-1)[0] == 'discipline_name') {
            const disciplines = serverCache.getDisciplines();
            return (disciplines instanceof Error) ? <Err err={disciplines}/> :
                <SelectBig data={disciplines}
                    onSelect={x=>this.setValue(schema, path, x)} value={this.getValue(path)} />;
        }

        const validClass = (this.state.errors[pathstr]) ? " invalid-field " : "";
        const type = schema.get('type');
        const format = schema.get('format') || "";
        const value = this.getValue(path);
        const setter = x => this.setValue(schema, path, x);
        if (type === 'boolean') {
            return (
                <div style={{lineHeight:"30px"}}>
                    <div className={validClass} style={{lineHeight:"30px"}}>
                        <Toggle checked={value} onChange={event => setter(event.target.checked)} disabled={options['disabled'] || false} />
                        <div style={{display:"inline", "verticalAlign":"super"}}>{value ? " True" : " False"}</div>
                    </div>
                </div>
            );
        } else if (type === 'integer') {
            return <NumberPicker className={validClass} defaultValue={value} onChange={setter} />
        } else if (type === 'number') {
            return <NumberPicker className={validClass} defaultValue={value} onChange={setter} />
        } else if (type === 'string') {
            const value_str = ""+(value || "");
            if (schema.get('enum')) {
                return <DropdownList className={validClass} value={value_str} data={schema.get('enum').toJS()} onChange={setter} />
            } else if (['date-time', 'date'].includes(format)) {
                const initial = (value_str && value_str !== "") ? moment(value_str).toDate() : null;
                return <DateTimePicker className={validClass} time={format == 'date-time'} defaultValue={initial}
                        onChange={path == 'embargo_date' ? onEmbargoDateChange : onDateChange} />
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
        } else if (schema.get('enum')) {
            const value_str = ""+(value || "");
            return <DropdownList className={"form-control"+ validClass} data={schema.get('enum').toJS()}
                     value={value_str} onChange={setter} />
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
            field = this.props.community ? renderSmallCommunity(this.props.community) : <Wait/>
        } else if (objEquals(path, ['license', 'license'])) {
            field = this.renderScalarField(schema, path, this.addFieldButton(buttons, path.join('/'), 'license'));
        } else if (objEquals(path, ['open_access'])) {
            const embargo = this.getValue(schema, newpath('embargo_date'));
            const disabled = embargo && moment(embargo).isValid();
            field = this.renderScalarField(schema, path, {}, {disabled: disabled});
        } else if (schema.get('type') === 'array') {
            const itemSchema = schema.get('items');
            const raw_values = this.getValue(path);
            const len = (raw_values && raw_values.length) || 1;
            const arrField = [...Array(len).keys()].map(i =>
                this.renderFieldTree(id+`[${i}]`, itemSchema, newpath(i)));
            const btnAddRemove = (ev, pos) => {
                ev.preventDefault();
                if (pos === 0) {
                    const itemType = itemSchema.get('type');
                    const values = this.state.record.getIn(path) || List();
                    const newItem = itemType === 'array' ? List() : itemType === 'object' ? Map() : null;
                    let newValues = values.push(newItem);
                    if (newValues.count() == 1) {
                        // added value starting from an empty container; 2 values needed
                        newValues = newValues.push(newItem);
                    }
                    this.setValue(schema, path, newValues);
                } else {
                    this.setValue(schema, newpath(pos), undefined);
                }
            }
            const btnClear = (ev) => {
                ev.preventDefault();
                this.removeErrors(path);
                this.setValue(schema, path, undefined);
            }
            field = arrField.map((f, i) =>
                <div className="container-fluid" key={id+`[${i}]`}>
                    <div className="row" key={i} style={{marginBottom:'0.5em'}}>
                        {f}
                        <div className={"col-sm-offset-9 col-sm-3"} style={{paddingRight:0}}>
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
                        </div>
                    </div>
                </div> );
        } else if (schema.get('type') === 'object') {
            field = this.renderComplexField(schema, path);
        } else {
            field = this.renderScalarField(schema, path, buttons);
        }

        const arrstyle = schema.get('type') !== 'array' ? {} : {
            paddingLeft:'10px',
            borderLeft:'1px solid black',
            borderRadius:'4px',
        };
        const pathstr = path.join('/');
        const isError = this.state.errors.hasOwnProperty(pathstr);
        const onfocus = () => { this.setState({showhelp: path.slice()}); }
        const onblur = () => { this.setState({showhelp: null}); }
        const title = schema.get('title');
        return (
            <div className="row" key={id}>
                <div key={id} style={{marginBottom:'0.5em'}} title={schema.get('description')}>
                    {!title ? false :
                        <label htmlFor={id} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>
                            <span style={{float:'right', color:isError?'red':'black'}}>
                                {title} {schema.get('isRequired') ? "*":""}
                            </span>
                        </label> }
                    <div className={title ? "col-sm-9":"col-sm-12"} style={arrstyle} onFocus={onfocus} onBlur={onblur}>
                        <div className="container-fluid" style={{paddingLeft:0, paddingRight:0}}>
                            {field}
                        </div>
                    </div>
                </div>
                <div className="col-sm-offset-3 col-sm-9">
                    <HeightAnimate>
                        { this.state.showhelp && objEquals(this.state.showhelp, path) ?
                            <div style={{marginLeft:'1em', paddingLeft:'1em', borderLeft: '1px solid #eee'}}>
                                <p> {schema.get('description')} </p>
                            </div>
                          : false }
                    </HeightAnimate>
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

        function renderBigFieldTree([pid, pschema]) {
            const datapath = schemaID ? ['community_specific', schemaID, pid] : [pid];
            const f = this.renderFieldTree(pid, pschema, datapath);
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
        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(schema, hiddenFields.concat(['dates', 'sizes', 'formats']));

        const majorFields = majors.entrySeq().map(renderBigFieldTree.bind(this));
        const minorFields = minors.entrySeq().map(renderBigFieldTree.bind(this));

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
                            { !open ?
                                <span>Show more details <span className="glyphicon glyphicon-chevron-right" style={{top:'0.1em'}} aria-hidden="true"/></span>:
                                <span>Hide details <span className="glyphicon glyphicon-chevron-down" style={{top:'0.2em'}} aria-hidden="true"/></span> }
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

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(props) {
        if (props.record && !this.state.record) {
            let record = props.record.get('metadata');
            if (!record.has('community_specific')) {
                record = record.set('community_specific', Map());
            }
            record = addEmptyMetadataBlocks(record, props.blockSchemas) || record;
            this.setState({record});
        } else if (this.state.record && props.blockSchemas) {
            const record = addEmptyMetadataBlocks(this.state.record, props.blockSchemas);
            if (record) {
                this.setState({record});
            }
        }

        function addEmptyMetadataBlocks(record, blockSchemas) {
            if (!blockSchemas || !blockSchemas.length) {
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
            if (!this.validField(schema, value)) {
                const pathstr = path.join("/");
                errors[pathstr] = invalidFieldMessage(pathstr);
            }
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
        const original = this.props.record.get('metadata').toJS();
        const updated = this.state.record.toJS();
        const patch = compare(original, updated);
        if (!patch || !patch.length) {
            this.setState({dirty:false});
            return;
        }
        const afterPatch = (record) => {
            if (this.props.isDraft && !this.isForPublication()) {
                this.props.refreshCache();
                // TODO(edima): when a draft is publised, clean the state of
                // records in versioned chain, to trigger a refetch of
                // versioning data
                this.setState({dirty:false, waitingForServer: false});
                notifications.clearAll();
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
                    <div className="col-sm-10">
                        <button type="submit" className={"btn btn-default btn-block " + klass} onClick={this.updateRecord}><i className={"glyphicon glyphicon-" + icon}/>&nbsp;&nbsp;{text}</button>
                    </div>
                    <div className="col-sm-2">
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
                    <div className="col-sm-10">
                        <button type="submit" className={"btn btn-default btn-block " + klass} onClick={this.updateRecord}><i className={"glyphicon glyphicon-" + icon}/>&nbsp;&nbsp;{text}</button>
                    </div>
                    <div className="col-sm-2">
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

    render() {
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas;
        if (!this.state.record || !rootSchema) {
            return <Wait/>;
        }
        const editTitle = "Editing " + (this.props.isDraft ? "draft" : "record") + (this.props.isVersion ?  " version": "");
        return (
            <div className="edit-record">
                <Versions isDraft={this.props.isDraft}
                          recordID={this.props.record.get('id')}
                          versions={this.props.record.get('versions')}
                          editing={true}/>

                <div className="row">
                    <div className="col-xs-12">
                        <h2 className="name">
                            <span style={{color:'#aaa'}}>{editTitle}</span>
                            {this.state.record.get('title')}
                        { this.props.isDraft
                          ?
                            <div className="pull-right">
                                <form className="form-inline" onSubmit={this.removeDraft}>
                                    <button className="btn btn-default" type="submit">
                                        <i className="fa fa-trash-o"></i> Delete draft
                                    </button>
                                </form>
                            </div>
                          : false
                        }
                        </h2>
                    </div>
                </div>
                <div style={{position:'relative', width:'100%'}}>
                    <div style={{position:'absolute', width:'100%', zIndex:1}}>
                        { this.state.modal }
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-12">
                        { this.props.isDraft ? this.renderFileBlock() : false }
                    </div>
                    <div className="col-xs-12">
                        <form className="form-horizontal" onSubmit={this.updateRecord}>
                            { this.renderFieldBlock(null, rootSchema) }

                            { !blockSchemas ? false :
                                blockSchemas.map(([id, blockSchema]) =>
                                    this.renderFieldBlock(id, (blockSchema||Map()).get('json_schema'))) }
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
