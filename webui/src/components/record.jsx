import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { Map } from 'immutable';
import { server } from '../data/server';
import { Wait } from './waiting.jsx';
import { timestamp2str } from '../data/misc.js'
import { Animate } from './animate.jsx';


export const RecordPage = React.createClass({
    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(nextProps) {
        const { id } = nextProps.params;
        server.fetchRecord(id);
        const findFn = (x) => x.get('id') == id;
        const record = nextProps.store.branch('currentRecord');
        if (record.get('id') == id) {
            this.record = record;
        }
    },

    render() {
        if (!this.record || !this.record.valid()) {
            return <Wait/>;
        }
        if (this.props.children) {
            return React.cloneElement(this.props.children, {store: this.props.store, record:this.record.get()})
        }
        return <Record record={this.record.get()} />;
    }
});


const Record = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    renderDates(record) {
        const floatRight={float:'right'};
        const bland={color:'#888'};

        const created = new Date(record.get('created')).toLocaleString();
        const updated = new Date(record.get('updated')).toLocaleString();
        return (
            <div style={floatRight}>
                <p style={floatRight}>
                    <span style={bland}>Created at </span>
                    <span style={{color:'#225'}}>{created}</span>
                </p>
                <div style={{clear:"both"}}/>
                { created != updated
                    ? <p style={floatRight}>
                        <span style={bland}>Last updated at </span>
                        <span style={{color:'#225'}}>{updated}</span>
                      </p>
                    : false }
            </div>
        );
    },

    renderCreators(metadata) {
        const creators = metadata.get('creator');
        if (!creators) {
            return false;
        }

        return (
            <p> <span style={{color:'black'}}> by </span>
                { creators && creators.count()
                    ? creators.map(c => <a className="creator" key={c}> {c}</a>)
                    : <span style={{color:'black'}}> [Unknown] </span>
                }
            </p>
        );
    },

    render() {
        const record = this.props.record;
        const metadata = record.get('metadata') || Map();
        const desc = metadata.get('description') ||"";

        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-sm-10">
                        <div className="large-record">
                            <h3 className="name">{metadata.get('title')}</h3>

                            { this.renderDates(record) }
                            <div style={{clear:"both", height:10}}/>

                            { this.renderCreators(metadata) }

                            <p className="description">{desc.substring(0,200)}</p>
                        </div>
                        </div>
                </div>
            </div>
        );
    }
});

