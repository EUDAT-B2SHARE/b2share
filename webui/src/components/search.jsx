import React from 'react/lib/ReactWithAddons';
import { Link, browserHistory } from 'react-router'
import { Map, List } from 'immutable';
import { serverCache, Error } from '../data/server';
import { Wait, Err } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'
import { ReplaceAnimate } from './animate.jsx';


export const SearchRecordRoute = React.createClass({
    renderResults({ start, stop, sortBy, order, query }) {
        const records = serverCache.searchRecords({
            start:start, stop:stop, sortBy:sortBy, order:order, query:query});
        if (records instanceof Error) {
            return <Err err={records}/>;
        }
        return records ?
            <ReplaceAnimate><RecordList records={records} /></ReplaceAnimate> :
            <Wait/>;
    },

    render() {
        const searchParams = this.props.location;
        return (
            <div>
                <Search/>
                { this.renderResults(this.props.location) }
            </div>
        );
    }
});


export function searchRecord(state) {
    const {q} = state;
    browserHistory.push(`/records/?q=${q}`);
}


const Search = React.createClass({
    // not a pure render, depends on the URL
    getInitialState() {
        return { q: "" };
    },

    search(event) {
        event.preventDefault();
        searchRecord(this.state);
    },

    searchHelp(event) {
        event.preventDefault();
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(np) {
        const location = np.location || {};
        const { start, stop, sortBy, order, q } = location.query || {};
        const upstate = {};
        if (q)  { upstate.q = q; }
        if (start)  { upstate.start = start; }
        if (stop)   { upstate.stop  = stop; }
        if (sortBy) { upstate.sortBy = sortBy; }
        if (order)  { upstate.order = order; }
        if (q || start || stop || sortBy || order) {
            this.setState(upstate);
        }
    },

    change(event) {
        this.setState({q: event.target.value});
    },

    render() {
        return (
            <form onSubmit={this.search} className="form-group-lg">
                <div className="input-group">
                    <span className="input-group-btn">
                        <button onClick={this.searchHelp} className="btn btn-default" type="button">
                            <i className="fa fa-question-circle"></i>
                        </button>
                    </span>
                    <input className="form-control" style={{borderRadius:0}} type="text" name="q"
                        value={this.state.q} onChange={this.change}
                        autofocus="autofocus" autoComplete="off" placeholder="Search records for..."/>
                    <span className="input-group-btn">
                        <button className="btn btn-primary" type="submit">
                            <i className="fa fa-search"></i> Search
                        </button>
                    </span>
                </div>
            </form>
        );
    }
});


const RecordList = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderCreators(creators) {
        if (!creators || !creators.count()) {
            return false;
        }
        return (
            <span>
                <span style={{color:'black'}}> by </span>
                {creators.map(c => <span className="creator" key={c}> {c}</span>)}
            </span>
        );
    },

    renderRecord(record) {
        const id = record.get('id');
        const created = record.get('created');
        const updated = record.get('updated');
        const metadata = record.get('metadata') || Map();
        const title = metadata.get('title') ||"";
        const description = metadata.get('description') ||"";
        const creators = metadata.get('creator') || List();
        return (
            <div className="record col-lg-6" key={record.get('id')}>
                <Link to={'/records/'+id}>
                    <p className="name">{title}</p>
                    <p>
                        <span className="date">{timestamp2str(created)}</span>
                        {this.renderCreators(creators)}
                    </p>
                    <p className="description">{description.substring(0,200)}</p>
                </Link>
            </div>
        );
    },

    render() {
        return (
            <div>
                <h1>Records</h1>
                <div className="container-fluid">
                    <div className="row">
                        { this.props.records.map(this.renderRecord) }
                    </div>
                </div>
            </div>
        );
    }
});
