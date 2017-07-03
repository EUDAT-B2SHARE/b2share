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
        let {isDraft, recordID, versions} = this.props;
        if (!versions) {
            return false;
        }
        if (versions && versions.toJS) {
            versions = versions.toJS();
        }
        const style = {
            float:'right',
            marginTop:'-3em',
            marginBottom:'-3em',
            color:'black',
            padding:'15px',
        };
        return (
            <div className="row">
                <div className="col-sm-12" >
                    { isDraft ?
                        <DraftVersions draftID={recordID} versions={versions} style={style}/> :
                        <PublishedVersions recordID={recordID} versions={versions} style={style}/> }
                </div>
            </div>
        );
    }
});


const DraftVersions = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        let {draftID, versions, style} = this.props;
        if(versions.length > 0){
            return (
                <div style={style}>
                    You are now creating a new version of
                    <Link onClick={e=>browser.gotoRecord(versions[0].id)} href="#"> this published record</Link>.
                </div>
            );
        }
        return false;
    },
});

const PublishedVersions = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    render() {
        let {recordID, versions, style} = this.props;
        const beQuiet = recordID == versions[0].id;
        const versionClass = beQuiet ? "" : "alert alert-warning";

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
            <div className={versionClass} style={style}>
                <div className="btn" style={{display: 'inline-block', color:'black', border: '0px solid #eee'}}>
                    { beQuiet ? "" : "This record has newer versions. " }
                </div>

                <div style={{display: 'inline-block', verticalAlign: 'middle', marginBottom: '1px', padding: '0', width: '17em'}}>
                    <DropdownList data={versions} defaultValue={thisVersion}
                        valueComponent={VerItemRenderer} itemComponent={VerItemRenderer}
                        onChange={handleVersionChange}/>
                </div>
            </div>
        );
    },
});
