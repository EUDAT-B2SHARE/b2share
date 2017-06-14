import React from 'react/lib/ReactWithAddons';
import { serverCache, notifications, browser } from '../data/server';

export const AccessRequest = React.createClass({
    mixins: [React.addons.LinkedStateMixin],

    getInitialState() {
        return {
            sending: false,
        }
    },

    sendRequestAccessFile(event) {
        event.preventDefault();
        var data = {
            message: this.message.value,
            name: this.name.value,
            affiliation: this.affiliation.value,
            email: this.email.value,
            address: this.address.value,
            city: this.city.value,
            country: this.country.value,
            zipcode: this.zipcode.value,
            phone: this.phone.value,
        };
        this.setState({sending: true});
        serverCache.accessRequest(this.props.params.id, data,
            () => {
                browser.gotoRecord(this.props.params.id);
                notifications.success("The access request has been successfully sent");
            },
            () => {
                notifications.danger("The access request could not be sent. " +
                                     "Please try again or consult the site administrator");
                this.setState({sending:false});
            });
    },

   render: function() {
        const gap = {marginTop:'1em', marginBottom:'1em'};
        if (this.state.sending) {
            return (
                <div><p>Please wait. Your request is currently being sent.</p></div>
            );
        }

        return (
            <div>
            	<form className="form-horizontal" onSubmit={this.sendRequestAccessFile}>
                    <div className='row'>
                    	<div className="col-sm-4" >
                        	<label forHtml='full_record_link' >Full link to the record </label>
                        </div>
                        <div className="col-sm-6" >
                        	<input ref='full_record_link' className="form-control" name='full_record_link' type='text'
                                value={browser.getRecordURL(this.props.params.id)} readOnly="true" size='60' />
                    	</div>
                    </div>

                    <div className='row' style={gap}>
                        <div className="col-sm-4" >
                            <label forHtml='message'>Access request message</label>
                        </div>
                        <div className=" col-sm-8" >
                            <textarea ref={(ref) => this.message = ref} id="message" name='message' className="form-control" type='textarea' rows="4" cols="50"  required/>
                        </div>
                    </div>

                    <div className='row' style={gap}>
                        <div className="col-sm-4">
                            <label forHtml='name'>Your full name</label>
                        </div>
                        <div className=" col-sm-8" >
                            <input ref={(ref) => this.name = ref} id='name' name='name' className="form-control" type='text'  required />
                        </div>
                    </div>

                    <div className='row' style={gap}>
                        <div className="col-sm-4" >
                            <label forHtml='affiliation'>Your affiliation</label>
                        </div>
                        <div className=" col-sm-8" >
                            <input ref={(ref) => this.affiliation = ref} id='affiliation'  name='affiliation' className="form-control" type='text' required />
                        </div>
                    </div>

                    <div className='row' style={gap}>
                        <div className="col-sm-4">
                            <label forHtml='email'>Your email</label>
                        </div>
                        <div className=" col-sm-8" >
                            <input ref={(ref) => this.email = ref} id='email' name='email' className="form-control" type='email' required />
                        </div>
                    </div>

                    <div className='row'  style={gap}>
                        <div className="col-sm-4">
                            <label forHtml='address'>Your address</label>
                        </div>
                        <div className=" col-sm-8" >
                            <input ref={(ref) => this.address = ref} id='address' name='address' className="form-control" type='text'  required />
                        </div>
                    </div>

                    <div className='row'  style={gap}>
                        <div className="col-sm-4">
                            <label forHtml='city'>City</label>
                        </div>
                        <div className=" col-sm-8" >
                            <input ref={(ref) => this.city = ref} id='city' name='city' className="form-control" type='text'  required />
                        </div>
                    </div>

                    <div className='row'  style={gap}>
                        <div className="col-sm-4">
                            <label forHtml='country'>Country</label>
                        </div>
                        <div className=" col-sm-8" >
                        <select ref={(ref) => this.country = ref} id='country' name='country' className="form-control" defaultValue=""  required >
                            <option value=""> Choose country </option>
                            <option value="Afghanistan" >Afghanistan</option>
                            <option value="Albania" >Albania</option>
                            <option value="Algeria" >Algeria</option>
                            <option value="Andorra" >Andorra</option>
                            <option value="Antigua and Barbuda" >Antigua and Barbuda</option>
                            <option value="Argentina" >Argentina</option>
                            <option value="Armenia" >Armenia</option>
                            <option value="Australia" >Australia</option>
                            <option value="Austria" >Austria</option>
                            <option value="Azerbaijan" >Azerbaijan</option>
                            <option value="Bahamas" >Bahamas</option>
                            <option value="Bahrain" >Bahrain</option>
                            <option value="Bangladesh" >Bangladesh</option>
                            <option value="Barbados" >Barbados</option>
                            <option value="Belarus" >Belarus</option>
                            <option value="Belgium" >Belgium</option>
                            <option value="Belize" >Belize</option>
                            <option value="Benin" >Benin</option>
                            <option value="Bhutan" >Bhutan</option>
                            <option value="Bolivia" >Bolivia</option>
                            <option value="Bosnia and Herzegovina" >Bosnia and Herzegovina</option>
                            <option value="Botswana" >Botswana</option>
                            <option value="Brazil" >Brazil</option>
                            <option value="Brunei" >Brunei</option>
                            <option value="Bulgaria" >Bulgaria</option>
                            <option value="Burkina Faso" >Burkina Faso</option>
                            <option value="Burundi" >Burundi</option>
                            <option value="Cambodia" >Cambodia</option>
                            <option value="Cameroon" >Cameroon</option>
                            <option value="Canada" >Canada</option>
                            <option value="Cape Verde" >Cape Verde</option>
                            <option value="Central African Republic" >Central African Republic</option>
                            <option value="Chad" >Chad</option>
                            <option value="Chile" >Chile</option>
                            <option value="China" >China</option>
                            <option value="Colombia" >Colombia</option>
                            <option value="Comoros" >Comoros</option>
                            <option value="Congo" >Congo</option>
                            <option value="Costa Rica" >Costa Rica</option>
                            <option value="Côte d Ivoire" >Côte d Ivoire</option>
                            <option value="Croatia" >Croatia</option>
                            <option value="Cuba" >Cuba</option>
                            <option value="Cyprus" >Cyprus</option>
                            <option value="Czech Republic" >Czech Republic</option>
                            <option value="Denmark" >Denmark</option>
                            <option value="Djibouti" >Djibouti</option>
                            <option value="Dominica" >Dominica</option>
                            <option value="Dominican Republic" >Dominican Republic</option>
                            <option value="East Timor" >East Timor</option>
                            <option value="Ecuador" >Ecuador</option>
                            <option value="Egypt" >Egypt</option>
                            <option value="El Salvador" >El Salvador</option>
                            <option value="Equatorial Guinea" >Equatorial Guinea</option>
                            <option value="Eritrea" >Eritrea</option>
                            <option value="Estonia" >Estonia</option>
                            <option value="Ethiopia" >Ethiopia</option>
                            <option value="Fiji" >Fiji</option>
                            <option value="Finland" >Finland</option>
                            <option value="France" >France</option>
                            <option value="Gabon" >Gabon</option>
                            <option value="Gambia" >Gambia</option>
                            <option value="Georgia" >Georgia</option>
                            <option value="Germany" >Germany</option>
                            <option value="Ghana" >Ghana</option>
                            <option value="Greece" >Greece</option>
                            <option value="Grenada" >Grenada</option>
                            <option value="Guatemala" >Guatemala</option>
                            <option value="Guinea" >Guinea</option>
                            <option value="Guinea-Bissau" >Guinea-Bissau</option>
                            <option value="Guyana" >Guyana</option>
                            <option value="Haiti" >Haiti</option>
                            <option value="Honduras" >Honduras</option>
                            <option value="Hong Kong" >Hong Kong</option>
                            <option value="Hungary" >Hungary</option>
                            <option value="Iceland" >Iceland</option>
                            <option value="India" >India</option>
                            <option value="Indonesia" >Indonesia</option>
                            <option value="Iran" >Iran</option>
                            <option value="Iraq" >Iraq</option>
                            <option value="Ireland" >Ireland</option>
                            <option value="Israel" >Israel</option>
                            <option value="Italy" >Italy</option>
                            <option value="Jamaica" >Jamaica</option>
                            <option value="Japan" >Japan</option>
                            <option value="Jordan" >Jordan</option>
                            <option value="Kazakhstan" >Kazakhstan</option>
                            <option value="Kenya" >Kenya</option>
                            <option value="Kiribati" >Kiribati</option>
                            <option value="North Korea" >North Korea</option>
                            <option value="South Korea" >South Korea</option>
                            <option value="Kuwait" >Kuwait</option>
                            <option value="Kyrgyzstan" >Kyrgyzstan</option>
                            <option value="Laos" >Laos</option>
                            <option value="Latvia" >Latvia</option>
                            <option value="Lebanon" >Lebanon</option>
                            <option value="Lesotho" >Lesotho</option>
                            <option value="Liberia" >Liberia</option>
                            <option value="Libya" >Libya</option>
                            <option value="Liechtenstein" >Liechtenstein</option>
                            <option value="Lithuania" >Lithuania</option>
                            <option value="Luxembourg" >Luxembourg</option>
                            <option value="Macedonia" >Macedonia</option>
                            <option value="Madagascar" >Madagascar</option>
                            <option value="Malawi" >Malawi</option>
                            <option value="Malaysia" >Malaysia</option>
                            <option value="Maldives" >Maldives</option>
                            <option value="Mali" >Mali</option>
                            <option value="Malta" >Malta</option>
                            <option value="Marshall Islands" >Marshall Islands</option>
                            <option value="Mauritania" >Mauritania</option>
                            <option value="Mauritius" >Mauritius</option>
                            <option value="Mexico" >Mexico</option>
                            <option value="Micronesia" >Micronesia</option>
                            <option value="Moldova" >Moldova</option>
                            <option value="Monaco" >Monaco</option>
                            <option value="Mongolia" >Mongolia</option>
                            <option value="Montenegro" >Montenegro</option>
                            <option value="Morocco" >Morocco</option>
                            <option value="Mozambique" >Mozambique</option>
                            <option value="Myanmar" >Myanmar</option>
                            <option value="Namibia" >Namibia</option>
                            <option value="Nauru" >Nauru</option>
                            <option value="Nepal" >Nepal</option>
                            <option value="Netherlands" >Netherlands</option>
                            <option value="New Zealand" >New Zealand</option>
                            <option value="Nicaragua" >Nicaragua</option>
                            <option value="Niger" >Niger</option>
                            <option value="Nigeria" >Nigeria</option>
                            <option value="Norway" >Norway</option>
                            <option value="Oman" >Oman</option>
                            <option value="Pakistan" >Pakistan</option>
                            <option value="Palau" >Palau</option>
                            <option value="Panama" >Panama</option>
                            <option value="Papua New Guinea" >Papua New Guinea</option>
                            <option value="Paraguay" >Paraguay</option>
                            <option value="Peru" >Peru</option>
                            <option value="Philippines" >Philippines</option>
                            <option value="Poland" >Poland</option>
                            <option value="Portugal" >Portugal</option>
                            <option value="Puerto Rico" >Puerto Rico</option>
                            <option value="Qatar" >Qatar</option>
                            <option value="Romania" >Romania</option>
                            <option value="Russia" >Russia</option>
                            <option value="Rwanda" >Rwanda</option>
                            <option value="Saint Kitts and Nevis" >Saint Kitts and Nevis</option>
                            <option value="Saint Lucia" >Saint Lucia</option>
                            <option value="Saint Vincent and the Grenadines" >Saint Vincent and the Grenadines</option>
                            <option value="Samoa" >Samoa</option>
                            <option value="San Marino" >San Marino</option>
                            <option value="Sao Tome and Principe" >Sao Tome and Principe</option>
                            <option value="Saudi Arabia" >Saudi Arabia</option>
                            <option value="Senegal" >Senegal</option>
                            <option value="Serbia and Montenegro" >Serbia and Montenegro</option>
                            <option value="Seychelles" >Seychelles</option>
                            <option value="Sierra Leone" >Sierra Leone</option>
                            <option value="Singapore" >Singapore</option>
                            <option value="Slovakia" >Slovakia</option>
                            <option value="Slovenia" >Slovenia</option>
                            <option value="Solomon Islands" >Solomon Islands</option>
                            <option value="Somalia" >Somalia</option>
                            <option value="South Africa" >South Africa</option>
                            <option value="Spain" >Spain</option>
                            <option value="Sri Lanka" >Sri Lanka</option>
                            <option value="Sudan" >Sudan</option>
                            <option value="Suriname" >Suriname</option>
                            <option value="Swaziland" >Swaziland</option>
                            <option value="Sweden" >Sweden</option>
                            <option value="Switzerland" >Switzerland</option>
                            <option value="Syria" >Syria</option>
                            <option value="Taiwan" >Taiwan</option>
                            <option value="Tajikistan" >Tajikistan</option>
                            <option value="Tanzania" >Tanzania</option>
                            <option value="Thailand" >Thailand</option>
                            <option value="Togo" >Togo</option>
                            <option value="Tonga" >Tonga</option>
                            <option value="Trinidad and Tobago" >Trinidad and Tobago</option>
                            <option value="Tunisia" >Tunisia</option>
                            <option value="Turkey" >Turkey</option>
                            <option value="Turkmenistan" >Turkmenistan</option>
                            <option value="Tuvalu" >Tuvalu</option>
                            <option value="Uganda" >Uganda</option>
                            <option value="Ukraine" >Ukraine</option>
                            <option value="United Arab Emirates" >United Arab Emirates</option>
                            <option value="United Kingdom" >United Kingdom</option>
                            <option value="United States" >United States</option>
                            <option value="Uruguay" >Uruguay</option>
                            <option value="Uzbekistan" >Uzbekistan</option>
                            <option value="Vanuatu" >Vanuatu</option>
                            <option value="Vatican City" >Vatican City</option>
                            <option value="Venezuela" >Venezuela</option>
                            <option value="Vietnam" >Vietnam</option>
                            <option value="Yemen" >Yemen</option>
                            <option value="Zambia" >Zambia</option>
                            <option value="Zimbabwe" >Zimbabwe</option>
                        </select>
                        </div>
                    </div>

                    <div className='row'  style={gap}>
                        <div className="col-sm-4">
                            <label forHtml='zipcode'>Zip code</label>
                        </div>
                        <div className=" col-sm-8" >
                            <input ref={(ref) => this.zipcode = ref} id='zipcode' name='zipcode' className="form-control" type='text'  required />
                        </div>
                    </div>

                    <div className='row'  style={gap}>
                        <div className="col-sm-4">
                            <label forHtml='phone'>Your phone number</label>
                        </div>
                        <div className=" col-sm-8" >
                            <input ref={(ref) => this.phone = ref} id='phone' name="phone" type='text'  pattern="[0-9]*" className="form-control" title= "Numbers Only" required />
                        </div>
                    </div>

                    <div className='row' style={gap}>
                        <div className="col-sm-offset-2 col-sm-8">
                            <button type="submit" className="btn btn-primary btn-default btn-block" >Send</button>
                        </div>
                    </div>
                </form>
            </div>
        );
    }
});
