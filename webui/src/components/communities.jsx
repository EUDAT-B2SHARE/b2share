import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { fromJS } from 'immutable';
import { serverCache, Error } from '../data/server';
import { pairs } from '../data/misc';
import { Wait, Err } from './waiting.jsx';
import { Schema } from './schema.jsx';
import { ReplaceAnimate } from './animate.jsx';
import { LatestRecords } from './latest_records.jsx';
import { PersistentIdentifier } from './editfiles.jsx';


export const CommunityListRoute = React.createClass({
    render() {
        const communities = serverCache.getCommunities();
        if (communities instanceof Error) {
            return <Err err={communities}/>;
        }
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
        if (community instanceof Error) {
            return <Err err={community}/>;
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

    parseBytes(bytes) {
        // Parse bytes to nicer units
        const units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        if (!+bytes) return '0 Bytes';
        const divider = 1024;
        const i = Math.floor(Math.log(bytes) / Math.log(divider));
        return `${parseFloat((bytes / Math.pow(divider, i)).toFixed(1))} ${units[i]}`;
    },
    
    parseThousands(amount) {
        // Parse bytes to nicer units
        if (!+amount) return '0';
        if (amount > 1000) {
            return `${parseFloat((amount/1000).toFixed(1))}k`;
        }
        return amount;
    },

    renderCommunity(community, records) {
        const desc = community.get('description') || "";
        const created = new Date(community.get('created')).toLocaleString();
        const updated = new Date(community.get('updated')).toLocaleString();
        const file_downloads = records.get("total") > 0 ? this.parseThousands(community.get("communityFileDownloadTotal")) : "0"

        return (
            <div className="row" key={community.get("id")}>
                <div className="col-sm-6 col-md-6">
                    <div className="dates">
                        <p>
                            <span>Created at </span>
                            {created}
                        { created != updated && <span><br/><span>Last updated at </span>{updated}</span> }
                        </p>
                    </div>
                    <div className="description">
                        <p> {
                          desc.split('\n').map(function(item, key) {
                            return (
                                <span key={key}>
                                {item}
                                <br/>
                                </span>
                            )
                          })}
                        </p>
                    </div>
                    <p className="pid">
                        <span>Identifier: </span>
                        <PersistentIdentifier pid={community.get('id')}/>
                    </p>
                    <p className="pid">
                        <span>Using root schema version: {community.get('schema', {}).get('root_schema', "")}</span>
                    </p>
                </div>
                <div>
                    <div className='col-sm-6 col-md-6 col-lg-4 statistic-wrapper'>
                        <div className="community-statistics" id="statistics" >
                            <div className="statistic-row">
                                <p className="pid">
                                    <span>Record views</span><br /><span>{this.parseThousands(community.get("communityRecordViewsTotal"))}</span>
                                </p>
                                <p className="pid">
                                    <span>File downloads</span><br /><span>{file_downloads}</span>
                                </p>
                            </div>
                            <div className="statistic-details">
                                <p className="stat">
                                    <span>Records</span><span>{this.parseThousands(records.get("total"))}</span>
                                </p>
                                <p className="stat">
                                    <span>Files</span><span>{this.parseThousands(community.get("communityFileAmountTotal"))}</span>
                                </p>
                                <p className="stat">
                                    <span>File size</span><span>{this.parseBytes(community.get("communityFileSizeTotal"))}</span>
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="col-sm-6 col-md-6 col-lg-2 community-small-wrapper">
                        <div className="community-small passive" title={community.get('description')}>
                            <p className="name">{community.get('name')}</p>
                            <img className="logo" src={community.get('logo')}/>
                        </div>
                    </div>
                </div>
            </div>
        );
    },

    renderSchema([schemaID, schema]) {
        return !schema ? false :
            <div key={schema.get('id')} className="col-sm-12 bottom-line">
                <Schema id={schemaID} schema={schema}/>
            </div>;
    },

    render() {
        const community = this.props.community;
        if (community instanceof Error) {
            return <Err err={community}/>;
        }
        const latestRecords = serverCache.getLatestRecordsOfCommunity({community: community.get('id')});
        const records = serverCache.searchRecords({community: community.get('id')});
        const rootSchema = this.props.rootSchema;
        if (!rootSchema) {
            return <Wait />;
        }
        const envelopedRootSchema = fromJS({
            json_schema: rootSchema,
        });
        const blockSchemas = this.props.blockSchemas;
        return (
            <div className="community-page">
                <h1>{community.get('name')}</h1>

                { this.renderCommunity(community,records) }
                <hr/>
                { latestRecords ? <LatestRecords title="Community latest records" records={latestRecords} community={community.get('id')} /> : <Wait />}
                <div className="row">
                    { rootSchema ? this.renderSchema(['', envelopedRootSchema]) : false }
                </div>
                <div className="row">
                    { blockSchemas ? blockSchemas.map(this.renderSchema) : false}
                </div>
            </div>
        );
    }
});
