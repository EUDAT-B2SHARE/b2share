import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router';
import { serverCache, Error } from '../data/server';


export const Help = React.createClass({
    listLinks(links) {
        return <ul className="list-group">
            { Object.keys(links).map((key, index) => (
                !links[key][0] ? false :
                <li className="list-group-item" key={index}>
                    <Link to={links[key][0]} target="_blank" key={index}><i className={"fa " + links[key][1]}></i> {key}</Link>
                </li>
            ))}
            </ul>
    },

    render() {
        const info = serverCache.getInfo();
        const helplinks = info.get('help_links', new Map);
        const links = {
            'What is B2SHARE?': ['https://eudat.eu/services/b2share', 'fa-list'],
            'User Guide': [helplinks.get('user-guide'), 'fa-file'],
            'Search': [helplinks.get('search'), 'fa-info-circle'],
            'REST API': [helplinks.get('rest-api'), 'fa-info-circle'],
            'Terms of Use': [info.get('terms_of_use_link'), 'fa-question-circle'],
            'Report an issue': [helplinks.get('issues'), 'fa-exclamation-circle']
        }

        return (
            <div className="help-page">
                <h1>Help</h1>
                <div className="container-fluid">
                    <div className="col-sm-6">
                        {this.listLinks(links)}
                    </div>
                </div>
            </div>
        );
    }
});
