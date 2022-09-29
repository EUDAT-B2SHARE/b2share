import React from 'react/lib/ReactWithAddons';


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
        return (
            <div className={"alert alert-danger"}>
                <h3>Error <span>{error.code}</span></h3>
                <span>{msg}</span>
            </div>
        );
    }
});
