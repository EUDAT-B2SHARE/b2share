import React from 'react/lib/ReactWithAddons';
import { DropdownList } from 'react-widgets';
import { serverCache } from '../data/server';

const PT = React.PropTypes;

export const SelectBig = React.createClass({
    propTypes: {
        data: PT.array,
        value: PT.string,
        onSelect: PT.func.isRequired,
    },

    maxResults: 50,

    shouldComponentUpdate: function(nextProps, nextState) {
        const len = x => (x && x.length !== undefined) ? x.length : 0;
        // fast check, not exact, but should work for our use case
        return nextProps.value !== this.props.value
            || len(nextProps.data) !== len(this.props.data)
            || nextProps.readOnly !== this.props.readOnly;
    },

    getInitialState: function(){
        return {
            lastSearch: '',
            results: 0,
        };
    },

    select: function (val) {
        this.props.onSelect(val.id);
    },

    filter: function (item, search) {
        // rendering all inputs is slow (>7000 for languages)
        // so limit number of responses to maxResults
        if (search !== this.state.lastSearch) {
            this.state.results = 0;
            this.state.lastSearch = search;
        }
        if (this.state.results < this.maxResults) {
            const id = item.id.toLowerCase();
            const name = item.name.toLowerCase();
            var term = search.toLowerCase();
            if (name.indexOf(term) != -1 || id.indexOf(term) != -1) {
                this.state.results ++;
                return true;
            }
        }
        return false;
    },

    renderField(item) {
        if (item === undefined || item === null) {
            return "";
        }
        if (item.id === item.name) {
            return item.name;
        }
        return item.name + " ["+item.id+"]";
    },

    render() {
        const busy = !this.props.data;
        const data = this.props.data || [];
        return (
            <DropdownList
                data={data}
                valueField='id'
                textField={this.renderField}
                value={this.props.value}
                onChange={this.select}
                filter={this.filter}
                caseSensitive={false}
                minLength={2}
                busy={busy}
                disabled={this.props.readOnly} />
        );
    }
});
