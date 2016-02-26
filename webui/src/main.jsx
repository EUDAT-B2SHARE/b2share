import React from 'react/lib/ReactWithAddons';
import ReactDOM from 'react-dom';
const ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;

import createBrowserHistory from 'history/lib/createBrowserHistory'
import Notification from 'react-notification';
import { fromJS } from 'immutable';
import { Router, Route, IndexRoute, Link } from 'react-router'

import { server } from './data/server';
import { Store } from './data/store';

import { Animate } from './components/animate.jsx';
import { Navbar, Breadcrumbs } from './components/navbar.jsx';
import { HomePage } from './components/home.jsx';
import { UserPage } from './components/user.jsx';
import { Help, About, B2ShareHelp, LegalNotice, UserGuide, TermsOfUse, RestApi, SearchHelp } from './components/help.jsx';
import { CommunityListPage, CommunityPage } from './components/communities.jsx';
import { RecordListPage } from './components/record_list.jsx';
import { RecordPage, NewRecordPage, EditRecordPage } from './components/record.jsx';
import { SearchPage } from './components/search.jsx';

const VERSION = '0.4.0';


const store = new Store({
    user: {
        name: null,
    },
    latestRecords: [],
    records: [],
    currentRecord: {},
    communities: [],
    search: {
        query: '',
    }
});


server.setStore(store);


const AppFrame = React.createClass({
    getInitialState() {
        return { dataRef: store.root };
    },

    updateStateOnTick() {
        const updateState = () =>
            this.setState({ dataRef: store.root });
        if (window.requestAnimationFrame) {
            window.requestAnimationFrame(updateState);
        } else {
            setTimeout(updateState, 16);
        }
    },

    componentWillMount() {
        store.onChange = this.updateStateOnTick;
    },

    render() {
        // adding a mutating ref seems necessary to propagate changes
        const additionalProps = {store: store, dataRef: store.root,  key: this.props.location.pathname}
        const notif = <Notification isActive={true} message={"Hi asdf asd fa sdfa sdf as dfa sdf asfd"} action={"action1"} />;
        return (
            <div>
                <Navbar store={store} dataRef={store.root} />
                <Animate>
                    <Breadcrumbs />
                    <div className="container-fluid">
                        <div className="col-xs-1"></div>
                            { React.cloneElement(this.props.children, additionalProps) }
                        <div className="col-xs-1"></div>
                    </div>
                </Animate>
            </div>
        );
    }
});


const Frame = React.createClass({
    render() {
        const additionalProps = {store: store, dataRef: store.root,  key: this.props.location.pathname}
        return (
            <Animate>
                { React.cloneElement(this.props.children, additionalProps) }
            </Animate>
        );
    }
});


const router = (
    <Router history={createBrowserHistory()}>
        <Route path="/" component={AppFrame}>
            <IndexRoute component={HomePage} />

            <Route path="help">
                <IndexRoute component={Help} />
                <Route path="search" component={SearchHelp} />
                <Route path="terms-of-use" component={TermsOfUse} />
                <Route path="api" component={RestApi} />
            </Route>

            <Route path="user" component={UserPage} />

            <Route path="communities" component={Frame} >
                <IndexRoute component={CommunityListPage} />
                <Route path=":id" component={CommunityPage} />
            </Route>

            <Route path="records" component={Frame} >
                <IndexRoute component={RecordListPage} />
                <Route path="new" component={NewRecordPage}/>
                <Route path=":id" component={RecordPage}>
                    <Route path="edit" component={EditRecordPage}/>
                </Route>
            </Route>

            <Route path="search" component={SearchPage} />
        </Route>
    </Router>
);


const Footer = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        return  (
            <div className="container">
                <div className="row">
                    <div className="col-xs-12 col-sm-7 col-md-7">
                        <p> <img width="45" height="31" src="/img/flag-ce.jpg" style={{float:'left', marginRight:10}}/>
                            EUDAT receives funding from the European Union’s Horizon 2020 research
                            and innovation programme under grant agreement No. 654065.&nbsp;
                            <a target="_blank" href="http://www.eudat.eu/legal-notice">Legal Notice</a>.
                        </p>
                    </div>
                    <div className="col-xs-12 col-sm-5 col-md-5 text-right">
                        <ul className="list-inline pull-right" style={{marginLeft:20}}>
                            <li><span style={{color:'#173b93', fontWeight:'500'}}> v.{VERSION}</span></li>
                        </ul>
                        <ul className="list-inline pull-right">
                            <li><a href="/help/terms-of-use">Terms of Use</a></li>
                            <li><a href="/help/api">Rest API</a></li>
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
