import React from 'react/lib/ReactWithAddons';
import { Router, Route, IndexRoute, Link } from 'react-router'
import { server } from '../data/server';
import { currentUser } from './user.jsx';
import { LatestRecords } from './record_list.jsx';
import { Wait } from './waiting.jsx';

export const HomePage = React.createClass({
    componentWillMount() {
        this.binding = this.props.store.branch('latestRecords');
        server.fetchLatestRecords();
    },

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <div className="aligncenter" style={{margin:'2em 0'}}>
                            <h3>Store and share your research data</h3>
                            <p>Search in public datasets or register as a user to upload and share your data!</p>
                            { currentUser.x ? false :
                                <a href="/oauth/login/unity">Login <span style={{color:"black"}}>or</span> Register</a> }
                        </div>
                        <hr/>
                        <div className="row">
                            <div className="col-sm-6">
                                <h3>Create Record</h3>
                            </div>
                            <div className="col-sm-5">
                                <Link to={"/records/new"} className="btn btn-primary btn-block" style={{marginTop:'1em'}}>
                                    Create a new record</Link>
                            </div>
                        </div>

                        <hr/>
                        { this.binding.valid() ? <LatestRecords records={this.binding.get()} /> : <Wait />}
                    </div>
                </div>
            </div>
        );
    }
});
