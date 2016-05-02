import React from 'react/lib/ReactWithAddons';
import { Link, browserHistory } from 'react-router'
import { serverCache } from '../data/server';
import { ListAnimate, HeightAnimate } from './animate.jsx';


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
        const user = serverCache.getUser();
        const cname = this.props.collapse ? "collapse":"";
        return (
            <div className={cname + " navbar-collapse"} id="header-navbar-collapse">
                <NavbarSearch location={this.props.location}/>

                <ul className="nav navbar-nav text-uppercase">
                    <li> <Link to="/help" activeClassName='active'> Help </Link> </li>
                    <li> <Link to="/communities" activeClassName='active'> Communities </Link> </li>
                    <li> <Link to="/records/new" activeClassName='active'> Upload </Link> </li>
                    <li> <a href="http://www.eudat.eu/services/b2share" activeClassName='active' target="_blank"> Contact </a> </li>
                </ul>
                <ul className="nav navbar-nav text-uppercase user">
                    { user.get('name') ? <NavbarUser /> : <NavbarNoUser /> }
                </ul>
            </div>
        );
    }
});


const NavbarSearch = React.createClass({
    // not a pure render, depends on the URL
    getInitialState() {
        return { query: "" };
    },

    search(event) {
        event.preventDefault();
        browserHistory.push(`/records/?query=${this.state.query}`);
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props.location);
    },

    componentWillReceiveProps(np) {
        const { start, stop, sortBy, order, query } = np.query || {};
        const upstate = {};
        if (query)  { upstate.query = query; }
        if (start)  { upstate.start = start; }
        if (stop)   { upstate.stop  = stop; }
        if (sortBy) { upstate.sortBy = sortBy; }
        if (order)  { upstate.order = order; }
        if (query || start || stop || sortBy || order) {
            console.log("search", np, upstate);
            this.setState(upstate);
        }
    },

    change(event) {
        this.setState({query: event.target.value});
    },

    render() {
        return (
            <form onSubmit={this.search}>
                <div className="nav-search">
                    <span className="input-group-btn">
                        <button onClick={this.search} className="btn btn-default" type="button">
                            <i className="fa fa-question-circle"></i>
                        </button>
                    </span>
                    <input className="form-control" style={{borderRadius:0}} type="text" name="query"
                        value={this.state.query} onChange={this.change}
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


const NavbarNoUser = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        return (
            <li>
                <Link activeClassName='active' to="/users/login" className="visible-xs"><i className="fa fa-sign-in"/></Link>
                <Link activeClassName='active' to="/users/login" className="hidden-xs"><i className="fa fa-sign-in"/> Login</Link>
            </li>
        );
    }
});


const NavbarUser = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        return (
            <li className="dropdown">
                <a href="#" className="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">
                    <i className="fa fa-user"></i>
                    <i className="fa fa-user color-primary"></i>
                    <span className="caret"></span></a>
                <ul className="dropdown-menu pull-right" role="menu">
                    <li><Link to="/users/profile"> <i className="fa fa-info"></i> Profile </Link></li>
                    <li>
                        <Link to="/users/notifications">
                            <i className="fa fa-comments-o"></i> Notifications
                            <span className="label label-primary">1</span>
                        </Link>
                    </li>
                    <li className="divider"></li>
                    <li><Link to="/users/logout"> <i className="fa fa-sign-out"></i> Logout </Link></li>
                </ul>
            </li>
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
    renderNotification(level, text) {
        console.log('render not', level, text);
        return (
            <li className={"alert alert-"+level} key={text}>
                {text}
            </li>
        );
    },

    renderAlerts([level, texts]) {
        return(
            <ListAnimate key={level}>
                {texts.entrySeq().map(([t, date]) => this.renderNotification(level, t))}
            </ListAnimate>
        );
    },

    render() {
        const notifs = serverCache.getNotifications();
        return (
            <ol className="list-unstyled">
                <HeightAnimate>
                    <ListAnimate>
                        {notifs.entrySeq().map(this.renderAlerts)}
                    </ListAnimate>
                </HeightAnimate>
            </ol>
        );
    }
});
