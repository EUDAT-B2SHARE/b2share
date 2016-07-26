import React from 'react/lib/ReactWithAddons';
import { OrderedMap } from 'immutable';
import { Link } from 'react-router'
import { serverCache, Error } from '../data/server';
import { Wait, Err } from './waiting.jsx';

const except = {'$schema':true, 'community_specific':true, 'owner':true,
                '_internal':true, '_deposit':true, '_files':true,
                '_pid':true, '_oai':true, 'publication_state': true, };

export function getSchemaOrderedMajorAndMinorFields(schema) {
    if (!schema) {
        return [];
    }
    const presentation = schema.getIn(['b2share', 'presentation']);
    const properties = schema.get('properties');

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

    return [majors, minors];
};

export function getType(property, propertyID, schema) {
    let ret = null;
    // console.log(property);
    const isArray = property.get('type') === 'array';
    if (!isArray) {
        ret = {
            isArray: false,
            type: property.get('type'),
            format: property.get('format'),
            enum: property.get('enum'),
        }
    } else {
        const items = property.get('items');
        if (items) {
            const t = getType(items);
            ret = {
                isArray: true,
                type: t.type,
                format: t.format,
                enum: t.enum,
            }
        }
    }
    if (schema && schema.get('required')) {
        const index = schema.get('required').keyOf(propertyID);
        if (index !== undefined) {
            ret.required = true;
        }
    }
    return ret;
}


export const Schema = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderProperty(schema, [id, p]) {
        const title = p.get('title') || id;
        const type = getType(p, id, schema);
        let typeString = type.type;
        if (type.format) {
            typeString = " ["+type.format+"]";
        }
        if (type.isArray) {
            typeString = 'array <'+typeString+'>';
        }
        if (type.required) {
            typeString += ' (required)';
        }
        return (
            <div key={id} className="row" style={{marginTop:'1em'}}>
                <div className="col-sm-3">
                    <span style={{fontWeight:'bold'}}> {title} </span>
                </div>
                <div className="col-sm-3">
                    <span style={{fontFamily:'monospace'}}> {typeString} </span>
                </div>
                <div className="col-sm-6">
                    {p.get('description')}
                </div>
            </div>
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
            <div style={{margin:'2em 0'}}>
                <div className="row">
                    <div className="col-sm-12">
                        <h3 className="title">{jschema.get('title') || "Metadata"}</h3>
                        <p className="description">{jschema.get('description')}</p>
                    </div>
                </div>
                { majors.entrySeq().map(this.renderProperty.bind(this, jschema)) }
                { minors.entrySeq().map(this.renderProperty.bind(this, jschema)) }
            </div>
        );
    }
});

