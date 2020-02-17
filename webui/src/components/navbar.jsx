import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache, browser, notifications, Error } from '../data/server';
import { ListAnimate, HeightAnimate } from './animate.jsx';
import { NavbarUser } from './user.jsx';


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
                    <li> <Link to="/help"> Help </Link> </li>
                    <li> <Link to="/communities"> Communities </Link> </li>
                    <li> <Link to="/records/new"> Upload </Link> </li>
                    <li> <a href="https://www.eudat.eu/support-request?service=B2SHARE" target="_blank"> Contact </a> </li>
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
        return {
            q: "",
        };
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(newProps) {
        const location = newProps.location || {};
        const state = Object.assign({}, location.query);
        delete state['drafts'];
        delete state['community'];
        delete state['page'];
        this.setState(state);
    },

    search(event) {
        event.preventDefault();
        browser.gotoSearch(this.state);
    },

    searchHelp(event) {
        event.preventDefault();
        window.open("https://eudat.eu/services/userdoc/b2share-advanced-search", "_blank");
    },

    render() {
        const setStateEvent = ev => this.setState({q: ev.target.value});
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
                        value={this.state.q} onChange={setStateEvent}
                        autoComplete="off" placeholder="Search records for..."/>
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
    olDomElement: null,

    componentWillMount() {
        notifications.store.onChange = () => {
            this.forceUpdate();
            if (this.olDomElement && notifications.isNotEmpty()) {
                this.olDomElement.scrollIntoView({
                    block: "start",
                    behavior: "smooth",
                });
            }
        }
    },

    renderNotification(level, text, date) {
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
        const levels = notifications.getAll();
        const nonEmpty = levels.find(texts => texts.size > 0);
        return (
            <ol className="list-unstyled" ref={(x)=>{this.olDomElement=x}}>
                <HeightAnimate>
                    { nonEmpty ?
                        <ListAnimate>
                            {levels.entrySeq().map(this.renderAlerts)}
                        </ListAnimate> : false }
                </HeightAnimate>
            </ol>
        );
    }
});
