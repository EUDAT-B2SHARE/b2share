import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'

var Restapi = require('../docs/templates/rest-api');
var Termofuse = require('../docs/templates/tou');


export const Help = React.createClass({
    render() {
        return (
            <div className="container-fluid help-page">
                <div className="row">
                    <div className="col-sm-10">
                        <div className="page-header"> <h2>Help</h2> </div>
                    </div>
                </div>

                <div className="row">
                    <div className="col-xs-1 hidden-xs"/>
                    <div className="col-sm-10">
                        <div className="row">
                            <div className="col-sm-3">
                                <ul className="list-group">
                                    <li className="list-group-item">
                                        <Link to="http://www.eudat.eu/services/b2share" target="_blank"><i className="fa fa-list"></i> What is B2SHARE</Link>
                                    </li>
                                    <li className="list-group-item">
                                        <Link to="http://www.eudat.eu/services/userdoc/b2share" target="_blank"><i className="fa fa-info-circle"></i> User Guide</Link>
                                    </li>
                                    <li className="list-group-item">
                                        <Link to="/help/search"><i className="fa fa-search"></i> Search</Link>
                                    </li>
                                    <li className="list-group-item">
                                        <Link to="/help/terms-of-use"><i className="fa fa-question-circle"></i> Term-Of-Use</Link>
                                    </li>
                                    <li className="list-group-item">
                                        <Link to="/help/api"><i className="fa fa-list"></i> RestAPI</Link>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});

export const About = React.createClass({
    render() {
        return <div>About</div>;
    }
});

export const B2ShareHelp = React.createClass({
    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>What is B2SHARE</h1>
                    </div>
                </div>
            </div>
        );
    }
});

export const LegalNotice = React.createClass({
    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>Legal Notice</h1>
                    </div>
                </div>
            </div>
        );
    }
});

export const UserGuide = React.createClass({
    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>User Guide</h1>
                    </div>
                </div>
            </div>
        );
    }
});

export const TermsOfUse = React.createClass({
	render: function() {
		var termofuse;
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <Termofuse term_of_use={termofuse}/>
                    </div>
                </div>
            </div>
        );
    }
});

export const RestApi = React.createClass({
    render: function() {
	    var restapihelp;
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <Restapi rest_api={restapihelp}/>
                    </div>
                </div>
            </div>
        );
    }
});

export const SearchHelp = React.createClass({
    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <h1>Searching</h1>
                    </div>
                </div>
            </div>
        );
    }
});
