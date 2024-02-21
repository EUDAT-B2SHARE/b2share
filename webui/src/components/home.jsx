import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { serverCache } from '../data/server';
import { Wait } from './waiting.jsx';
import { LoginOrRegister } from './user.jsx';
import { LatestRecords } from './latest_records.jsx';

export const HomeRoute = React.createClass({
    render() {
        const latestRecords = serverCache.getLatestRecords();
        const user = serverCache.getUser();
        const info = serverCache.getInfo();
        const site_function = info.get('site_function');
        const b2access = info.get('b2access_registration_link');
        const training_site = info.get('training_site_link');
        const divStyle = {
            color: 'red',
          };
        return (
            <div className="container-fluid home-page">
                <div className="row">
                    <div className="col-sm-12">
                        <div style={{margin:'2em 0', textAlign: 'center'}}>
                        { (site_function == "" || site_function == "production") ?
                            <div>
                            <h3>Store and publish your research data</h3>
                            <p>Search in public datasets or register as a user to upload and publish your data!</p>
                            </div>
                            :
                            <div>
                            <h3 style={divStyle} >Attention: This is not a production instance. Please refrain from storing or publishing your research data here.</h3>
                            <p>Service is intended solely for testing purposes, and data may be deleted at any time!</p>
                            </div>
                            }
                            { training_site ?
                                <p>Please use <a href={training_site}>{training_site}</a> for testing or training.</p>
                                : false }
                            { (user && user.get('name')) ? false : <LoginOrRegister b2access_registration_link={b2access}/> }
                        </div>
                        <hr/>
                        <div className="row">
                            <div className="col-sm-6">
                                <h3>Create record</h3>
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
