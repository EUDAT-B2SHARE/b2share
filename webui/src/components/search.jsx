import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map } from 'immutable';
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'
import { ReplaceAnimate } from './animate.jsx';


export const SearchRecordRoute = React.createClass({
    render() {
        const { start, stop, sortBy, order, query } = this.props.location;
        const records = serverCache.searchRecords({start:start, stop:stop, sortBy:sortBy, order:order, query:query});
        return records ?
            <ReplaceAnimate><RecordList records={records} /></ReplaceAnimate> :
            <Wait/>;
    }
});


const RecordList = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        return (
            <div>
                <h1>Records</h1>
                <div className="container-fluid">
                    <div className="row">
                        { this.props.records.map(renderRecord) }
                    </div>
                </div>
            </div>
        );
    }
});


export function renderRecord(record) {
    const id = record.get('id');
    const created = record.get('created');
    const updated = record.get('updated');
    const metadata = record.get('metadata') || Map();
    const title = metadata.get('title') ||"";
    const description = metadata.get('description') ||"";
    const creators = metadata.get('creator') || [];
    return (
        <div className="record col-sm-6" key={record.get('id')}>
            <Link to={'/records/'+id}>
                <p className="name">{title}</p>
                <p> <span className="date">{timestamp2str(created)}</span>
                    <span style={{color:'black'}}> by </span>
                    {creators.map(c => <span className="creator" key={c}> {c}</span>)}
                </p>
                <p className="description">{description.substring(0,200)}</p>
            </Link>
        </div>
    );
}
