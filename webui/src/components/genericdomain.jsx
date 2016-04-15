var React = require('react');
var render = require('react-dom');


const urlRoot = window.location.origin;


const imgUrls = {
    img_eudat:     `${urlRoot}/img/communities/eudat.png`,
    img_bbmri:     `${urlRoot}/img/communities/bbmri.png`,
    img_clarin:    `${urlRoot}/img/communities/clarin.png`,
    img_drihm:     `${urlRoot}/img/communities/drihm.png`,
    img_euon:      `${urlRoot}/img/communities/euon.png`,
    img_gbif:      `${urlRoot}/img/communities/gbif.png`,
    img_nrm:       `${urlRoot}/img/communities/nrm.png`,
    img_rda:       `${urlRoot}/img/communities/rda.png`,
    img_on:        `${urlRoot}/img/on.png`,
    img_off:       `${urlRoot}/img/off.png`,
};


export const GenericDomainForm = React.createClass({
    getInitialState: function () {
        return {
            pressed: imgUrls.img_off
        };
    },

    openAccessHandleClick: function(event) {
        this.setState({pressed: !this.state.pressed})
    },
        
    render: function() {
        var open_access_pic = this.state.pressed? imgUrls.img_on : imgUrls.img_off;
        return (
            <div>
                <h3> Add basic details </h3>
                    <div className='row'>
                        <div className='col-sm-6'>
                            <table>
                                <tbody>
                                    <tr>
                                        <td><label forHtml='title' >Title</label></td>
                                        <td><input ref='title' name='title' type='text' /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='description'>Description</label></td>
                                        <td><textarea ref='description' name='description' type='textarea' rows="4" cols="50" /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='creator'>Creator</label></td>
                                        <td><input ref='creator' name='creator' type='text' /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='open_access'>Open Access</label></td>
                                        <td><img src={open_access_pic} width="45" height="20" onClick={this.openAccessHandleClick} /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='embargo'>Embargo Till</label></td>
                                        <td><input ref='embargo' name='embargo' type='text' /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='license'>License</label></td>
                                        <td><input ref='license' name='license' type='text' /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='keywords'>Keywords</label></td>
                                        <td><input ref='keywords' name='keywords' type='text' /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='contact_email'>Contact Email</label></td>
                                        <td><input ref='contact_email' name='contact_email' type='text' /></td>
                                    </tr>
                                    <tr>
                                        <td><label forHtml='discipline'>Discipline</label></td>
                                        <td><input name="discipline" type='text' /></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
            </div>
        );
    }
});
