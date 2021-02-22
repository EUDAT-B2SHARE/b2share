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

    renderSchema([id, schema], depth=0) {
        const requiredClass = schema.get('isRequired') ? "required property":"";

        const type = schema.get('type');
        const title = schema.get('title');
        const description = schema.get('description');
        let inner = null;

        if (type === 'array') {
            inner = (
                <ul className="list-unstyled field-array">
                    { this.renderSchema([null, schema.get('items')], depth) }
                </ul>
            );
        } else if (type === 'object') {
            inner = (
                <ul className="list-unstyled">
                    { schema.get('properties').entrySeq()
                                .sort(([id, fschema]) => { return !fschema.get('isRequired'); })
                                .map(field => this.renderSchema(field, depth+1)) }
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

        const leftwidth = 12 / (this.columnCount - depth);
        const leftcolumn = !id ? false :
            <div className={"col-sm-" + leftwidth}>
                <p className={requiredClass}>
                    <span className="bold">{title}</span>
                    <span className="mono-style">
                        {title?" :: ":""}
                        {id}
                        {schema.get('isRequired') ? " (required)":false}
                    </span>
                </p>
                <p> {schema.get('description')} </p>
            </div>;
        const rightcolumnsize = leftcolumn ? "col-sm-" + (12 - leftwidth) : "col-sm-12";
        return (
            <li key={id} className="row field-general">
                {leftcolumn}
                <div className={rightcolumnsize}> {inner} </div>
            </li>
        );
    },

    determineColumnCount(schema, count=1) {
        var fcount = count;
        [['properties'], ['items', 'properties']].forEach(t => {
            if (schema.getIn(t)) {
                schema.getIn(t).forEach(field => {
                    fcount = Math.max(fcount, this.determineColumnCount(field, count+1));
                });
            }
        });
        return Math.max(fcount, count);
    },

    render() {
        const schema = this.props.schema;
        if (!schema) {
            return <Wait/>;
        }
        const jschema = schema.get('json_schema');
        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(jschema);

        this.columnCount = this.determineColumnCount(jschema);
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
                    { majors.entrySeq().map(field => this.renderSchema(field, 0)) }
                    { minors.entrySeq().map(field => this.renderSchema(field, 0)) }
                </ul>
            </div>
        );
    }
});
