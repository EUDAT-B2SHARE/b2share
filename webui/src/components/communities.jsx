import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache } from '../data/server';
import { pairs } from '../data/misc';
import { Wait } from './waiting.jsx';
import { Schema } from './schema.jsx';
import { ReplaceAnimate } from './animate.jsx';


export const CommunityListRoute = React.createClass({
    render() {
        const communities = serverCache.getCommunities();
        return communities ?
            <CommunityList communities={communities} /> :
            <Wait/>;
    }
});


export const CommunityRoute = React.createClass({
    render() {
        const { id } = this.props.params; // community id or name
        const community = serverCache.getCommunity(id);
        if (!community) {
            return <Wait/>;
        }

        const [rootSchema, blockSchemas] = serverCache.getCommunitySchemas(community.get('id'), 'last');
        return (
            <ReplaceAnimate>
                <Community community={community} rootSchema={rootSchema} blockSchemas={blockSchemas}/>
            </ReplaceAnimate>
        );
    }
});


const CommunityList = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderCommunity(community) {
        const id = community.get('id');
        const name = community.get('name') || "";
        const description = community.get('description') || "";
        const logo = community.get('logo') || "";
        return (
            <div className="col-sm-6 col-lg-4" key={id}>
                <Link to={"/communities/"+name}>
                    <div className="community link">
                        <h3 className="name">{name}</h3>
                        <img className="logo" src={logo}/>
                        <p className="description"> {description.substring(0,200)} </p>
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

    renderSchema([schemaID, schema]) {
        return !schema ? false :
            <div key={schema.get('id')} className="col-sm-12" style={{borderBottom:'1px solid #eee'}}>
                <Schema schema={schema}/>
            </div>;

    },

    render() {
        const community = this.props.community;
        const blockSchemas = this.props.blockSchemas;
        return (
            <div className="community-page">
                <h1>{community.get('name')}</h1>

                { this.renderCommunity(community) }
                { blockSchemas ?
                    <div className="row">
                        <div className="col-sm-12">
                            <hr/>
                            <h3>Schemas</h3>
                        </div>
                    </div> : false }
                <div className="row">
                    { blockSchemas ? blockSchemas.map(this.renderSchema) : false}
                </div>
            </div>
        );
    }
});
