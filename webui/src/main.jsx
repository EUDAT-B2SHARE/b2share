import React from 'react/lib/ReactWithAddons';
import ReactDOM from 'react-dom';
const ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;

import { fromJS } from 'immutable';
import { Router, Route, browserHistory, useRouterHistory, IndexRoute } from 'react-router';

import PiwikReactRouter from 'piwik-react-router';

import { serverCache, notifications } from './data/server';

import { ReplaceAnimate } from './components/animate.jsx';
import { Navbar, Breadcrumbs, Notifications } from './components/navbar.jsx';
import { HomeRoute } from './components/home.jsx';
import { UserRoute } from './components/user.jsx';
import { Help } from './components/help.jsx';
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

// Set environmental variables in matomo-config.js

const piwik = window.B2SHARE_WEBUI_MATOMO_URL && window.B2SHARE_WEBUI_MATOMO_SITEID ?
    PiwikReactRouter({
        url: window.B2SHARE_WEBUI_MATOMO_URL,
        siteId: window.B2SHARE_WEBUI_MATOMO_SITEID,
    }) : false;

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
    <Router history={ (browserHistory) }>
        <Route path="/" component={AppFrame} onChange={testNewPage}>
            <IndexRoute component={HomeRoute} />

            <Route path="help">
                <IndexRoute component={Help} />
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



const routerElement = ReactDOM.render(router, document.getElementById('page'));
serverCache.init(info => {
    const siteFunctionElement = document.getElementById('site-function');
    if (siteFunctionElement && info.get('site_function')) {
        if (info.get('site_function') != 'production') {
            siteFunctionElement.innerHTML = info.get('site_function');
        }
    }

    const versionElement = document.getElementById('version');
    if (versionElement && info.get('version')) {
        versionElement.innerHTML = info.get('version');
    }
});
