import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';


export function getType(property) {
    const isArray = property.get('type') === 'array';
    if (!isArray) {
        return {
            isArray: false,
            type: property.get('type'),
            format: property.get('format'),
        }
    }

    const items = property.get('items');
    if (items) {
        const t = getType(items);
        return {
            isArray: true,
            type: t.type,
            format: t.format,
        }
    }
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
        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">
                        <h4 className="title">{jschema.get('title')}</h4>
                        <p className="description">{jschema.get('description')}</p>
                    </div>
                </div>
                { jschema.get('properties').entrySeq().map(this.renderProperty) }
            </div>
        );
    }
});
