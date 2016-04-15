var React = require('react');
var render = require('react-dom');
import { GenericDomainForm } from './genericdomain.jsx';


export const NrmDomain = React.createClass({
    render: function() {
        return (
            <div>
                <h3> NRM </h3>
                <GenericDomainForm />
            </div>
        );
    }
});
