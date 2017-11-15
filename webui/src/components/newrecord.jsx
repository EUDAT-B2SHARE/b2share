import React from 'react/lib/ReactWithAddons';

import { serverCache, notifications, Error, browser } from '../data/server';
import { Wait, Err } from './waiting.jsx';
import { renderSmallCommunity } from './common.jsx';


export const NewRecordRoute = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    getInitialState() {
        return {
            community_id: null,
            title: "",
            errors: {},
        }
    },

    setError(id, msg) {
        const err = this.state.errors;
        err[id] = msg;
        this.setState({errors: this.state.errors});
    },

    createAndGoToRecord(event) {
        event.preventDefault();
        if (!this.state.title.length || !this.state.title.trim()) {
            this.setError('title', "Please add a (temporary) record title");
            return;
        }
        if (!this.state.community_id) {
            this.setError('community', "Please select a target community");
            return;
        }
        const json_record = {
            community: this.state.community_id,
            titles: [{
                title: this.state.title.trim(),
            }],
            open_access: true,
        }
        serverCache.createRecord(json_record, record => browser.gotoEditRecord(record.id));
    },

    selectCommunity(community_id) {
        this.setState({community_id: community_id});
    },

    renderCommunity(community) {
        const cid = community.get('id');
        const selected = cid === this.state.community_id;
        return (
            <div className="col-lg-2 col-sm-3 col-xs-6" key={community.get('id')}>
                { renderSmallCommunity(community, selected, this.selectCommunity.bind(this, cid)) }
            </div>
        );
    },

    renderCommunityList(communities) {
        if (!communities) {
            return <Wait/>;
        }
        return (
            <div className="container-fluid">
                <div className="row">
                    { communities.map(this.renderCommunity) }
                </div>
            </div>
        );
    },

    onTitleChange(event) {
        this.setState({title:event.target.value});
    },

    componentWillMount() {
        const user = serverCache.getUser();
        if (!user || !user.get('name')) {
            notifications.warning('Please login. A new record can only be created by logged in users.');
        }
    },

    render() {
        const training_site = serverCache.getInfo().get('training_site_link');
        const communities = serverCache.getCommunities();
        if (communities instanceof Error) {
            return <Err err={communities}/>;
        }

        const stitle = {marginTop:'1em'};
        if (this.state.errors.title) {
            stitle.color = "red";
        }
        const scomm = {marginTop:'1em'};
        if (this.state.errors.community) {
            scomm.color = "red";
        }
        return (
            <div className="new-record">
                { training_site ?
                    <div className="row">
                        <div className="col-sm-9 col-sm-offset-3">
                            <p>Please use <a href={training_site}>{training_site}</a> for testing or training.</p>
                        </div>
                    </div>
                    : false }
                <div className="row">
                    <form className="form-horizontal" onSubmit={this.createAndGoToRecord}>
                        <div className="form-group row">
                            <label htmlFor="title" className="col-sm-3 control-label" style={stitle}>
                                <span style={{float:'right'}}>Title</span>
                            </label>
                            <div className="col-sm-9" style={{marginTop:'1em'}}>
                                <input type="text" className="form-control" id='title'
                                    style={{fontSize:24, height:48}}
                                    value={this.state.title} onChange={this.onTitleChange} />
                            </div>
                        </div>

                        <div className="form-group row">
                            <label htmlFor="community" className="col-sm-3 control-label" style={scomm}>
                                <span style={{float:'right'}}>Community</span>
                            </label>
                            <div className="col-sm-9">
                                {this.renderCommunityList(communities)}
                            </div>
                        </div>

                        <div className="form-group submit row">
                            {this.state.errors.title ?
                                <div className="col-sm-9 col-sm-offset-3">{this.state.errors.title} </div>: false }
                            {this.state.errors.community ?
                                <div className="col-sm-9 col-sm-offset-3">{this.state.errors.community} </div> : false }
                            <div className="col-sm-offset-3 col-sm-9" style={{marginTop:'1em'}}>
                                <button type="submit" className="btn btn-primary btn-default btn-block">
                                    Create Draft Record</button>
                            </div>
                        </div>
                    </form>
                </div>
                <div className="row">
                    <div className="col-sm-9 col-sm-offset-3"  style={{borderTop:'1px solid #eee', paddingTop:'1em'}}>
                        <p className="alert alert-warning" style={{color:'black'}}>
                        You can also update the data in an existing record by creating a new version of that record.
                        Search for the 'Create new version' button on the record's page.
                        </p>
                    </div>
                </div>
            </div>
        );
    }
});
