import React from 'react/lib/ReactWithAddons';
import { Link, browserHistory } from 'react-router'
import { Map, List } from 'immutable';
import { DropdownList, NumberPicker } from 'react-widgets';
import { serverCache, Error } from '../data/server';
import { Wait, Err } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'
import { ReplaceAnimate } from './animate.jsx';


export const SearchRecordRoute = React.createClass({
    renderResults(params) {
        const records = serverCache.searchRecords(params);
        if (records instanceof Error) {
            return <Err err={records}/>;
        }
        return records ?
            <ReplaceAnimate><RecordList records={records} /></ReplaceAnimate> :
            <Wait/>;
    },

    render() {
        const communities = serverCache.getCommunities();
        const location = this.props.location || {};
        const searchParams = location.query || {};
        return (
            <div>
                <h1>Records</h1>
                <Search location={this.props.location} communities={communities}/>
                { this.renderResults(searchParams) }
            </div>
        );
    }
});


export function searchRecord(state) {
    var queryArray = [];
    for (var p in state) {
        if (state.hasOwnProperty(p)) {
            const q = state[p];
            if (q !== undefined && q !== null && q !== '') {
                queryArray.push(encodeURIComponent(p) + "=" + encodeURIComponent(q));
            }
        }
    }
    const query = queryArray.join("&");
    const q_query = query ? ('?'+query) : '';

    // trigger a route reload which will do the new search, see SearchRecordRoute
    browserHistory.push(`/records/${q_query}`);
}


const Search = React.createClass({
    // not a pure render, depends on the URL
    getInitialState() {
        return {
            q: "",
            page: 1,
            size: 10,
            sort: 'bestmatch',
        };
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(newProps) {
        const location = newProps.location || {};
        this.setState(location.query || {});
    },

    search(event) {
        event.preventDefault();
        searchRecord(this.state);
    },

    searchHelp(event) {
        event.preventDefault();
    },

    renderSearchBar() {
        const setStateEvent = ev => this.setState({q: ev.target.value});
        return (
            <form onSubmit={this.search} className="form-group-lg">
                <div className="input-group">
                    <span className="input-group-btn">
                        <button onClick={this.searchHelp} className="btn btn-default" type="button">
                            <i className="fa fa-question-circle"></i>
                        </button>
                    </span>
                    <input className="form-control" style={{borderRadius:0}} type="text" name="q"
                        value={this.state.q} onChange={setStateEvent}
                        autofocus="autofocus" autoComplete="off" placeholder="Search records for..."/>
                    <span className="input-group-btn">
                        <button className="btn btn-primary" type="submit">
                            <i className="fa fa-search"></i> Search
                        </button>
                    </span>
                </div>
            </form>
        );
    },

    renderFilters() {
        if (!this.props.communities || this.props.communities instanceof Error) {
            return false;
        }

        const communities = this.props.communities.map(c => ({id: c.get('id'), name:c.get('name')})).toJS();
        communities.unshift({id:'', name:'All communities'});

        const order = [{id:'bestmatch', name:'Best Match'}, {id:'mostrecent', name:'Most Recent'}]

        const setCommunityID = c => this.setState({community: c.id});
        const setSort = s => this.setState({sort: s.id});
        const setPageSize = ps => this.setState({size: ps});

        return (
            <form className="form-horizontal" onSubmit={this.updateRecord} style={{marginTop:'1em'}}>
                <div className="form-group">
                    <label htmlFor='community' className="col-md-2 control-label">
                        <span style={{float:'right'}}> Show records from: </span>
                    </label>
                    <div id='title' className="col-md-2">
                        <DropdownList data={communities} valueField='id' textField='name'
                            defaultValue='' onChange={setCommunityID} />
                    </div>
                    <label htmlFor='sort' className="col-md-2 control-label">
                        <span style={{float:'right'}}> Sort by: </span>
                    </label>
                    <div id='sort' className="col-md-2">
                        <DropdownList data={order} valueField='id' textField='name'
                            defaultValue='bestmatch' onChange={setSort} />
                    </div>
                    <label htmlFor='size' className="col-md-2 control-label">
                        <span style={{float:'right'}}> Page size: </span>
                    </label>
                    <div id='size' className="col-md-2">
                        <NumberPicker value={this.state.size} onChange={setPageSize}/>
                    </div>
                </div>
            </form>
        );
    },

    render() {
        return (
            <div>
                { this.renderSearchBar() }
                { this.renderFilters() }
            </div>
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
        const creators = metadata.get('creators') || List();
        return (
            <div className="record col-lg-12" key={record.get('id')}>
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
                <div className="container-fluid">
                    <div className="row">
                        { this.props.records.map(this.renderRecord) }
                    </div>
                </div>
            </div>
        );
    }
});
