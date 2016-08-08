import React from 'react/lib/ReactWithAddons';

const PT = React.PropTypes;

export const SelectLicense = React.createClass({
    propTypes: {
        title: PT.string.isRequired,
        onSelect: PT.func.isRequired,
        setModal: PT.func.isRequired,
    },

    onReceiveMessage(event) {
        var origin = event.origin || event.originalEvent.origin;
        if (origin === window.location.origin) {
            this.props.setModal(false);
            if (event.data) {
                this.props.onSelect(event.data);
            }
        }
    },

    componentWillMount() {
        window.addEventListener("message", this.onReceiveMessage, false);
    },

    componentWillUnmount() {
        window.removeEventListener("message", this.onReceiveMessage);
    },

    render(type, getValue, setValue, title) {
        const licenseModal = <iframe src="/license-selector.html"
                                     style={{border:'none'}}
                                     frameborder="0"
                                     width="100%"
                                     height="900px"
                                     marginheight="0"
                                     marginwidth="0"
                                     scrolling="auto" />;
        return (
            <a className="input-group-addon" href="#" style={{backgroundColor:'white'}}
               onClick={() => this.props.setModal(licenseModal)} >
                    <span className="glyphicon glyphicon-copyright-mark" aria-hidden="true"/>
                    {" "}
                    {this.props.title}
            </a>
        );
    },
});