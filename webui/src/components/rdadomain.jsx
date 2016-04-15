var React = require('react');
var render = require('react-dom');
import { GenericDomainForm } from './genericdomain.jsx';


export const RDADomain = React.createClass({
    render: function() {
        return (
            <div>
                <h3> RDA </h3>
                <GenericDomainForm />
            </div>
        );
    }
});
