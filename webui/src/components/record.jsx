import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map } from 'immutable';
import { server } from '../data/server';
import { Wait } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'


export const RecordPage = React.createClass({
    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(nextProps) {
        const { id } = nextProps.params;
        server.fetchRecord(id);
        const findFn = (x) => x.get('id') == id;
        const record = nextProps.store.branch('currentRecord');
        if (record.get('id') == id) {
            this.record = record;
        }
    },

    render() {
        if (!this.record || !this.record.valid()) {
            return <Wait/>;
        }
        // if (this.props.children) {
        //     return React.cloneElement(this.props.children, {record:this.record.get()})
        // }
        return <Record record={this.record.get()} />;
    }
});


const Record = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderDates(record) {
        const floatRight={float:'right'};
        const bland={color:'#888'};

        const created = new Date(record.get('created')).toLocaleString();
        const updated = new Date(record.get('updated')).toLocaleString();
        return (
            <div style={floatRight}>
                <p style={floatRight}>
                    <span style={bland}>Created at </span>
                    <span style={{color:'#225'}}>{created}</span>
                </p>
                <div style={{clear:"both"}}/>
                { created != updated
                    ? <p style={floatRight}>
                        <span style={bland}>Last updated at </span>
                        <span style={{color:'#225'}}>{updated}</span>
                      </p>
                    : false }
            </div>
        );
    },

    renderCreators(basic) {
        const creators = basic.get('creator') || [];

        return (
            <p> <span style={{color:'black'}}> by </span>
                { creators && creators.length
                    ? creators.map(c => <a className="creator" key={c}> {c}</a>)
                    : <span style={{color:'black'}}> [Unknown] </span>
                }
            </p>
        );
    },

    render() {
        const record = this.props.record;
        const metadata = record.get('metadata') || Map();
        const basic = metadata.find(md => md.get('schema_id') == '0') || Map();
        const desc = basic.get('description') ||"";

        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <div className="large-record">
                            <h3 className="name">{basic.get('title')}</h3>

                            { this.renderDates(record) }
                            <div style={{clear:"both", height:10}}/>

                            { this.renderCreators(basic) }

                            <p className="description">{desc.substring(0,200)}</p>
                        </div>
                        </div>
                </div>
            </div>
        );
    }
});


export const NewRecordPage = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    getInitialState() {
        return {
            title: ""
        }
    },

    createAndGoToRecord(event) {
        event.preventDefault();
        console.log(this.state);
        server.createRecord( { title: this.state.title },
            record => { window.location.assign(`${window.location.origin}/records/${record.id}/edit`); }
        );
    },

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <div className="new-record">

                            <form className="form-horizontal" onSubmit={this.createAndGoToRecord}>
                                <div className="form-group">
                                    <label htmlFor="title" className="col-sm-2 control-label">Title</label>
                                    <div className="col-sm-10">
                                        <input type="text" className="form-control" id="title" valueLink={this.linkState('title')}
                                            placeholder="Record Title"/>
                                    </div>
                                </div>

                                <div className="form-group submit">
                                    <div className="col-sm-offset-2 col-sm-6">
                                        <button type="submit" className="btn btn-primary btn-default btn-block">
                                            Create Draft Record</button>
                                    </div>
                                </div>
                            </form>

                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


export const EditRecord = React.createClass({
    mixins: [React.PureRenderMixin],

    render() {
        const record = this.props.record;
        const metadata = record.get('metadata') || Map();
        const basic = metadata.find(md => md.get('schema_id') == '0') || Map();
        const desc = basic.get('description') ||"";
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h3 className="name">{basic.get('title')}</h3>
                        <p className="date">{new Date(1000*record.get('created_at')).toLocaleString()}</p>
                        <p className="description">{desc.substring(0,200)}</p>
                    </div>
                </div>
            </div>
        );
    }
});
