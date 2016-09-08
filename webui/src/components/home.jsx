import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import { timestamp2str } from '../data/misc.js'
import { serverCache, Error } from '../data/server';
import { currentUser } from './user.jsx';
import { Wait, Err } from './waiting.jsx';
import { LoginOrRegister } from './user.jsx';

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
                            <LoginOrRegister/>
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

    renderCreators(creators) {
        if (!creators || !creators.count()) {
            return false;
        }
        return (
            <span>
                <span style={{color:'black'}}> by </span>
                {creators.map(c => <span className="creator" key={c}> {c}</span>)}
            </span>
        );
    },

    renderRecord(record) {
        const id = record.get('id');
        const created = record.get('created');
        const updated = record.get('updated');
        const metadata = record.get('metadata') || Map();
        const title = metadata.get('title') ||"";
        const description = metadata.get('description') ||"";
        const creators = metadata.get('creators') || List();
        return (
            <div className="record col-md-6" key={record.get('id')}>
                <Link to={'/records/'+id}>
                    <p className="name">{title}</p>
                    <p>
                        <span className="date">{timestamp2str(created)}</span>
                        {this.renderCreators(creators)}
                    </p>
                    <p className="description">{description.substring(0,200)}</p>
                </Link>
            </div>
        );
    },

    render() {
        if (this.props.records instanceof Error) {
            return false;
        }
        return (
            <div>
                <h3>Latest Records</h3>
                <div className="row">
                    { this.props.records.map(this.renderRecord) }
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
