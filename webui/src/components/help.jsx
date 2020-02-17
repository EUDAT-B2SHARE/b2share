import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router';

import { serverCache, Error } from '../data/server';


export const Help = React.createClass({
    render() {
        const termsOfUse = serverCache.getInfo().get('terms_of_use_link');
        return (
            <div className="help-page">
                <h1>Help</h1>

                <div className="container-fluid">
                    <div className="col-sm-6">
                        <ul className="list-group">
                            <li className="list-group-item">
                                <Link to="https://eudat.eu/services/b2share" target="_blank"><i className="fa fa-list"></i> What is B2SHARE?</Link>
                            </li>
                            <li className="list-group-item">
                                <Link to="https://eudat.eu/services/userdoc/b2share-usage" target="_blank"><i className="fa fa-info-circle"></i> User Guide</Link>
                            </li>
                            <li className="list-group-item">
                                <Link to="https://eudat.eu/services/userdoc/b2share-advanced-search" target="_blank"><i className="fa fa-info-circle"></i> Advanced Search guide </Link>
                            </li>
                            <li className="list-group-item">
                                <Link to="https://eudat.eu/services/userdoc/b2share-http-rest-api" target="_blank"><i className="fa fa-list"></i> REST API </Link>
                            </li>
                            { termsOfUse ?
                                <li className="list-group-item">
                                    <a href={termsOfUse}><i className="fa fa-question-circle"></i> Terms of Use</a>
                                </li> : false
                            }
                            <li className="list-group-item">
                                <Link to="https://github.com/EUDAT-B2SHARE/b2share" target="_blank"><i className="fa fa-exclamation-circle"></i> Report an issue </Link>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        );
    }
});
