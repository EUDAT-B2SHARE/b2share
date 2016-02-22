import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { server } from '../data/server';
import { Wait } from './waiting.jsx';


export const MetadataBlock = React.createClass({
    mixins: [React.PureRenderMixin],

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



// TODO: use these examples to guide the rendering the metadata
const examples = {
    fields: {
        "description": {
            "title": "Description",
            "description": "The record abstract.",
            "type": "string",
        },
       'authors': {
            'title': 'Authors',
            'description': 'Authors...',
            "type": "array",
            "items": { "type": "string" },
            "uniqueItems": true,
        },
       'keywords': {
            'title': 'Keywords',
            'description': 'Keywords...',
            "type": "array",
            "minItems": 2,
            "maxItems": 5,
            "items": { "type": "string" },
            "uniqueItems": true,
        },
        'open_access': {
            'title': 'Open Access',
            'description': 'Indicate whether the resource is open or access is restricted.',
            'type': 'boolean',
        },
        'embargo_date': {
            'title': 'Embargo Date',
            'description': 'Date that the embargo will expire.',
            'type': 'string',
            'format': 'date-time',
            'default': Date.now(),
        },
        'contact_email': {
            'title': 'Contact Email',
            'description': 'The email of the contact person for this record.',
            'type': 'string',
            'format': 'email',
        },
    },
    "b2share": {
        "plugins": {
            'language': 'language_chooser',
            'licence': 'licence_chooser',
            'discipline': 'discipline_chooser',
        },
        "overwrite": {
            "language_code": { "http://b2share.eudat.eu/schemas/B2SHARE+Basic+Optional+Schema": [ "language" ] },
            "resource_type": { "http://b2share.eudat.eu/schemas/B2SHARE+Basic+Optional+Schema": [ "resource_type" ] },
        }
    },
}
