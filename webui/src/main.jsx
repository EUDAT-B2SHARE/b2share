import React from 'react/lib/ReactWithAddons';
import ReactDOM from 'react-dom';
const ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;

import { browserHistory } from 'react-router';
import { fromJS } from 'immutable';
import { Router, Route, IndexRoute, Link } from 'react-router'

import { serverCache } from './data/server';

import { ReplaceAnimate } from './components/animate.jsx';
import { Navbar, Breadcrumbs } from './components/navbar.jsx';
import { HomeRoute } from './components/home.jsx';
import { UserRoute } from './components/user.jsx';
import { Help, About, B2ShareHelp, LegalNotice, UserGuide, TermsOfUse, RestApi, SearchHelp } from './components/help.jsx';
import { CommunityListRoute, CommunityRoute } from './components/communities.jsx';
import { RecordListRoute } from './components/record_list.jsx';
import { RecordRoute, NewRecordRoute, EditRecordRoute  } from './components/record.jsx';
import { SearchRoute } from './components/search.jsx';


const VERSION = '0.5.0';


const AppFrame = React.createClass({
    getInitialState() {
        return { dataRef: serverCache.store.root };
    },

    updateStateOnTick() {
        const updateState = () =>
            this.setState({ dataRef: serverCache.store.root });
        if (window.requestAnimationFrame) {
            window.requestAnimationFrame(updateState);
        } else {
            setTimeout(updateState, 16);
        }
    },

    componentWillMount() {
        serverCache.store.onChange = this.updateStateOnTick;
    },

    render() {
        // adding a mutating ref seems necessary to propagate changes
        console.log('appframe:', this.props);
        console.log('appframe:', this.context);
        const additionalProps = {dataRef: this.state.dataRef,  key: this.props.location.pathname}
                            // { React.cloneElement(this.props.children, additionalProps) }
        return (
            <div>
                <Navbar dataRef={this.state.dataRef} />
                <div className="container-fluid">
                    <div className="col-xs-1"/>
                    <div className="col-xs-10">
                        <Breadcrumbs />
                        <ReplaceAnimate>
                            { this.props.children }
                        </ReplaceAnimate>
                    </div>
                    <div className="col-xs-1"/>
                </div>
            </div>
        );
    }
});


const Frame = React.createClass({
    render() {
        const additionalProps = {dataRef: this.props.dataRef,  key: this.props.location.pathname}
        return (
            <ReplaceAnimate>
                { React.cloneElement(this.props.children, additionalProps) }
            </ReplaceAnimate>
        );
    }
});


const router = (
    <Router history={browserHistory}>
        <Route path="/" component={AppFrame}>
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
                <Route path=":id" component={CommunityRoute} />
            </Route>

            <Route path="records" component={Frame} >
                <IndexRoute component={RecordListRoute} />
                <Route path="new" component={NewRecordRoute}/>
                <Route path=":id" component={Frame} >
                    <IndexRoute component={RecordRoute} />
                    <Route path="edit" component={EditRecordRoute}/>
                </Route>
            </Route>

            <Route path="search" component={SearchRoute} />
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
