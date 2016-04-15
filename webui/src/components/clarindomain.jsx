var React = require('react');
var render = require('react-dom');
import { GenericDomainForm } from './genericdomain.jsx';


export const ClarinDomain = React.createClass({
    render: function() {
        return (
            <div>
                <h3> Clarin </h3>
                <GenericDomainForm />
                <table>
                    <tbody>
                        <tr>
                            <td><label forHtml='language_code' >Language Code</label></td>
                            <td><input ref='language_code' name='language_code' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='country'>Country/Region</label></td>
                            <td><input ref='country' name='country' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='resource_type'>Resource Type</label></td>
                            <td><input ref='resource_type' name='resource_type' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='project_name'>Project Name</label></td>
                            <td><input ref='project_name' name='project_name' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='quality'>Quality</label></td>
                            <td><input ref='quality' name='quality' type='text' /></td>
                        </tr>                    
                    </tbody>
                </table>
            </div>
        );
    }
});
