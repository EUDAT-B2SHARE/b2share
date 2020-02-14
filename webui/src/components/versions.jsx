import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map, List } from 'immutable';
import { DateTimePicker, Multiselect, DropdownList, NumberPicker } from 'react-widgets';
import moment from 'moment';
import { serverCache, browser, Error } from '../data/server';
import { keys, humanSize } from '../data/misc';
import { ReplaceAnimate } from './animate.jsx';
import { Wait, Err } from './waiting.jsx';


const PT = React.PropTypes;


export const Versions = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        let {isDraft, recordID, versions, editing} = this.props;
        if (!versions) {
            return false;
        }
        if (versions && versions.toJS) {
            versions = versions.toJS();
        }
        return (
            <div className="row">
                <div className="col-sm-12" >
                    { isDraft ?
                        <DraftVersions draftID={recordID} versions={versions} style={style} editing={editing}/> :
                        <PublishedVersions recordID={recordID} versions={versions} style={style} editing={editing}/> }
                </div>
            </div>
        );
    }
});


const DraftVersions = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        let {draftID, versions, style, editing} = this.props;
        if (versions.length > 0 && editing){
            return (
                <div style={style}>
                    You are now creating a new version of
                    <a href="#" onClick={e => { e.preventDefault(); browser.gotoRecord(versions[0].id)} }
                       > this published record</a>.
                </div>
            );
        }
        return false;
    },
});

const PublishedVersions = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        let {recordID, versions, className} = this.props;
        const beQuiet = recordID == versions[0].id;

        const thisVersion = versions.find(v => recordID == v.id);
        const VerItemRenderer = ({item}) => {
            const index = item.index + 1;
            const text = index == versions.length ? "Latest Version" : ("Version" + index);
            const creation = moment(item.created).format('ll');
            return (<span>{text} - {creation}</span>);
        };
        const handleVersionChange = (v) => {
            serverCache.getters.record.clear();
            browser.gotoRecord(v.id);
        }

        return (
            <div className={className + " " + (beQuiet ? "" : "alert alert-warning")}>
                <div className="btn newer">
                    { beQuiet ? "" : "This record has newer versions. " }
                </div>

                <div className="dropdown">
                    <DropdownList data={versions} defaultValue={thisVersion}
                        valueComponent={VerItemRenderer} itemComponent={VerItemRenderer}
                        onChange={handleVersionChange}/>
                </div>
            </div>
        );
    },
});
