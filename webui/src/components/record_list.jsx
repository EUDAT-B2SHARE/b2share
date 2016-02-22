import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map } from 'immutable';
import { server } from '../data/server';
import { Wait } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'


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


const RecordList = React.createClass({
    mixins: [React.addons.PureRenderMixin],

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
    mixins: [React.addons.PureRenderMixin],

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


function renderRecord(record) {
    if (record.get('error')) {
        return (
            <div className="record col-sm-6" key={record.get('id')}>
                <Link to={'/records/'+record.get('id')}>
                    <p className="name">{basic.get('title')}</p>
                    <p> <span className="date">{timestamp2str(record.get('created'))}</span>
                        <span style={{color:'black'}}> by </span>
                        {creators.map(c => <span className="creator" key={c}> {c}</span>)}
                    </p>
                    <p className="description">{desc.substring(0,200)}</p>
                </Link>
            </div>
        );
    }

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
                    {creators.map(c => <span className="creator" key={c}> {c}</span>)}
                </p>
                <p className="description">{desc.substring(0,200)}</p>
            </Link>
        </div>
    );
}
