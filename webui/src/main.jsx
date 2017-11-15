import React from 'react/lib/ReactWithAddons';
import ReactDOM from 'react-dom';
const ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;

import { fromJS } from 'immutable';
import { Router, Route, browserHistory, IndexRoute } from 'react-router'

import { serverCache, notifications } from './data/server';

import { ReplaceAnimate } from './components/animate.jsx';
import { Navbar, Breadcrumbs, Notifications } from './components/navbar.jsx';
import { HomeRoute } from './components/home.jsx';
import { UserRoute } from './components/user.jsx';
import { Help, TermsOfUse, RestApi, SearchHelp } from './components/help.jsx';
import { CommunityListRoute, CommunityRoute } from './components/communities.jsx';
import { SearchRecordRoute } from './components/search.jsx';
import { RecordRoute  } from './components/record.jsx';
import { NewRecordRoute  } from './components/newrecord.jsx';
import { EditRecordRoute, NewRecordVersionRoute  } from './components/editrecord.jsx';
import { AccessRequest } from './components/accessrequest.jsx';
import { ReportAbuse } from './components/reportabuse.jsx';
import { CommunityAdmin } from './components/community_admin.jsx'

// TODO: test file uploads in various browsers
// TODO: edit records: plugins
// TODO: edit records: open enums (rename enum to options?)
// TODO: do memory profile

const AppFrame = React.createClass({
    getInitialState() {
        return { dataRef: serverCache.store.root };
    },

    updateStateOnTick() {
        const updateState = () => this.setState({ dataRef: serverCache.store.root });
        if (window.requestAnimationFrame) {
            window.requestAnimationFrame(updateState);
        } else {
            updateState();
        }
    },

    componentWillMount() {
        serverCache.store.onChange = this.updateStateOnTick;
    },

    render() {
        // adding a mutating ref is necessary to propagate changes
        const additionalProps = {dataRef: this.state.dataRef,  pathName: this.props.location.pathname}
        return (
            <div>
                <Navbar dataRef={this.state.dataRef}  location={this.props.location}/>
                <div className="container-fluid">
                    <div className="col-sm-1"/>
                    <div className="col-sm-10">
                        <Breadcrumbs />
                        <Notifications dataRef={notifications.store.root}/>
                        <ReplaceAnimate>
                            { this.props.children && React.cloneElement(this.props.children, additionalProps) }
                        </ReplaceAnimate>
                    </div>
                    <div className="col-sm-1"/>
                </div>
            </div>
        );
    }
});


const Frame = React.createClass({
    render() {
        const additionalProps = {dataRef: this.props.dataRef,  pathName: this.props.location.pathname}
        return (
            <ReplaceAnimate>
                { this.props.children && React.cloneElement(this.props.children, additionalProps) }
            </ReplaceAnimate>
        );
    }
});


function testNewPage(prev, next) {
    if (prev.location.pathname === next.location.pathname) {
        return;
    }
    notifications.clearAll();
}


const router = (
    <Router history={browserHistory}>
        <Route path="/" component={AppFrame} onChange={testNewPage}>
            <IndexRoute component={HomeRoute} />

            <Route path="help">
                <IndexRoute component={Help} />
                <Route path="search" component={SearchHelp} />
                <Route path="terms-of-use" component={TermsOfUse} />
                <Route path="api" component={RestApi} />
            </Route>

            <Route path="user" component={UserRoute} />

            <Route path="communities" component={Frame} >
                <IndexRoute component={CommunityListRoute} />
                <Route path=":id" component={Frame} >
                    <IndexRoute component={CommunityRoute} />
                    <Route path="admin" component={CommunityAdmin} />
                </Route>

            </Route>

            <Route path="records" component={Frame} >
                <IndexRoute component={SearchRecordRoute} />
                <Route path="new" component={NewRecordRoute}/>
                <Route path=":id" component={Frame} >
                    <IndexRoute component={RecordRoute} />
                    <Route path="edit" component={EditRecordRoute}/>
                    <Route path="update" component={NewRecordVersionRoute}/>
                    <Route path="accessrequest" component={AccessRequest}/>
                    <Route path="abuse" component={ReportAbuse}/>
                </Route>
            </Route>

        </Route>
    </Router>
);


const Footer = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    getInitialState() {
        return {}
    },

    render() {
        const {site_function, version, git_commit} = this.state.info ? this.state.info.toJS() : {};
        return  (
            <div className="container">
                <div className="row">
                    <div className="col-xs-12 col-sm-7 col-md-7">
                        <p style={{position: 'relative', height:0, margin:0}}>
                            <span className="site-function" style={{'position':'absolute', bottom:'10px'}}>
                                { site_function !== 'production' ? (site_function||'') : false }
                            </span>
                        </p>
                        <p> <img width="45" height="31" src="/img/flag-ce.jpg" style={{float:'left', marginRight:10}}/>
                            EUDAT receives funding from the European Union’s Horizon 2020 research
                            and innovation programme under grant agreement No. 654065.&nbsp;
                            <a target="_blank" href="http://www.eudat.eu/legal-notice">Legal Notice</a>.
                        </p>
                    </div>
                    <div className="col-xs-12 col-sm-5 col-md-5 text-right">
                        <ul className="list-inline pull-right" style={{marginLeft:20}}>
                            <li title={"git:"+git_commit}>
                                <span style={{color:'#173b93', fontWeight:'500'}}> v.{version||''}</span>
                                <code style={{border:'none', backgroundColor:'transparent', color:'gray'}}>
                                    { git_commit ? ("git:"+git_commit) : false }
                                </code>
                            </li>
                        </ul>
                        <ul className="list-inline pull-right">
                            <li><a href="/help/terms-of-use">Terms of Use</a></li>
                            <li><a href="/help/api">HTTP API</a></li>
                            <li><a target="_blank" href="http://eudat.eu/what-eudat">About EUDAT</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        );
    }
});


const footerElement = ReactDOM.render(<Footer />, document.getElementById('footer') );
const routerElement = ReactDOM.render(router, document.getElementById('page'));
serverCache.init(info => footerElement.setState({info}));
