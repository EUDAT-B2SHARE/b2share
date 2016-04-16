import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';
import { keys, timestamp2str, stateLinker, pairs } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';


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
        if (!this.state.title.length) {
            this.setError('title', "Please add a (temporary) record title");
            return;
        }
        if (!this.state.community_id) {
            this.setError('community', "Please select a target community");
            return;
        }
        serverCache.createRecord(
            { community: this.state.community_id, title: this.state.title, open_access: true },
            record => { window.location.assign(`${window.location.origin}/records/${record.id}/edit`); }
        );
    },

    selectCommunity(community_id) {
        this.setState({community_id: community_id});
    },

    renderCommunity(community) {
        const cid = community.get('id');
        const active = cid === this.state.community_id;
        return (
            <div className="col-lg-2 col-sm-3 col-xs-6" key={community.get('id')}>
                { renderSmallCommunity(community, active, this.selectCommunity.bind(this, cid)) }
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

    render() {
        const communities = serverCache.getCommunities();
        const gap = {marginTop:'1em'};
        const biggap = {marginTop:'2em'};
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
                <div className="row">
                    <form className="form" onSubmit={this.createAndGoToRecord}>
                        <div className="form-group row">
                            <label htmlFor="title" className="col-sm-3 control-label" style={stitle}>Title</label>
                            <div className="col-sm-9" style={gap}>
                                <input type="text" className="form-control" id="title" valueLink={this.linkState('title')} />
                            </div>
                        </div>

                        <div className="form-group row">
                            <label htmlFor="community" className="col-sm-3 control-label" style={scomm}>
                                <div style={{fontWeight:'bold'}}>Community</div>
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
                            <div className="col-sm-offset-3 col-sm-9" style={gap}>
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


export const EditRecordRoute = React.createClass({
    render() {
        const { id } = this.props.params;
        const record = serverCache.getRecord(id);
        if (!record) {
            return <Wait/>;
        }
        const [rootSchema, blockSchemas] = serverCache.getRecordSchemas(record);
        const community = serverCache.getCommunity(record.getIn(['metadata', 'community']));

        return (
            <ReplaceAnimate>
                <EditRecord record={record} community={community} rootSchema={rootSchema} blockSchemas={blockSchemas}/>
            </ReplaceAnimate>
        );
    }
});


const EditRecord = React.createClass({
    getInitialState() {
        return {
            errors: {},
        };
    },

    renderFileZone() {
        return (
            <div className="row">
                <div className="col-md-12">
                    <div className="deposit-step">
                        <p>Step 01</p>
                        <h4>Drag and drop files here</h4>
                    </div>
                </div>
            </div>
        );
    },

    renderField(id, field) {
        const gap = {marginTop:'1em'};
        return (
            <div className="form-group row" key={id} style={gap} title={field.description}>
                <label htmlFor={id} className="col-sm-3 control-label" style={{fontWeight:'bold'}}>{field.title}</label>
                <div className="col-sm-9">
                    { plugin ? this.renderPlugin(id, field) :
                        <input type="text" className="form-control" id={id}
                            value={this.state[id]} onChange={stateLinker(this, id)} />
                    }
                </div>
            </div>
        );
    },

    renderFieldBlock(record, schemaID, schema) {
        console.log("field block", schemaID, schema);
        return (
            <div className="row">
            </div>
        );
    },

    render() {
        const record = this.props.record;
        const rootSchema = this.props.rootSchema;
        const blockSchemas = this.props.blockSchemas;
        if (!record || !rootSchema) {
            return <Wait/>;
        }
        return (
            <div className="edit-record">
                <div className="row">
                    <form className="form" onSubmit={this.updateRecord}>
                        { this.renderFieldBlock(this.props.record, null, rootSchema) }

                        { blockSchemas ? blockSchemas.map(([id, blockSchema]) =>
                            this.renderFieldBlock(this.props.record, id, this.props.blockSchemas) ) : false }

                        <div className="form-group submit row">
                            {pairs(this.state.errors).map( ([id, msg]) =>
                                <div className="col-sm-9 col-sm-offset-3">{msg} </div>) }
                            <div className="col-sm-offset-3 col-sm-9" style={gap}>
                                <button type="submit" className="btn btn-primary btn-default btn-block">
                                    Update Draft/Record</button>
                            </div>
                        </div>

                    </form>
                </div>
            </div>
        );
    }
});

///////////////////////////////////////////////////////////////////////////////

export function renderSmallCommunity(community, active, onClickFn) {
    const activeClass = active ? " active": " inactive";
    return (
        <div key={community.get('id')}>
            <div className={"community-small" + activeClass} title={community.get('description')}
                    onClick={onClickFn ? onClickFn : ()=>{}}>
                <p className="name">{community.get('name')}</p>
                <img className="logo" src={community.get('logo')}/>
            </div>
        </div>
    );
}


