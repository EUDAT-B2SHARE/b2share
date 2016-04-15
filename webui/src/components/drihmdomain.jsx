var React = require('react');
var render = require('react-dom');
import { GenericDomainForm } from './genericdomain.jsx';


export const DrihmDomain = React.createClass({
    render: function() {
        return (
            <div>
                <h3> DRIHM </h3>
                <GenericDomainForm />
                <table>
                    <tbody>
                        <tr>
                            <td><label forHtml='reference_date' >Reference date</label></td>
                            <td><input ref='reference_date' name='reference_date' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='reference_system'>Reference System</label></td>
                            <td><input ref='reference_system' name='reference_system' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='topic_category'>Topic Category</label></td>
                            <td><input ref='topic_category' name='topic_category' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='responsible'>Responsible Party</label></td>
                            <td><input ref='responsible' name='responsible' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='geographic_location'>Geographic Location</label></td>
                            <td><input ref='geographic_location' name='geographic_location' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='spatial_resolution'>Spatial Resolution</label></td>
                            <td><input ref='spatial_resolution' name='spatial_resolution' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='vertical_extent'>Vertical Extent</label></td>
                            <td><input ref='vertical_extent' name='vertical_extent' type='text' /></td>
                        </tr>
                        <tr>
                            <td><label forHtml='lineage'>Lineage</label></td>
                            <td><input ref='lineage' name='lineage' type='text' /></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
});
