import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { createAndGoToRecord } from './record.jsx';


export const Navbar = React.createClass({
    // not a pure render
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

                    { this.state.open ? <NavbarMenu store={this.props.store} ref={this.props.store.root} /> : false }
                </div>
            </nav>
        );
    }
});


const NavbarSearch = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        return (
            <form>
                <div className="nav-search">
                    <span className="input-group-btn">
                        <button onClick={this.search} className="btn btn-default" type="button">
                            <i className="fa fa-question-circle"></i>
                        </button>
                    </span>
                    <input className="form-control" style={{borderRadius:0}} type="text" name="query"
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


const NavbarMenu = React.createClass({
    // not a pure render, depends on the URL
    render() {
        const topgap = {marginTop:'0.5em'}
        const user = this.props.store.branch('user');
        return (
            <div className="collapse navbar-collapse" id="header-navbar-collapse">
                <NavbarSearch />

                <ul className="nav navbar-nav text-uppercase" style={topgap}>
                    <li> <Link to="/help" activeClassName='active'> Help </Link> </li>
                    <li> <Link to="/communities" activeClassName='active'> Communities </Link> </li>
                    <li> <Link to="/records/new" activeClassName='active'> Upload </Link> </li>
                    <li> <Link to="http://www.eudat.eu/services/b2share" activeClassName='active' target="_blank"> Contact </Link> </li>

                    { user.get('name') ? <NavbarUser /> : <NavbarNoUser /> }
                </ul>
            </div>
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


export const Breadcrumbs = React.createClass({
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

