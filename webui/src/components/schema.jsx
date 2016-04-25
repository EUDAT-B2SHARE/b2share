import React from 'react/lib/ReactWithAddons';
import { OrderedMap } from 'immutable';
import { Link } from 'react-router'
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';


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

    const except = {'$schema':true, 'community_specific':true, '_internal':true};
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

export function getType(property) {
    let ret = null;
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
    return ret;
}


export const Schema = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    getTypeString(property) {
        const t = getType(property);
        const s = t.type + (t.format ? (" ["+t.format+"]"):'');
        return t.isArray ? ('array <'+s+'>') : s;
    },

    renderProperty([id, p]) {
        const title = p.get('title') || id;
        return (
            <div key={id} className="row" style={{marginTop:'1em'}}>
                <div className="col-sm-3">
                    <span style={{fontWeight:'bold'}}> {title} </span>
                </div>
                <div className="col-sm-3">
                    <span style={{fontFamily:'monospace'}}> {this.getTypeString(p)}  </span>
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
        console.log('schema', schema.toJS());
        const jschema = schema.get('json_schema');
        const [majors, minors] = getSchemaOrderedMajorAndMinorFields(jschema);
        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">
                        <h4 className="title">{jschema.get('title')}</h4>
                        <p className="description">{jschema.get('description')}</p>
                    </div>
                </div>
                { majors.entrySeq().map(this.renderProperty) }
                { minors.entrySeq().map(this.renderProperty) }
            </div>
        );
    }
});

