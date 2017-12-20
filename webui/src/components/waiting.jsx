import React from 'react/lib/ReactWithAddons';
import { Versions } from './versions.jsx';


export const Wait = React.createClass({
    render() {
        return (
            <div> Loading... </div>
        );
    }
});


export const Err = React.createClass({
    render() {
        const error = this.props.err;
        let msg = error.text;
        if (error.data && error.data.message) {
            msg = error.data.message;
        }
        const showVersions = Boolean(this.props.versions);
        return (
            <div className={"alert alert-danger"}>
                <div class="row">
                    <div class="col-md-6">
                        <h3>Error <span>{error.code}</span></h3>
                        { showVersions ? <Versions recordID={this.props.id} versions={this.props.versions}/> : null }
                    </div>
                    <div class="col-md-6">
                        <span>{msg}</span>
                    </div>
                </div>
            </div>
        );
    }
});
