import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import { DropdownList, NumberPicker } from 'react-widgets';
import { serverCache, browser, Error } from '../data/server';
import { Wait, Err } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'
import { ReplaceAnimate } from './animate.jsx';


export const SearchRecordRoute = React.createClass({
    render() {
        const communities = serverCache.getCommunities();
        const location = this.props.location || {};
        const drafts = (location.query.drafts == 1) ? 1 : "";
        const submitted = (location.query.submitted == 1) ? 1 : "";
        const result = serverCache.searchRecords(location.query || {});
        const numResults = (result && result.get('total')) || 0;
        const title = submitted ? 'Submitted for review' : ( drafts ? 'Drafts' : 'Records');
        return (
            <div>
                <h1>{title}</h1>
                <Search location={location}
                        communities={communities}
                        drafts={drafts}
                        numResults={result && result.get('total') || 0}/>
                { result instanceof Error ? <Err err={result}/>
                    : !result ? <Wait/>
                        : <ReplaceAnimate>
                                <RecordList records={result.get('hits')} drafts={drafts} />
                          </ReplaceAnimate>
                }
            </div>
        );
    }
});


const Search = React.createClass({
    // not a pure render, depends on the URL
    getInitialState() {
        return {
            q: "",
            community: "",
            sort: 'mostrecent',
            page: "1",
            size: "10",
            drafts: "",
        };
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(newProps) {
        const location = newProps.location || {};
        this.setState(location.query || {});
        this.setState({drafts:this.props.drafts});
    },

    componentDidUpdate(prevProps, prevState) {
        if (prevState.community !== this.state.community
            || prevState.page !== this.state.page
            || prevState.size !== this.state.size
            || prevState.sort !== this.state.sort
            || prevState.drafts !== this.state.drafts ) {
            this.search();
        }
    },

    search(event) {
        event ? event.preventDefault() : false;
        browser.gotoSearch(this.state);
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
                        autoFocus="autofocus" autoComplete="off" placeholder="Search records for..."/>
                    <span className="input-group-btn">
                        <button className="btn btn-primary" type="submit">
                            <i className="fa fa-search"></i> Search
                        </button>
                    </span>
                </div>
            </form>
        );
    },

    order: [
        { id: 'bestmatch', name:'Best Match' },
        { id: 'mostrecent', name:'Most Recent' },
    ],
    sizes: ["10", "25", "50"],

    renderFilters() {
        if (!this.props.communities || this.props.communities instanceof Error) {
            return false;
        }

        const communities = this.props.communities.map(c => ({id: c.get('id'), name:c.get('name')})).toJS();
        communities.unshift({id:'', name:'All communities'});

        const setCommunityID = c => this.setState({community: c.id});
        const setSort = s => this.setState({sort: s.id});
        const setPageSize = ps => this.setState({size: ps});

        return (
            <form className="form-horizontal" style={{marginTop:'1em'}}>
                <div className="form-group">
                    <label htmlFor='community' className="col-md-2 control-label">
                        <span style={{float:'right'}}> Show records from: </span>
                    </label>
                    <div id='title' className="col-md-2">
                        <DropdownList data={communities} valueField='id' textField='name'
                            value={this.state.community} onChange={setCommunityID} />
                    </div>
                    <label htmlFor='sort' className="col-md-2 control-label">
                        <span style={{float:'right'}}> Sort by: </span>
                    </label>
                    <div id='sort' className="col-md-2">
                        <DropdownList data={this.order} valueField='id' textField='name'
                            value={this.state.sort} onChange={setSort} />
                    </div>
                    <label htmlFor='size' className="col-md-2 control-label">
                        <span style={{float:'right'}}> Page size: </span>
                    </label>
                    <div id='size' className="col-md-2">
                        <DropdownList data={this.sizes} value={this.state.size} onChange={setPageSize}/>
                    </div>
                </div>
            </form>
        );
    },

    renderPagination() {
        const numPages = 5;
        const p = +this.state.page;
        const psize = +this.state.size;
        const maxPage = Math.ceil(this.props.numResults/psize);
        const start = Math.max(1, p - Math.floor(numPages/2));
        const stop = Math.min(maxPage, start + numPages - 1);

        const setPage = page => page != p ? this.setState({page: "" + page}) : null;
        const setPrevPage = p <= 1 ? null : () => setPage(p-1);
        const setNextPage = maxPage <= p ? null : () => setPage(p+1);

        const lis = [];
        for (let i = start; i <= stop; i++) {
            const cn = i == p ? "active" : "";
            lis.push(<li key={i} className={cn}><a href="#" onClick={()=>setPage(i)}>{i}</a></li>);
        };

        const indexStart = (p-1) * psize + 1;
        const indexEnd = Math.min(indexStart + psize - 1, this.props.numResults);
        const msg = ` ${indexStart} - ${indexEnd} of ${this.props.numResults} results`;

        return (
            <div>
                <div style={{padding:'0.5em 0 0 0.5em', display:'inline-block'}}>
                    <p> { this.props.numResults ? msg : "No results"}</p>
                </div>
                <div style={{float:'right'}}>
                    <nav aria-label="Page navigation">
                        <ul className="pagination" style={{margin:'0'}}>
                            <li className={setPrevPage ? "":"disabled"}>
                                <a href="#" aria-label="Previous" onClick={setPrevPage}>
                                    <span aria-hidden="true">&laquo;</span>
                                </a>
                            </li>
                            { lis }
                            <li className={setNextPage ? "":"disabled"}>
                                <a href="#" aria-label="Next" onClick={setNextPage}>
                                    <span aria-hidden="true">&raquo;</span>
                                </a>
                            </li>
                        </ul>
                    </nav>
                </div>
            </div>
        );
    },

    render() {
        return (
            <div>
                { this.renderSearchBar() }
                { this.renderFilters() }
                { this.renderPagination() }
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
                {creators.map(c => <span className="creator" key={c.get('creator_name')}> {c.get('creator_name')}; </span>)}
            </span>
        );
    },

    renderRecord(record) {
        function first(map, key) {
            const x = map.get(key);
            return (x && x.count && x.count()) ? x.get(0) : Map();
        }
        const id = record.get('id');
        const created = record.get('created');
        const updated = record.get('updated');
        const metadata = record.get('metadata') || Map();
        const title = first(metadata, 'titles').get('title') || "";
        const description = first(metadata, 'descriptions').get('description') ||"";
        const creators = metadata.get('creators') || List();
        const edit = (this.props.drafts == 1) ? "/edit" : ""
        return (
            <div className="record col-lg-12" key={id}>
                <Link to={'/records/'+id+edit}>
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
