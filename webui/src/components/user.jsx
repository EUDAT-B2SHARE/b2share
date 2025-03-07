import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache, Error, loginURL, notifications } from '../data/server';
import { FocusManager } from './common.jsx'
import { CommunityAdmin } from './community_admin.jsx'
import { Wait, Err } from './waiting.jsx';

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

    ignore(e) {
        e.preventDefault();
        return false;
    },

    menuClick() {
        this.setState({open: false})
    },

    renderNoUser() {
        return (
            <li className="dropdown">
                <a href={loginURL}><i className="glyphicon glyphicon-log-in"/> Login</a>
            </li>
        );
    },

    handleClick(e) {
        if (this.state.open) {
            this.setState({open: false})
        } else {
            // This is required for Safari to open the menu
            // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#clicking_and_focus
            e.target.focus()
            this.setState({open: true})
        }
    },

    renderUser(user) {
        return (
            <FocusManager
                onBlur={() => this.setState({open: false})}
            >
            {bind => (
                <li className={"dropdown"+(this.state.open ? " open":"")}>
                    <a id="dropdown-top" href="#" className="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false" onClick={(e) => this.handleClick(e)} {...bind}>
                        <i className="glyphicon glyphicon-user"></i>
                        {" "} {user.get('name')} {" "}
                        <span className="caret"></span>
                    </a>
                {this.state.open && (
                    <ul id="dropdown-menu" className="dropdown-menu pull-right" style={{textAlign:'left'}} role="menu" onClick={this.menuClick} {...bind}>
                        <li><Link to="/user"> <i className="fa fa-info"></i> Profile </Link></li>
                        <li className="divider"></li>
                        <li><Link to={"/records/?q=owners:" + this.props.user.get('id')}> <i className="fa fa-file"></i> Published records </Link></li>
                        <li><Link to="/records/?drafts=1"> <i className="fa fa-file"></i> Draft records </Link></li>
                        <li className="divider"></li>
                        <li><a href="/api/user/logout/"> <i className="glyphicon glyphicon-log-out"></i> Logout </a></li>
                    </ul>
                )}
                </li>
            )}
            </FocusManager>
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

    createLink(communitiesMapping, name) {
        return <Link to={`/communities/${communitiesMapping[name.replace(new RegExp("(^com:|:[^:]*$)",'g'),"")]}/admin`}> (admin page)</Link>
    },

    listRoles(roles, communitiesMapping) {
        return roles.map(r =>
            <li key={r.get('name')}>
                {r.get('description')}
                {r.get('name').includes(':admin')? this.createLink(communitiesMapping, r.get('name')) : ""}
            </li>)
    },

    render() {
        const user = this.props.user;
        if (!user || !user.get || !user.get('name')) {
            return this.renderNoUser();
        }
        const roles = user.get('roles');
        const communitiesList = serverCache.getCommunities();
        if (communitiesList.size) {
            var communitiesMapping = communitiesList.reduce((map, community) => {
                map[community.get('id').replace(new RegExp("-",'g'),"")] = community.get('name');
                return map;
            }, {});
        }
        return (
            <div className="bottom-line">
                <h1>User Profile</h1>
                <div className="container-fluid">
                    <div className="row">
                        <p><span style={{fontWeight:'bold'}}>Name:</span> {user.get('name')}</p>
                        <p><span style={{fontWeight:'bold'}}>Email:</span> {user.get('email') || "-"}</p>
                    </div>
                    <div className="row">
                        <h3>Roles</h3>
                        <p>
                            {(roles && roles.count() && communitiesMapping !== undefined) ? this.listRoles(roles, communitiesMapping) : "You have no assigned roles" }
                        </p>
                    </div>
                    <div className="row">
                        <h3>Own records</h3>
                        <p><Link to={"/records?q=owners:"+user.get('id')}>
                            List of your published records
                            </Link></p>
                    </div>
                    <div className="row">
                        <h3>Own drafts</h3>
                            <p><Link to={"/records?drafts=1"}>
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
    getInitialState() {
        return {
            token: null,
        }
    },

    newToken(tokenName) {
        if (!tokenName) {
            notifications.danger('Please choose a name for the new token');
        } else {
            notifications.clearAll();
            serverCache.newUserToken(tokenName, token => {
                this.setState({token});
            });
        }
    },

    renderToken(t) {
        return <div key={t.id}> <Token token_id={t.id} token_name={t.name} removeToken={this.removeToken} /> </div>
    },

    removeToken(token_id){
        serverCache.removeUserToken(token_id);
    },

    render() {
        const tokenList = serverCache.getUserTokens();
        if (!tokenList) {
            return <Wait/>;
        }
        if (tokenList instanceof Error) {
            return <Err err={tokenList}/>;
        }
        return (
            <div>
                {tokenList.length ?
                    <div>
                        <p>Active tokens:</p>
                            <ul className="list-group">
                                { tokenList.map(this.renderToken) }
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

            <AddToken newToken={this.newToken} />
            </div>
        );
    }
});


const Token = React.createClass({
    removeToken(e){
        e.preventDefault();
        this.props.removeToken(this.props.token_id);
    },

    render(){
        return  <li className="list-group-item" key={this.props.token_id}>{this.props.token_name}
                    <span className="pull-right">
                            <form className="form-inline" onSubmit={this.removeToken}>
                                <button className="btn btn-default btn-xs" type="submit">
                                    <i className="fa fa-trash-o"></i> Remove
                                </button>
                            </form>
                    </span>
                </li>;
    }
});

const AddToken = React.createClass({
    getInitialState() {
        return {
            name: "",
        }
    },

    addToken(e){
        e.preventDefault();
        this.props.newToken(this.state.name);
    },

    render(){
        return <div>
                    <p className="control-label">Create new token:</p>
                    <form className="form-inline" onSubmit={this.addToken}>
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
            }
});
