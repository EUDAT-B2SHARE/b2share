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
        const arrayStyle = {
            marginLeft: '5px',
            paddingLeft:'10px',
            borderLeft:'1px solid black',
            borderRadius:'4px',
        };
        const generalStyle = {
            marginTop: '0.5em',
            marginBottom: '0.5em',
            paddingTop: '0.5em',
            paddingBottom: '0.5em',
        };
        const requiredClass = schema.get('isRequired') ? "required property":"";
        const monoStyle = {fontFamily:'monospace'};

        const type = schema.get('type');
        const title = schema.get('title');
        const description = schema.get('description');
        let inner = null;

        if (type === 'array') {
            inner = (
                <ul className="list-unstyled" style={arrayStyle}>
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
            inner = (<span style={monoStyle}>enum [{e.join(', ')}]</span>);
        } else {
            inner = type;
            if (schema.get('format')) {
                inner += " [" + schema.get('format') + "]";
            }
            inner = <span style={monoStyle}>{inner}</span>
        }

        const leftcolumn = !id ? false :
            <div className="col-sm-6">
                <p className={requiredClass}>
                    <span style={{fontWeight:'bold'}}>{title}</span>
                    <span style={{fontFamily:'monospace'}}>
                        {title?" :: ":""}
                        {id}
                        {schema.get('isRequired') ? " (required)":false}
                    </span>
                </p>
                <p> {schema.get('description')} </p>
            </div>;
        const rightcolumnsize = leftcolumn ? "col-sm-6" : "col-sm-12";
        return (
            <li key={id} className="row" style={generalStyle}>
                {leftcolumn}
                <div className={rightcolumnsize}> {inner} </div>
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
            <div style={{margin:'2em 0'}}>
                <div className="row">
                    <div className="col-sm-12">
                        <h3 className="title">{jschema.get('title') || "Metadata"}</h3>
                        <p className="description">{jschema.get('description')}</p>
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

