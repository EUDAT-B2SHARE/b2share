import React from 'react';
import { Link } from 'react-router'
import { server } from '../data/server';
import { Wait } from './waiting.jsx';


export const CommunityListPage = React.createClass({
    componentWillMount() {
        server.fetchCommunities();
        this.binding = this.props.store.branch('communities');
    },

    render() {
        return this.binding.valid() ?
            <CommunityList communities={this.binding.get()} /> :
            <Wait/>;
    }
});


export const CommunityPage = React.createClass({
    componentWillMount() {
        server.fetchCommunities();
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(nextProps) {
        const { id } = nextProps.params; // community id or name
        server.fetchCommunitySchemas(id);
        const findFn = (x) => x.get('id') == id || x.get('name') == id;
        this.binding = nextProps.store.branch('communities').find(findFn);
    },

    render() {
        if (this.binding.valid()) window.comm = this.binding.get();
        return this.binding.valid() ?
            <Community community={this.binding.get()} /> :
            <Wait/>;
    }
});


const CommunityList = React.createClass({
    mixins: [React.PureRenderMixin],

    renderCommunity(community) {
        const desc = community.get('description') || "";
        return (
            <div className="col-sm-6" key={community.get('id')}>
                <Link to={"/communities/"+community.get('name')}>
                    <div className="community link">
                        <h3 className="name">{community.get('name')}</h3>
                        <h4 className="domain">{community.get('domain')}</h4>
                        <img className="logo" src={community.get('logo')}/>
                        <p className="description"> {desc.substring(0,200)} </p>
                    </div>
                </Link>
            </div>
        );
    },

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>Communities</h1>

                        <div className="container-fluid">
                        <div className="row">
                            { this.props.communities.map(this.renderCommunity) }
                        </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


const Community = React.createClass({
    mixins: [React.PureRenderMixin],

    renderCommunity(community) {
        const desc = community.get('description') || "";
        return (
            <div className="row" key={community.get("id")}>
                <div className="col-sm-6">
                    <h4 className="domain">{community.get('domain')}</h4>
                    <p className="description"> {desc} </p>
                </div>
                <div className="col-sm-6">
                    <img className="logo" src={community.get('logo')}/>
                </div>
            </div>
        );
    },

    renderSchema(schema) {
        return (
            <div className="row" key={schema.get('id')}>
                <Schema schema={schema} />
            </div>
        );
    },

    render() {
        const community = this.props.community;
        const schemas = community.get('schema_list');
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>{community.get('name')}</h1>

                        { this.renderCommunity(community) }
                        { schemas && schemas.count() ?
                            <div className="row">
                                <div className="col-sm-12">
                                    <h3>Metadata schemas:</h3>
                                </div>
                            </div> : false }
                        <div className="row">
                            { schemas ? schemas.map(s => <Schema schema={s} key={s.get('id')}/>):false }
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


const Schema = React.createClass({
    mixins: [React.PureRenderMixin],

    render() {
        const schema = this.props.schema;
        return (
            <div className="col-sm-6" style={{borderBottom:'1px solid #ddd'}}>
                <h4 className="title">{schema.get('title')}</h4>
                <p className="description">{schema.get('description')}</p>
            </div>
        );
    }
});


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
