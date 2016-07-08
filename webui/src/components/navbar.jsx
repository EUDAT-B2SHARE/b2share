import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache, Error, NOTIFICATION_DISPLAY_TIME } from '../data/server';
import { ListAnimate, HeightAnimate } from './animate.jsx';
import { NavbarUser } from './user.jsx';
import { searchRecord } from './search.jsx';


export const Navbar = React.createClass({
    // not a pure render, depends on the URL
    getInitialState() {
        return { open: true };
    },

    toggle() {
        this.setState({open: !this.state.open});
    },

    render() {
        return (
            <nav className="header-nav navbar navbar-default navbar-static-top">
                <div className="container-fluid">
                    <div className="col-xs-1"/>
                    <div className="navbar-header">
                        <button type="button" className="navbar-toggle collapsed" onClick={this.toggle}>
                            <span className="sr-only">Toggle Navigation Menu</span>
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                        </button>
                        <Link to="/" className="navbar-brand">
                            <img style={{height: 90}} src="/img/logo.png"/>
                        </Link>
                    </div>

                    { this.state.open ? <NavbarMenu collapse={!this.state.open} location={this.props.location}/> : false }
                </div>
            </nav>
        );
    }
});


const NavbarMenu = React.createClass({
    // not a pure render, depends on the URL
    render() {
        const cname = this.props.collapse ? "collapse":"";
        const hideSearchBar = this.props.location.pathname == '/records' || this.props.location.pathname == '/records/';
        return (
            <div className={cname + " navbar-collapse"} id="header-navbar-collapse">
                <NavbarSearch location={this.props.location} visibility={!hideSearchBar}/>

                <ul className="nav navbar-nav text-uppercase">
                    <li> <Link to="/help" activeClassName='active'> Help </Link> </li>
                    <li> <Link to="/communities" activeClassName='active'> Communities </Link> </li>
                    <li> <Link to="/records/new" activeClassName='active'> Upload </Link> </li>
                    <li> <a href="http://www.eudat.eu/services/b2share" activeClassName='active' target="_blank"> Contact </a> </li>
                </ul>
                <ul className="nav navbar-nav user">
                    <NavbarUser user={serverCache.getUser()}/>
                </ul>
            </div>
        );
    }
});


const NavbarSearch = React.createClass({
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
        const visibility = this.props.visibility ? "visible" : "hidden";
        return (
            <form onSubmit={this.search} style={{visibility}}>
                <div className="nav-search">
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
                            <i className="fa fa-search"></i> SEARCH
                        </button>
                    </span>
                </div>
            </form>
        );
    }
});


export const Breadcrumbs = React.createClass({
    // not a pure render, depends on the URL
    renderLink(text, path, isfirst, islast) {
        if (isfirst && islast) {
            return <i className="fa fa-home"/>;
        } else if (isfirst) {
            return <Link to={path}><i className="fa fa-home"/></Link>;
        } else if (islast) {
            return text;
        }
        return <Link to={path}>{text}</Link>;
    },

    renderItem([text, path, isfirst, islast]) {
        return (
            <li key={path} className={'text-uppercase' + (islast ?' active':'')}>
                {this.renderLink(text, path, isfirst, islast)}
            </li>
        );
    },

    render() {
        let crumbs = window.location.pathname.split('/').filter(x=>x);
        if (!crumbs.length) {
            return false;
        }
        let pairs = [['', '/', true, false]];
        for (let i = 0; i < crumbs.length; i++) {
            pairs.push([crumbs[i], '/'+crumbs.slice(0, i+1).join('/'), false]);
        }
        pairs[pairs.length-1][3] = true;
        return (
            <div className="row">
                <ol className="breadcrumb">
                    { pairs.map(this.renderItem) }
                </ol>
            </div>
        );
    }
});


export const Notifications = React.createClass({
    renderNotification(level, text, date) {
        if (date + NOTIFICATION_DISPLAY_TIME < Date.now()) {
            return false; // old notification, ignore
        }
        return (
            <li className={"alert alert-"+level} key={text}>
                {text}
            </li>
        );
    },

    renderAlerts([level, texts]) {
        return(
            <ListAnimate key={level}>
                {texts.entrySeq().map(([t, date]) => this.renderNotification(level, t, date))}
            </ListAnimate>
        );
    },

    render() {
        const levels = serverCache.getNotifications();
        return (
            <ol className="list-unstyled">
                <HeightAnimate>
                    <ListAnimate>
                        {levels.entrySeq().map(this.renderAlerts)}
                    </ListAnimate>
                </HeightAnimate>
            </ol>
        );
    }
});
