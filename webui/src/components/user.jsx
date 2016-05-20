import React from 'react/lib/ReactWithAddons';
import { Link, browserHistory } from 'react-router'
import { serverCache, loginURL } from '../data/server';

export const LoginOrRegister = React.createClass({
    mixins: [React.addons.PureRenderMixin],
    render() {
        return (
            <a href={loginURL}>Login <span style={{color:"black"}}>or</span> Register</a>
        );
    }
});

export const NavbarUser = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    getInitialState() {
        return {
            open: false,
        }
    },

    toggleOpen() {
        this.setState({open:!this.state.open});
    },

    ignore(e) {
        e.preventDefault();
        return false;
    },

    renderNoUser() {
        return (
            <li>
                <a href={loginURL}><i className="glyphicon glyphicon-log-in"/> Login</a>
            </li>
        );
    },

    renderUser(user) {
        return (
            <li className={"dropdown"+(this.state.open ? " open":"")} onClick={this.toggleOpen}>
                <a href="#" className="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false" onClick={this.ignore}>
                    <i className="glyphicon glyphicon-user"></i>
                    {" "} {user.get('name')} {" "}
                    <span className="caret"></span>
                </a>
                <ul className="dropdown-menu pull-right" role="menu">
                    <li><Link to="/user"> <i className="fa fa-info"></i> Profile </Link></li>
                    <li className="divider"></li>
                    <li><a href="/api/logout/"> <i className="glyphicon glyphicon-log-out"></i> Logout </a></li>
                </ul>
            </li>
        );
    },

    render() {
        const user = this.props.user;
        return (user && user.get('name')) ? this.renderUser(user) : this.renderNoUser();
    }
});


export const UserRoute = React.createClass({
    render() {
        return <UserProfile user={serverCache.getUser()}/>;
    }
});



export const UserProfile = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderNoUser() {
        return (
            <div>
                <h1>User Profile</h1>

                <div className="container-fluid">
                    <div className="row">
                        No authenticated user found. Please <LoginOrRegister/>.
                    </div>
                </div>
            </div>
        );
    },

    render() {
        const user = this.props.user;
        if (!user || !user.get('name')) {
            return this.renderNoUser();
        }
        return (
            <div>
                <h1>User Profile</h1>

                <div className="container-fluid">
                    <div className="row">
                        <p>Name: {user.get('name')}</p>
                        <p>Email: {user.get('email') || "-"}</p>
                        <p>Roles: {user.get('roles') || "-"}</p>
                        <p><Link to={"/records?q=owner_id:"+user.get('id')}>Own records</Link></p>
                    </div>
                </div>
            </div>
        );
    }
});
