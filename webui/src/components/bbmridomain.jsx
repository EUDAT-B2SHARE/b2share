var React = require('react');
var render = require('react-dom');
import { GenericDomainForm } from './genericdomain.jsx';


export const BbmriDomain = React.createClass({
    render: function() {
        return (
            <div>
                <h3> BBMRI </h3>
                <GenericDomainForm />
                <table>
                    <tbody>
                        <tr>
                            <td><label forHtml='UUID' >UUID</label></td>
                            <td><input ref='UUID' name='UUID' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='species_name'>Species name</label></td>
                            <td><input ref='species_name' name='species_name' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='collector_name'>Collector name</label></td>
                            <td><input ref='collector_name' name='collector_name' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='collector_date'>Collection date</label></td>
                            <td><input ref='collector_date' name='collector_date' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='Locality'>Locality</label></td>
                            <td><input ref='Locality' name='Locality' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='Latitude'>Latitude</label></td>
                            <td><input ref='Latitude' name='Latitude' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='Longitude'>Longitude</label></td>
                            <td><input ref='Longitude' name='Longitude' type='text' /></td>
                        </tr>                      
                    </tbody>
                </table>
            </div>
        );
    }
});
