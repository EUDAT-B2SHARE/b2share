var React = require('react');
var render = require('react-dom');


import { Router, Route, IndexRoute, Link } from 'react-router';
import { server } from '../data/server';
import { currentUser } from './user.jsx';
import { Wait } from './waiting.jsx';
import { GenericDomainForm } from './genericdomain.jsx';
import { BbmriDomain } from './bbmridomain.jsx';
import { RDADomain } from './rdadomain.jsx';
import { NrmDomain } from './nrmdomain.jsx';
import { ClarinDomain } from './clarindomain.jsx';
import { DrihmDomain } from './drihmdomain.jsx'

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

export const FileUploadComponent = React.createClass({
  getInitialState: function() {
    return {
      data_uri: null,
    };
  },

    render: function() {
        return (
            <div> 
                <h3>Drag and drop files here</h3>
                <input type="file" onChange={this.handleFile} />
            </div>
        );
    }
});



export const EudatDomainForm = React.createClass({

    render: function() {
        return (
            <div>
                <h3> Generic Domain </h3>
                <GenericDomainForm />
            </div>
        );
    }
});



export const BbmriDomainForm = React.createClass({
    render: function() {
        return (
            <div>
                <BbmriDomain />
            </div>
        );
    }
});


export const RdaDomainForm = React.createClass({
    render: function() {
        return (
            <div>
                <RDADomain />
            </div>
        );
    }
});

export const NrmDomainForm = React.createClass({
    render: function() {
        return (
            <div>
                <NrmDomain />
            </div>
        );
    }
});

export const ClarinDomainForm = React.createClass({
    render: function() {
        return (
            <div>
                <ClarinDomain />
            </div>
        );
    }
});

export const DrihmDomainForm = React.createClass({
    render: function() {
        return (
            <div>
                <DrihmDomain />
            </div>
        );
    }
});


export const SelectDomain = React.createClass({
    getInitialState: function() {
        return { 
            eudatVisible: false,
            bbmriVisible: false,
            rdaVisible: false,
            nrmVisible: false,
            clarinVisible: false,
            drihmVisible: false,
        };
    },


    onClickEudat: function() {
        this.setState({ 
            eudatVisible: !this.state.eudatVisible, 
            bbmriVisible: false,
            rdaVisible: false,
            nrmVisible: false,
            clarinVisible: false,
            drihmVisible: false,
        });
    },

    onClickBbmri: function() {
        this.setState({ 
            bbmriVisible: !this.state.bbmriVisible,
            eudatVisible: false,
            rdaVisible: false,
            nrmVisible: false,
            clarinVisible: false,
            drihmVisible: false,
        });
    },

    onClickRda: function() {
        this.setState({ 
            rdaVisible: !this.state.rdaVisible,
            eudatVisible: false,
            bbmriVisible: false,
            nrmVisible: false,
            clarinVisible: false,
            drihmVisible: false,
        });
    },

    onClickNrm: function() {
        this.setState({ 
            nrmVisible: !this.state.nrmVisible,
            eudatVisible: false,
            bbmriVisible: false,
            rdaVisible: false,
            clarinVisible: false,
            drihmVisible: false,
        });
    },    

    onClickClarin: function() {
        this.setState({ 
            clarinVisible: !this.state.clarinVisible,
            nrmVisible: false,
            eudatVisible: false,
            bbmriVisible: false,
            rdaVisible: false,
            drihmVisible: false,
        });
    },    

    onClickDrihm: function() {
        this.setState({ 
            drihmVisible: !this.state.drihmVisible,
            clarinVisible: false,
            nrmVisible: false,
            eudatVisible: false,
            bbmriVisible: false,
            rdaVisible: false,            
        });
    },        

    render: function() {
        return (
            <div>
                <img width="75" height="51" src={imgUrls.img_eudat} alt="EUDAT" className="img-eudat" onClick={this.onClickEudat}/>
                { this.state.eudatVisible ? <EudatDomainForm /> : null }

                <img width="75" height="51" src={imgUrls.img_bbmri} alt="BBMRI" className="img-bbmri" onClick={this.onClickBbmri}/>
                { this.state.bbmriVisible ? <BbmriDomainForm /> : null }

                <img width="75" height="51" src={imgUrls.img_rda} alt="RDA" className="img-rda" onClick={this.onClickRda}/>
                { this.state.rdaVisible ? <RdaDomainForm /> : null }

                <img width="75" height="51" src={imgUrls.img_nrm} alt="NRM" className="img-nrm" onClick={this.onClickNrm}/>
                { this.state.nrmVisible ? <NrmDomainForm /> : null }

                <img width="75" height="51" src={imgUrls.img_clarin} alt="Clarin" className="img-clarin" onClick={this.onClickClarin}/>
                { this.state.clarinVisible ? <ClarinDomainForm /> : null }

                <img width="75" height="51" src={imgUrls.img_drihm} alt="drihm" className="img-drihm" onClick={this.onClickDrihm}/>
                { this.state.drihmVisible ? <DrihmDomainForm /> : null }
            </div>                        
        );
    }
});




export const Domain = React.createClass({
    render: function() {
        return (
            <div>
                <SelectDomain /> 

            </div>
        );
    }
});



export const Upload = React.createClass({
    handleSubmit: function(e) {

    var self = this;
    var reader = new FileReader();
    var file = e.target.files[0];

    reader.onload = function(upload) {
      self.setState({
        data_uri: upload.target.result,
      });
    }

    reader.readAsDataURL(file);
  },

    render: function() {
        return (
            <div>
                <form onSubmit={this.handleSubmit} encType="multipart/form-data" >
                    <FileUploadComponent />
                    <Domain />
                    <button type="submit">Create the record</button>
                </form>
            </div>
        );
    }
});
