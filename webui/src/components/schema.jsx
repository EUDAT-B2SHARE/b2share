import React from 'react';
import { Link } from 'react-router'
import { server } from '../data/server';
import { Wait } from './waiting.jsx';


export const Schema = React.createClass({
    mixins: [React.PureRenderMixin],

    getType(p) {
        let type = p.get('type');
        if (type === 'array') {
            const etype = p.getIn(['items', 'type']);
            if (etype) {
                type += '<'+ etype + '>';
            }
        }
        return type;
    },

    renderProperty([id, p]) {
        return (
            <div key={id} className="row">
                <div className="col-sm-12">
                    <span style={{fontWeight:'bold'}}> {p.get('title')} </span>
                    <span style={{fontFamily:'monospace'}}> {this.getType(p)}  </span>
                    {p.get('description')}
                </div>
            </div>
        );
    },

    render() {
        const schema = this.props.schema;
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-12">
                        <h4 className="title">{schema.get('title')}</h4>
                        <p className="description">{schema.get('description')}</p>
                    </div>
                </div>
                { schema.get('properties').entrySeq().map(this.renderProperty) }
            </div>
        );
    }
});
