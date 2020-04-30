import React from 'react/lib/ReactWithAddons';
import { OrderedMap } from 'immutable';
import { Link } from 'react-router'
import { serverCache, Error } from '../data/server';
import { PersistentIdentifier } from './editfiles.jsx';
import { Wait, Err } from './waiting.jsx';

const except = {'$schema':true, 'community_specific':true, 'owner':true,
                '_internal':true, '_deposit':true, '_files':true,
                '_pid':true, '_oai':true, 'publication_state': true};

export function getSchemaOrderedMajorAndMinorFields(schema) {
    if (!schema) {
        return [];
    }
    const presentation = schema.getIn(['b2share', 'presentation']);
    const properties = schema.get('properties');

    const majorIDs = presentation && presentation.get('major') ?
        presentation.get('major').filter(id => properties.get(id)) : null;
    const minorIDs = presentation && presentation.get('minor') ?
        presentation.get('minor').filter(id => properties.get(id)) : null;

    let minors = OrderedMap(minorIDs ? minorIDs.map(id => [id, properties.get(id)]) : []);
    let majors = OrderedMap(majorIDs ? majorIDs.map(id => [id, properties.get(id)]) : []);

    properties.entrySeq().forEach(([id, p]) => {
        if (!majors.has(id) && !minors.has(id) && !except.hasOwnProperty(id)) {
            majors = majors.set(id, p);
        }
    });

    return [majors, minors];
};

export const Schema = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderSchema([id, schema]) {
        const requiredClass = schema.get('isRequired') ? "required property" : "";

        const type = schema.get('type');
        const title = schema.get('title');
        const description = schema.get('description');
        let inner = null;

        if (type === 'array') {
            inner = (
                <ul className="list-unstyled field-array">
                    {this.renderSchema([null, schema.get('items')])}
                </ul>
            );
        } else if (type === 'object') {
            inner = (
                <ul className="list-unstyled">
                    { schema.get('properties').entrySeq().map(this.renderSchema) }
                </ul>
            );
        } else if (schema.get('enum')) {
            const e = schema.get('enum').toJS();
            inner = (<span className="mono-style">enum [{e.join(', ')}]</span>);
        } else {
            inner = type;
            if (schema.get('format')) {
                inner += " [" + schema.get('format') + "]";
            }
            inner = <span className="mono-style">{inner}</span>
        }

        return (
            <li key={id} className="row field-general">
                <div className="col-sm-6">
                    <p className={"schema-field " + requiredClass}>
                        <span>{title}</span>
                        <span>{schema.get('unit') ? ' (' + schema.get('unit') + ')' : false }</span>
                        <span className="mono-style">
                            {title ? " :: " : ""}
                            {id}
                            {schema.get('isRequired') ? " (required)" : false}
                        </span>
                    </p>
                    <p> {schema.get('description')} </p>
                </div>
                <div className="col-sm-6"> {inner} </div>
            </li>
        );
    },

    render() {
        const schema = this.props.schema;
        if (!schema) {
            return <Wait/>;
        }
        const jschema = schema.get('json_schema');
        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(jschema);
        return (
            <div className="schema">
                <div className="row">
                    <div className="col-sm-12">
                        <h3 className="title">{jschema.get('title') || "Metadata fields"}</h3>
                        <p className="description">{jschema.get('description')}</p>
                        { !this.props.id ? false :
                            <p className="pid">
                                <span>Block schema identifier: </span>
                                <PersistentIdentifier pid={this.props.id}/>
                            </p>
                        }
                    </div>
                </div>
                <ul className="list-unstyled">
                    { majors.entrySeq().map(this.renderSchema) }
                    { minors.entrySeq().map(this.renderSchema) }
                </ul>
            </div>
        );
    }
});
