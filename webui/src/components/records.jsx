import React from 'react';
import { Link } from 'react-router'
import { server } from '../data/server';
import { Wait } from './waiting.jsx';


export const RecordListPage = React.createClass({
    componentWillMount() {
        this.binding = this.props.store.branch('records');
        const { start, stop, sortBy, order } = this.props.location;
        server.fetchRecords({start:start, stop:stop, sortBy:sortBy, order:order});
    },

    render() {
        return this.binding.valid() ?
            <RecordList binding={this.binding} ref={this.binding.getRef()} /> :
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
        const findFn = (x) => x.get('id') == id || x.get('name') == id;
        this.binding = nextProps.store.branch('records').find(findFn);
    },

    render() {
        return this.binding && this.binding.valid() ?
            <Record binding={this.binding} ref={this.binding.getRef()} /> :
            <Wait/>;
    }
});



export const RecordList = React.createClass({
    mixins: [React.PureRenderMixin],

    render() {
        const records = this.props.binding.get() || [];
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>Records</h1>

                        <div className="container-fluid">
                        <div className="row">
                        { records.map(renderRecord) }
                        </div>
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

                <p>
                    <a href="/records" className="btn btn-default"> More Records ... </a>
                </p>
            </div>
        );
    }
});


function renderRecord(record) {
    const desc = record.get('description') ||"";
    return (
        <div className="record col-sm-6" key={record.get('id')}>
            <a href="/records/{record.get('id')}">
                <p className="date">{record.get('created_at')}</p>
                <p className="name">{record.get('title')}</p>
                <p className="description">{desc.substring(0,200)}</p>
            </a>
        </div>
    );
}
