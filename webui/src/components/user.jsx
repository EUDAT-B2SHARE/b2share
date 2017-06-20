import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache, Error, loginURL, notifications } from '../data/server';
import { CommunityAdmin } from './community_admin.jsx'

const PT = React.PropTypes;

export const LoginOrRegister = React.createClass({
    mixins: [React.addons.PureRenderMixin],
    propTypes: {
        b2access_registration_link: React.PropTypes.string.isRequired,
    },
    render() {
        return (
            <span>
                <a href={loginURL}> Login </a>
                or
                <a href={this.props.b2access_registration_link}> Register </a>
            </span>
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
                    <li><a href="/api/user/logout/"> <i className="glyphicon glyphicon-log-out"></i> Logout </a></li>
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
    mixins: [React.addons.LinkedStateMixin],

    renderNoUser() {
        const b2access = serverCache.getInfo().get('b2access_registration_link');
        return (
            <div>
                <h1>User Profile</h1>

                <div className="container-fluid">
                    <div className="row">
                        No authenticated user found. Please <LoginOrRegister b2access_registration_link={b2access}/>.
                    </div>
                </div>
            </div>
        );
    },

    createLink(communitiesList, name){
        return <Link to={`/communities/${communitiesList[name.replace(new RegExp("(^com:|:[^:]*$)",'g'),"")]}/admin`}>(admin page)</Link>
    },

    listRoles(roles, communitiesList){
        return roles.map(r =>
            <li key={r.get('name')}>
                {r.get('description')}
                {r.get('name').includes(':admin')? this.createLink(communitiesList, r.get('name')) : ""}
            </li>)
    },

    render() {
        const user = this.props.user;
        if (!user || !user.get || !user.get('name')) {
            return this.renderNoUser();
        }
        const roles = user.get('roles');
        const communitiesListTemp = serverCache.getCommunities();
        var communitiesList = communitiesListTemp.reduce(function(map, community){
            map[community.get('id').replace(new RegExp("-",'g'),"")] = community.get('name');
            return map;
        });
        return (
            <div>
                <h1>User Profile</h1>
                <div className="container-fluid">
                    <div className="row">
                        <p><span style={{fontWeight:'bold'}}>Name:</span> {user.get('name')}</p>
                        <p><span style={{fontWeight:'bold'}}>Email:</span> {user.get('email') || "-"}</p>
                    </div>
                    <div className="row">
                        <h3>Roles</h3>
                        {roles && roles.count() && typeof(communitiesList) !== "undefined" ? this.listRoles(roles, communitiesList) : <p>You have no assigned roles</p>}
                    </div>
                    <div className="row">
                        <h3>Own records</h3>
                        <p><Link to={"/records?q=owners:"+user.get('id')}>
                            List of your published records
                            </Link></p>
                    </div>
                    <div className="row">
                        <h3>Own drafts</h3>
                            <p><Link to={"/records?drafts=1&q=publication_state%3Adraft"}>
                                List of your draft records
                            </Link></p>
                    </div>
                    <div className="row">
                        <h3>API Tokens</h3>
                        <TokenList />
                    </div>
                </div>
            </div>
        );
    }
});


const TokenList = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    getInitialState() {
        return {
            name: "",
            token: null,
            tokenList: [],
        }
    },

    componentWillMount() {
        serverCache.getUserTokens(tokenList => this.setState({tokenList}));
    },

    newToken(e) {
        e.preventDefault();
        if (!this.state.name) {
            notifications.danger('Please choose a name for the new token');
        } else {
            notifications.clearAll();
            serverCache.newUserToken(this.state.name, token => {
                const tokenList = this.state.tokenList;
                tokenList.push(token);
                this.setState({token, tokenList})
            });
        }
    },

    renderToken(t) {
        return <li className="list-group-item" key={t.id}>{t.name}</li>;
    },

    render() {
        return (
            <div>
                {this.state.tokenList.length ?
                    <div>
                        <p>Active tokens:</p>
                            <ul className="list-group">
                                { this.state.tokenList.map(this.renderToken) }
                            </ul>
                    </div> : <div><p> You have no active tokens </p></div>
                }

                {this.state.token ?
                    <div className="alert alert-success">
                        <h4>A new access token has just been created:</h4>
                        <dl className="dl-horizontal">
                            <dt>Name</dt>
                            <dd>{this.state.token.name}</dd>
                            <dt>Access token</dt>
                            <dd className="access-token">{this.state.token.access_token}</dd>
                        </dl>
                        <p className="alert alert-warning">Please copy the personal access token now. You won't see it again!</p>
                    </div> : false
                }

                <div>
                    <p className="control-label">Create new token:</p>
                    <form className="form-inline" onSubmit={this.newToken}>
                        <div className="form-group">
                            <input className="form-control" style={{borderRadius:0}} type="text" name="name"
                                value={this.state.name} onChange={e => this.setState({name: e.target.value})}
                                autoComplete="off" placeholder="New token name..."/>
                        </div>
                        <div className="form-group">
                                <button className="btn btn-primary" type="submit">
                                    <i className="fa fa-search"></i> New Token
                                </button>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
});
