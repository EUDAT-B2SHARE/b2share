import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { server } from '../data/server';
import { Wait } from './waiting.jsx';
import { Schema } from './schema.jsx';


export const CommunityListRoute = React.createClass({
    render() {
        const communities = store.getIn(['communities']);
        if (!communities) {
            server.fetchCommunities();
            return <Wait/>;
        }
        return <CommunityList communities={communities} />;
    }
});


export const CommunityRoute = React.createClass({
    render() {
        const { id } = nextProps.params; // community id or name
        const communities = store.getIn(['communities']);
        if (!communities) {
            server.fetchCommunities();
        } else {
            const findFn = (x) => x.get('id') == id || x.get('name') == id;
            this.community = communities.find(findFn);
        }
        // TODO: sort this out; when do we fetch the schemas?
        // server.fetchCommunitySchemas(id);

        return this.community ?
            <Community community={this.community} /> :
            <Wait/>;
    }
});


const CommunityList = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderCommunity(community) {
        const desc = community.get('description') || "";
        return (
            <div className="col-sm-6" key={community.get('id')}>
                <Link to={"/communities/"+community.get('name')}>
                    <div className="community link">
                        <h3 className="name">{community.get('name')}</h3>
                        <img className="logo" src={community.get('logo')}/>
                        <p className="description"> {desc.substring(0,200)} </p>
                    </div>
                </Link>
            </div>
        );
    },

    render() {
        return (
            <div className="community-list-page">
                <h1>Communities</h1>

                <div className="container-fluid">
                    <div className="row">
                        { this.props.communities.map(this.renderCommunity) }
                    </div>
                </div>
            </div>
        );
    }
});


const Community = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderCommunity(community) {
        const desc = community.get('description') || "";

        const bland={color:'#888'};
        const created = new Date(community.get('created')).toLocaleString();
        const updated = new Date(community.get('updated')).toLocaleString();
        return (
            <div className="row" key={community.get("id")}>
                <div className="col-sm-6">
                    <div>
                        <p>
                            <span style={bland}>Created at </span>
                            <span style={{color:'#225'}}>{created}</span>
                        </p>
                        <div style={{clear:"both"}}/>
                        { created != updated
                            ? <p>
                                <span style={bland}>Last updated at </span>
                                <span style={{color:'#225'}}>{updated}</span>
                              </p>
                            : false }
                    </div>
                    <div style={{clear:"both", height:10}}/>
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
            <div key={schema.get('id')} className="col-sm-6" style={{borderBottom:'1px solid #eee'}}>
                <Schema schema={schema}/>
            </div>
        );
    },

    render() {
        const community = this.props.community;
        const schemas = community.get('schema_list');
        return (
            <div className="community-page">
                <h1>{community.get('name')}</h1>

                { this.renderCommunity(community) }
                { schemas && schemas.count() ?
                    <div className="row">
                        <div className="col-sm-12">
                            <hr/>
                            <h3>Metadata schemas:</h3>
                        </div>
                    </div> : false }
                <div className="row">
                    { schemas ? schemas.map(this.renderSchema) : false }
                </div>
            </div>
        );
    }
});

