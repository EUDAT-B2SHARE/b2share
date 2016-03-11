import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map } from 'immutable';
import { server } from '../data/server';
import { objToArray } from '../data/misc';
import { Wait } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'
import { Animate } from './animate.jsx';


const defaultSchema = {
    "title": "B2SHARE Basic Block Schema",
    "description": "This is the schema used for validating the basic metadata fields of a B2SHARE record",
    "type": "object",
    "properties": {
        "title": {
            "title": "Title",
            "description": "The main title of the record.",
            "type": "string",
        },
        "description": {
            "title": "Description",
            "description": "The record abstract.",
            "type": "string",
        },
        "creator": {
            "title": "Author",
            "description": "The record author(s).",
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": true,
        },
        'keywords': {
            'title': 'Keywords',
            'description': 'Keywords...',
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": true,
        },
        'open_access': {
            'title': 'Open Access',
            'description': 'Indicate whether the resource is open or access is restricted. In case of restricted access the uploaded files will not be public, however the metadata will be.',
            'type': 'boolean',
        },
        'licence': {
            'title': 'Licence',
            'description': 'Specify the license under which this data set is available to the users (e.g. GPL, Apache v2 or Commercial). Please use the License Selector for help and additional information.',
            'type': 'string'
        },
        'embargo_date': {
            'title': 'Embargo Date',
            'description': 'Date that the embargo will expire.',
            'type': 'string',
            'format': 'date-time',
            'default': new Date(),
        },
        'contact_email': {
            'title': 'Contact Email',
            'description': 'The email of the contact person for this record.',
            'type': 'string',
            'format': 'email',
        },
        'discipline': {
            'title': 'Discipline',
            'description': 'Scientific discipline...',
            'type': 'string'
        },

        'contributor': {
            'title': 'Contributor',
            'description': 'Contributor...',
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": true,
        },
        'resource_type': {
            'title': 'Resource Type',
            'description': 'Resource Type...',
            "type": "array",
            "items": {
                'type': 'string',
                'enum': ['Text', 'Image', 'Video', 'Audio', 'Time-Series', 'Other'],
            },
            "uniqueItems": true,
        },
        'version': {
            'title': 'Version',
            'description': 'Version...',
            'type': 'string',
        },
        'language': {
            'title': 'Language',
            'description': 'Language...',
            "type": "string"
        },
        'alternate_identifier': {
            'title': 'Alternate Identifier',
            'description': 'Alternate Identifier...',
            "type": "string"
        },
    },
    "required": ["title", "description", "open_access"],
    "additionalProperties": true,
    "b2share": {
        "recommended": ['creator', 'licence', 'publication_date',
                        'keywords', 'contact_email', 'discipline'],
        "plugins": {
            'licence': 'licence_chooser',
            'discipline': 'discipline_chooser',
            'language': 'language_chooser',
        },
        "mapping": {
            "oai_dc": {
                "title": "dc.title",
                "description": "dc.description",
                "creator": "dc.creator",
                "subject": "dc.subject",
            },
            "marcxml": {
            },
        }
    },
}


function renderCommunity(community, active, onClickFn) {
    const activeClass = active ? " active": " inactive";
    const newpadding = {padding:'0 2px'};
    return (
        <div className="col-lg-2 col-sm-3 col-xs-6" style={newpadding} key={community.get('id')}>
            <div className={"community"+activeClass} title={community.get('description')}
                    onClick={onClickFn ? onClickFn : ()=>{}}>
                <p className="name">{community.get('name')}</p>
                <img className="logo" src={community.get('logo')}/>
            </div>
        </div>
    );
}


export const NewRecordPage = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    getInitialState() {
        return {
            community_id: null,
            title: "",
            description: "",
        }
    },

    componentWillMount() {
        server.fetchCommunities();
        this.binding = this.props.store.branch('communities');
    },

    createAndGoToRecord(event) {
        event.preventDefault();
        console.log(this.state);
        server.createRecord( { community_id: this.state.community_id, title: this.state.title, description: this.state.description },
            record => { window.location.assign(`${window.location.origin}/records/${record.id}/edit`); }
        );
    },

    selectCommunity(community_id) {
        console.log('set state', community_id);
        this.setState({community_id: community_id});
    },

    renderCommunity(community) {
        const active = community.get('id') === this.state.community_id;
        return renderCommunity(community, active, this.selectCommunity.bind(this, community.get('id')));
    },

    renderCommunityList(community) {
        if (!this.binding.valid()) {
            return "Wait..."
        }
        const communities = this.binding.get();
        return (
            <div className="container-fluid">
                <div className="row">
                    { communities.map(this.renderCommunity) }
                </div>
            </div>
        );
    },

    render() {
        const gap = {marginTop:'1em'};
        return (
            <div className="new-record">
                <div className="row">
                    <form className="form" onSubmit={this.createAndGoToRecord}>
                        <div className="form-group">
                            <label htmlFor="community" className="col-sm-3 control-label" style={gap}>
                                <div style={{fontWeight:'bold'}}>Community</div>
                            </label>
                            <div className="col-sm-9">
                                {this.renderCommunityList()}
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="title" className="col-sm-3 control-label" style={gap}>Title</label>
                            <div className="col-sm-9" style={gap}>
                                <input type="text" className="form-control" id="title" valueLink={this.linkState('title')} />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="description" className="col-sm-3 control-label" style={gap}>Description</label>
                            <div className="col-sm-9" style={gap}>
                                <input type="text" className="form-control" id="description" valueLink={this.linkState('description')} />
                            </div>
                        </div>

                        <div className="form-group submit">
                            <div className="col-sm-offset-3 col-sm-6" style={gap}>
                                <button type="submit" className="btn btn-primary btn-default btn-block">
                                    Create Draft Record</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
});


export const EditRecordPage = React.createClass({
    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(nextProps) {
        const { id } = nextProps.params;
        const commListBind = nextProps.store.branch('communities');
        if (!commListBind.count()) {
            server.fetchCommunities();
        }
        server.fetchRecord(id);
        const findFn = (x) => x.get('id') == id;
        const record = nextProps.store.branch('currentRecord');
        if (record.get('id') == id && commListBind.count()) {
            const community_id = record.get('metadata').get('community_id');
            const findFn = (x) => {console.log(x); return x.get('id') == community_id;}
            this.community = commListBind.find(findFn);
            if (this.community) {
                this.record = record;
            }
        }
    },

    render() {
        if (!this.record || !this.record.valid()) {
            return <Wait/>;
        }
        return <EditRecord record={this.record.get()} community={this.community.get()} />;
    }
});


export const EditRecord = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    componentWillMount() {
        this.record = this.props.record;
        this.community = this.props.community;
        this.schema = this.props.schema || defaultSchema;
        this.fields = objToArray(this.schema.properties);
        this.metadata = this.record.get('metadata') || Map();

        let state = {};
        if (this.fields && this.metadata) {
            for (const i in this.fields) {
                const f = this.fields[i];
                state[f] = this.metadata.get(f);
            }
        }
        this.setState(state);
    },

    getInitialState() {
        return {};
    },

    rnd() {
        const BIG = 1024 * 1024 * 1024;
        return Math.floor((Math.random() * BIG) + BIG);
    },

    renderField(id, field) {
        const gap = {marginTop:'1em'};
        return (
            <div className="form-group row" key={id} style={gap} title={field.description}>
                <label htmlFor={id} className="col-sm-3 control-label" style={{marginTop:10}}>{field.title}</label>
                <div className="col-sm-9">
                    <input type="text" className="form-control" id={id} valueLink={this.linkState(id)} />
                </div>
            </div>
        );
    },

    render() {
        return (
            <div className="edit-record">
                <div className="row">
                    <div className="col-md-12">
                        <div className="deposit-step">
                            <p>Step 01</p>
                            <h4>Drag and drop files here</h4>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <form className="form" onSubmit={this.createAndGoToRecord}>
                            <div className="form-group row">
                                <label htmlFor="community" className="col-sm-3 control-label">
                                    <div style={{fontWeight:'bold'}}>Community</div>
                                </label>
                                <div className="col-sm-9">
                                    {renderCommunity(this.community, true)}
                                </div>
                            </div>

                            {this.fields.map(f => this.renderField(f, this.schema.properties[f]))}

                            <div className="form-group submit">
                                <div className="col-sm-offset-3 col-sm-6" style={{marginTop:'1em'}}>
                                    <button type="submit" className="btn btn-primary btn-default btn-block">
                                        Create Draft Record</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        );
    }
});
