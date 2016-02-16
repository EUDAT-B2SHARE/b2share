import React from 'react';
import { Link } from 'react-router'
import { Map } from 'immutable';
import { server } from '../data/server';
import { Wait } from './waiting.jsx';


export const RecordListPage = React.createClass({
    componentWillMount() {
        const { start, stop, sortBy, order } = this.props.location;
        server.fetchRecords({start:start, stop:stop, sortBy:sortBy, order:order});
        this.records = this.props.store.branch('records');
    },

    render() {
        return this.records.valid() ?
            <RecordList records={this.records.get()} /> :
            <Wait/>;
    }
});


export const RecordPage = React.createClass({
    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(nextProps) {
        const { id } = nextProps.params;
        server.fetchRecord(id);
        const findFn = (x) => x.get('id') == id;
        this.record = nextProps.store.branch('currentRecord').find(findFn);
    },

    render() {
        console.log('record page children', this.props.children);
        if (!this.record || !this.record.valid()) {
            return <Wait/>;
        }
        if (this.props.children) {
            return React.cloneElement(this.props.children, {record:this.record.get()})
        }
        return <Record record={this.record.get()} />;
    }
});


const RecordList = React.createClass({
    mixins: [React.PureRenderMixin],

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>Records</h1>

                        <div className="row">
                        { this.props.records.map(renderRecord) }
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


export const LatestRecords = React.createClass({
    mixins: [React.PureRenderMixin],

    propTypes: {
        records: React.PropTypes.object.isRequired,
    },

    render() {
        return (
            <div>
                <h3>Latest Records</h3>
                <div className="row">
                    { this.props.records.map(renderRecord) }
                </div>
                <div className="row">
                    <div className="col-sm-12">
                        <Link to="/records" className="btn btn-default"> More Records ... </Link>
                    </div>
                </div>
            </div>
        );
    }
});


export function createAndGoToRecord() {
    server.createRecord(record => {
        window.location.assign(`${window.location.origin}/records/${record.id}/edit`);
    });
}


function timestamp2str(ts) {
    const date = new Date(ts);
    const y = date.getFullYear().toString();
    const month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const m = month[date.getMonth()]
    const d = date.getDate().toString();
    return d + " " + m + " " + y;
}


function renderRecord(record) {
    const metadata = record.get('metadata') || Map();
    const basic = metadata.find(md => md.get('schema_id') == '0') || Map();
    const desc = basic.get('description') ||"";
    const creators = basic.get('creator') || [];
    return (
        <div className="record col-sm-6" key={record.get('id')}>
            <Link to={'/records/'+record.get('id')}>
                <p className="name">{basic.get('title')}</p>
                <p> <span className="date">{timestamp2str(record.get('created'))}</span>
                    <span style={{color:'black'}}> by </span>
                    {creators.map(c => <span className="creator" key={c}>{c}</span>)}
                </p>
                <p className="description">{desc.substring(0,200)}</p>
            </Link>
        </div>
    );
}

const Record = React.createClass({
    mixins: [React.PureRenderMixin],

    render() {
        const record = this.props.record;
        const metadata = record.get('metadata') || Map();
        const basic = metadata.find(md => md.get('schema_id') == '0') || Map();
        const desc = basic.get('description') ||"";

        const floatRight={float:'right'};
        const bland={color:'#888'};

        const created = new Date(record.get('created')).toLocaleString();
        const updated = new Date(record.get('updated')).toLocaleString();
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <div className="large-record">
                            <h3 className="name">{basic.get('title')}</h3>
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
                            <div style={{clear:"both", height:10}}/>
                            <p className="description">{desc.substring(0,200)}</p>
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
