import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache } from '../data/server';
import { currentUser } from './user.jsx';
import { renderRecord } from './search.jsx';
import { Wait } from './waiting.jsx';

export const HomeRoute = React.createClass({
    render() {
        const latestRecords = serverCache.getLatestRecords();
        return (
            <div className="container-fluid home-page">
                <div className="row">
                    <div className="col-sm-12">
                        <div style={{margin:'2em 0', textAlign: 'center'}}>
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
                        { latestRecords ? <LatestRecords records={latestRecords} /> : <Wait />}
                    </div>
                </div>
            </div>
        );
    }
});

const LatestRecords = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    propTypes: {
        records: React.PropTypes.object.isRequired,
    },

    render() {
        return (
            <div>
                <h3>Latest Records</h3>
                <div className="row">
                    { this.props.records.map(renderRecord) }
                </div>
                <div className="row">
                    <div className="col-sm-offset-6 col-sm-5" style={{marginTop:'1em', marginBottom:'1em',}}>
                        <Link to="/records" className="btn btn-default btn-block"> More Records ... </Link>
                    </div>
                </div>
            </div>
        );
    }
});
