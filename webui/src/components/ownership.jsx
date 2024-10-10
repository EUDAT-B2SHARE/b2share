import React from 'react/lib/ReactWithAddons';
import { serverCache, notifications, browser, Error, apiUrls } from '../data/server';

export const Ownership = React.createClass({
    getInitialState() {
        this.setWrapperRef = this.setWrapperRef.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
        var state = {
            owners: []
        }

        return state
    },

    getOwners() {
        const addOwners = r => {
            this.setState({ owners: r })
        }
        serverCache.getRecordOwners(this.props.record.get('id'), addOwners)
    },

    componentDidMount() {
        this.getOwners()
        document.addEventListener("mousedown", this.handleClickOutside);
    },

    componentWillUnmount() {
        document.removeEventListener("mousedown", this.handleClickOutside);
    },

    addOwnership() {
        const ownershipSuccess = () => {
            this.setState({ ownershipAdded: true });
            this.getOwners();
        }
        console.log(this.state.ownershipEmail)
        serverCache.addOwnership(this.props.record.get('id'), this.state.ownershipEmail.toLowerCase(), ownershipSuccess, console.error)
    },

    removeOwnersip(email) {
        console.log(email)
        const ownerRemoved = () => {
            this.getOwners()
            this.setState({ ownershipRemoved: true })
        }
        serverCache.removeRecordOwner(this.props.record.get('id'), email, ownerRemoved)
    },

    setWrapperRef(node) {
        this.wrapperRef = node;
    },

    handleClickOutside(event) {
        if (this.wrapperRef && !this.wrapperRef.contains(event.target)) {
            this.props.hide();
        }
    },

    render() {
        return (
            <div id="ownershipChange" className="modal col-lg-8 col-lg-offset-2 col-md-8 col-md-offset-2 col-xs-10 col-xs-offset-1 ownership-modal" style={{ display: "block" }} ref={this.setWrapperRef} >
                <h1 className='col-md-offset-1'>Change ownership for this record</h1>
                <div className='row'>
                    <label htmlFor='ownership-input' className="col-md-1 col-md-offset-1 control-label" style={{ fontWeight: 'bold' }}>
                        <span>
                            Email
                        </span>
                    </label>
                    <div className="col-md-9">
                        <div className="container-fluid" style={{ paddingLeft: 0, paddingRight: 0 }}>
                            <input type="text" className='form-control' id='ownership-input' onChange={(event) => this.setState({ ownershipEmail: event.target.value })} value={this.state.ownershipEmail} />
                        </div>
                    </div>
                </div>
                <div className='row'>
                    <div className='col-md-10 col-md-offset-1' style={{ marginTop: '10px' }}>
                    You are modifying ownership of this record. Record owners have possibility to modify the record metadata, create new versions of this record and modify the ownership of this record. Clicking Save does not remove ownership from you.
                    </div>
                </div>
                <div className='row'>
                    <div className='col-md-10 col-md-offset-1' style={{ marginTop: '10px' }}>
                        <b>Owners:</b>
                    </div>
                </div>
                {this.state.owners.map(o => {
                    const ce_setter = this.state.owners.length <= 1 || o['preset']
                    const ce = !ce_setter ? "" : " disabled"
                    let title = ce ? "Record has to have at least one owner" : "Remove users ownership for this record"
                    if (o['preset']) title = "Can not remove preset owner"
                    return(
                        <div className='row' style={{ marginTop: '10px' }} key={o.email} >
                            <div className='col-md-8 col-md-offset-1'>
                                {o.email}
                            </div>
                            <div className='col-md-1' title={title}>
                                <button type="submit" className={"btn btn-default abuse" + ce} onClick={() => this.removeOwnersip(o.email)}><i className='fa fa-minus' />&nbsp;Remove</button>
                            </div>
                        </div>)
                })}
                <div className='row'>
                    <div className='col-md-10 col-md-offset-1' style={{ marginTop: '10px' }}>
                        If you have any questions, ask FMI data support by clicking "CONTACT" from the menu or send email to b2share-tuki@fmi.fi
                    </div>
                </div>
                <div className="row buttons" style={{ marginTop: '0px' }}>
                    <div className="col-sm-3 col-sm-offset-5" style={{ marginTop: '10px' }}>
                        <button type="submit" className={"btn btn-default btn-block btn-primary"} onClick={this.addOwnership}><i className={"glyphicon glyphicon-send"} />&nbsp;&nbsp;Save</button>
                    </div>
                    <div className="col-sm-3" style={{ marginTop: '10px' }}>
                        <button type="submit" className={"btn btn-default btn-block discard "} onClick={this.props.hide}><i className="glyphicon glyphicon-remove" />&nbsp;Close</button>
                    </div>
                </div>
                <div className='row'>
                    {this.state.ownershipAdded ?
                        <div className="col-md-8">
                            Ownership of the record has been added to {this.state.ownershipEmail}
                        </div>
                        : false}
                </div>
                <div className='row'>
                    {this.state.ownershipRemoved ?
                        <div className="col-md-8">
                            Ownership removed
                        </div>
                        : false}
                </div>
            </div>
        )
    },
})
