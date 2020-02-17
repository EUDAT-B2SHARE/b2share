import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router';
import { DropdownList, Multiselect } from 'react-widgets';
import { fromJS, OrderedMap, Map } from 'immutable';
import { serverCache, notifications , browser , Error, loginURL} from '../data/server';
import { isCommunityAdmin } from './record.jsx';
import { LoginOrRegister } from './user.jsx';
import { Wait, Err } from './waiting.jsx';

export const CommunityAdmin = React.createClass({
    // Assign a role to a user
    handleChange(roles, email, selectedRole){
        var searchedUser = {};
        if(email && selectedRole ){
             serverCache.registerUserRole(email, roles[selectedRole],
                    () => {
                        notifications.success("The new role was added to the user");
                    },
                    () => {
                        notifications.danger("An error occured while trying to add the new role to the user.");
                    }
                );
        }
    },

    renderNoUser() {
        const b2access = serverCache.getInfo().get('b2access_registration_link');
        return (
            <div>
                <div className="container-fluid">
                    <div className="row">
                        No authenticated user found. Please <LoginOrRegister b2access_registration_link={b2access}/>.
                    </div>
                </div>
            </div>
        );
    },

    render() {
        const current_user = serverCache.getUser();
        const community = serverCache.getCommunity(this.props.params.id);

        if (!current_user || !current_user.get || !current_user.get('name')) {
            return this.renderNoUser();
        }
        if (!community) {
            return <Wait/>;
        }
        if (community instanceof Error) {
            return <Err err={community}/>;
        }

        if (!isCommunityAdmin(community.get('id'))) {
            return <Err err={{code: 403, text: "You don't have the required role to access this page"}}/>;
        }

        const communityName = community.get('name');

        var roles = {};
        community.get('roles').forEach( role =>{
            roles[role.get('name').replace(new RegExp("^com:[^:]*:"), "")] = role.get('id');
        });

        var users = {};
        for (var key in roles) {
            users[roles[key]] = serverCache.getCommunityUsers(roles[key]);
        }

        var mergedUsers = {};
        Object.keys(users).forEach(role => {
            if(typeof(users[role]) !== "undefined" && Object.keys(users[role]).length > 0 ){
                users[role].forEach(user => {
                    if( !mergedUsers[user.getIn(['id'])] ){
                        mergedUsers[user.getIn(['id'])] = {"active":user.getIn(["active"]), "email": user.getIn(["email"]), "roles":[]};
                    }
                    mergedUsers[user.getIn(['id'])].roles.push(parseInt(role));
                })
            }
        })

        return (
            <div>
                <div> <h1>{communityName} user management</h1> </div>
                <div className="well">
                    <UsersTable users={mergedUsers} roles={roles}/>
                </div>
                <div>
                    <AddUser roles={roles} handleChange={this.handleChange} />
                </div>
            </div>
        );
    }
});


export const UsersTable = React.createClass({
    render() {
        if (!this.props.users) {
            return <Wait/>;
        }
        var rows = [];
        Object.keys(this.props.users).forEach( userid => {
            var roleName = [];
            for(var k in this.props.roles){
                if(this.props.users[userid]["roles"].includes(this.props.roles[k])){
                    roleName.push(k);
                }
            }
            rows.push( <UserRow userID={userid}
                                userEmail={this.props.users[userid]["email"]}
                                userRoleID={this.props.users[userid]["roles"]}
                                userRoleName={roleName}
                                key={userid}
                                roles={this.props.roles} />);
        });

        return (
            <div>
                <div className="row">
                    <div className="col-sm-4"><h4><strong> Email Address </strong></h4></div>
                    <div className="col-sm-2"><h4><strong> Role </strong></h4></div>
                    <div className="col-sm-6"><h4><strong> Edit </strong></h4></div>
                </div>
                <div>{rows}</div>
            </div>
        );
    }
});


export const UserRow = React.createClass({
    render(){
        if (!this.props.roles) {
            return <Wait/>;
        }

        var showRolesName = this.props.userRoleName.map((role) => <div key={role}> {role || ''}</div>);
        return (
            <div>
                <div className="row well">
                    <div className="col-sm-4">{this.props.userEmail}</div>
                    <div className="col-sm-2">{showRolesName}</div>
                    <div className="col-sm-6"><EditRoles roles={this.props.roles}
                                                        defRoleName={this.props.userRoleName}
                                                        defRoleID={this.props.userRoleID}
                                                        userEmail={this.props.userEmail}
                                                        userID={this.props.userID}/></div>
                </div>
            </div>
        );
    }
});

export const EditRoles = React.createClass({
    getInitialState() {
        return {
            edit: false,
            currentAssignedRole: null,
        };
    },

    componentWillMount(){
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(nextProps){
        this.setState({currentAssignedRole: nextProps.defRoleName});
    },

    onSubmit(e) {
        e.preventDefault();
        this.editUsersRoles();
    },

    assignRole(roleid, userEmail){
        serverCache.registerUserRole(userEmail, roleid,
            () => {
                notifications.success("The new role was added to the user");
            },
            () => {
                notifications.danger("An error occured while trying to add the new role to the user");
            }
        );
    },

    deleteRole(roleid, userid){
        const current_user = serverCache.getUser();
        if(parseInt(userid) === current_user.getIn(['id']) && this.props.roles['admin'] === parseInt(roleid)){
            notifications.danger("You are not allowed to remove your admin role through this page. ");
            this.setState({currentAssignedRole: this.state.currentAssignedRole.concat("admin")})
        }
        else{
            serverCache.deleteRoleOfUser(roleid, userid);
        }
    },

    editUsersRoles(){
        if(this.state.currentAssignedRole){
            let oldroles = new Set(this.props.defRoleName);
            let newroles = new Set(this.state.currentAssignedRole);
            var putList = new Set(this.state.currentAssignedRole.filter(x => !oldroles.has(x)));
            var deleteList = new Set(this.props.defRoleName.filter(x => !newroles.has(x)));
            if(putList.size > 0){
                putList.forEach(role => {
                    this.assignRole(this.props.roles[role], this.props.userEmail);
                })
            }
            if(deleteList.size > 0){
                deleteList.forEach(role => {
                    this.deleteRole(this.props.roles[role], this.props.userID);
                })
            }
        }
    },

    render() {
        var edit = this.state.edit;
        var toggle = () => this.setState({ edit: !edit});
        var noop = ()=>{ };
        var rolesList = [];
        for(var key in this.props.roles){
            rolesList.push(key);
        }
        return (
            <form className="form-horizontal" onSubmit={this.onSubmit}>
                <div className="row">
                    <div className="col-sm-4 ">
                        <button type="submit" className="btn btn-primary btn-default btn-block" onClick={toggle}> { edit ? 'Save' : 'Edit'} </button>
                    </div>
                    <div className="col-sm-8">
                        <Multiselect open={edit}
                                    readOnly={!edit}
                                    data={rolesList}
                                    value={this.state.currentAssignedRole}
                                    onChange={currentAssignedRole => this.setState({ currentAssignedRole })}
                                    onToggle={noop} />
                    </div>
                </div>
            </form>
        );
    }
});


export const AddUser = React.createClass({
    getInitialState() {
        return {
            email: "",
            selectedRole: "",
        };
    },

    onChange(e) {
        this.setState({
            [e.target.name]: e.target.value
        });
    },

    onSubmit(e) {
        e.preventDefault();
        this.props.handleChange(this.props.roles, this.state.email, this.state.selectedRole)
    },

    render() {
        const gap = {marginTop:'1em', marginBottom:'1em'};
        var rolesList = [];
        for(var key in this.props.roles){
            rolesList.push(key);
        }

        return(
            <div className='well' style={gap}>
                <h3>Add a new user</h3>
                <form  className="form-horizontal" onSubmit={this.onSubmit}>
                    <div className="row">
                        <div className="col-sm-6">
                            <label >New user email address:</label>
                            <input ref={(ref) => this.email = ref}
                                    name='email'
                                    className="form-control"
                                    type='email'
                                    onChange={this.onChange}  required />
                        </div>
                        <div className="col-sm-4">
                            <label >Choose a role for new user:</label>
                            <DropdownList data={rolesList}
                                            onChange={selectedRole => this.setState({ selectedRole })} />
                        </div>
                        <div className="col-sm-2">
                            <label ></label>
                            <button type="submit" className="btn btn-primary btn-default btn-block" >Add user</button>
                        </div>
                    </div>
                </form>
            </div>
        );
    },
});


