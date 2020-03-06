import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { timestamp2str } from '../data/misc.js'
import { Error } from '../data/server';
import { Map, List } from 'immutable';
import { ImplodedList } from './common.jsx';


export const LatestRecords = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    propTypes: {
        records: React.PropTypes.object.isRequired,
        community: React.PropTypes.string
    },

    renderCreators(creators) {
        if (!creators || !creators.count()) {
            return false;
        }
        return (
            <span>
                <span style={{color:'black'}}> by </span>
                <ImplodedList data={creators.map(c => <span className="creator" key={c.get('creator_name')}> {c.get('creator_name')}</span>)}/>
            </span>
        );
    },

    renderRecord(record) {
        function first(map, key) {
            const x = map.get(key);
            return (x && x.count && x.count()) ? x.get(0) : Map();
        }
        const id = record.get('id');
        const created = record.get('created');
        const updated = record.get('updated');
        const metadata = record.get('metadata') || Map();
        const title = first(metadata, 'titles').get('title') || "";
        const description = first(metadata, 'descriptions').get('description') ||"";
        const creators = metadata.get('creators') || List();
        return (
            <div className="record col-md-6" key={record.get('id')}>
                <Link to={'/records/'+id}>
                    <p className="name">{title}</p>
                    <p>
                        <span className="date">{timestamp2str(created)}</span>
                        {this.renderCreators(creators)}
                    </p>
                    <p className="description">{description.substring(0,200)}</p>
                </Link>
            </div>
        );
    },

    render() {
        if (this.props.records instanceof Error) {
            return false;
        }
        let params = this.props.community ? {community: this.props.community} : {};
        if (!this.props.records.count()) {
          return (
            <div/>
          );
        }
        return (
            <div>
                <h3>{ this.props.title ? this.props.title : "Latest records" }</h3>
                <div className="row">
                    { this.props.records.map(this.renderRecord) }
                </div>
                <div className="row">
                    <div className="col-sm-offset-6 col-sm-5" style={{marginTop:'1em', marginBottom:'1em',}}>
                    <Link to={{ pathname: "/records", query: params}} className="btn btn-default btn-block"> More Records ... </Link>
                    </div>
                </div>
                <hr/>
            </div>
        );
    }
});

