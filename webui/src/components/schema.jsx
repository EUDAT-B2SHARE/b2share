import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';


export const Schema = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    getType(p) {
        let type = p.get('type') || "";
        if (type === 'array') {
            const items = p.get('items');
            if (items) {
                const itemType = this.getType(items);
                if (itemType) {
                    type += '<'+ itemType + '>';
                }
            }
        }
        const format = p.get('format');
        if (format) {
            type += " ["+format+"]";
        }
        return type;
    },

    renderProperty([id, p]) {
        const title = p.get('title') || id;
        return (
            <div key={id} className="row" style={{marginTop:'1em'}}>
                <div className="col-sm-3">
                    <span style={{fontWeight:'bold'}}> {title} </span>
                </div>
                <div className="col-sm-3">
                    <span style={{fontFamily:'monospace'}}> {this.getType(p)}  </span>
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
