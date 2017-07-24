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

    componentWillMount(){
        if(!this.state.extend){
            this.setState({ dataList:this.props.data });
        }
    },

    shouldComponentUpdate(nextProps, nextState) {
        const len = x => (x && x.length !== undefined) ? x.length : 0;
        // fast check, not exact, but should work for our use case
        return nextProps.value !== this.props.value
            || len(nextProps.data) !== len(this.props.data)
            || nextState.extend == true
            || nextState.open !== this.state.open;
    },

    getInitialState(){
        return {
            lastSearch: '',
            results: 0,
            dataList: [],
            extend: false,
            open: false,
        };
    },

    select(val) {
        console.log("val = ", val)
        if(val.id === "-"){
            this.setState({ open: false});
            this.props.onSelect(null);
        }
        else if(val.id === "..." ){
            this.setState({dataList: this.props.list_extend , extend: true, open: true})
        } else {
            this.setState({ open: false});
            this.props.onSelect(val.id);
        }
    },

    filter(item, search) {
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
        let data;
        if(!this.props.list_extend){
            data = this.props.data || [];
        } else {
            data = this.state.dataList;
        }
        if(!this.props.extendable){
            return (
                <div>
                    <DropdownList
                        data={data}
                        valueField='id'
                        textField={this.renderField}
                        value={this.props.value}
                        onChange={this.select}
                        filter={this.filter}
                        caseSensitive={false}
                        minLength={2}
                        busy={busy} />
                </div>
            );
        }else{
            return (
                <div>
                    <DropdownList
                        data={data}
                        open={this.state.open}
                        valueField='id'
                        textField={this.renderField}
                        value={this.props.value}
                        onChange={this.select}
                        filter={this.filter}
                        caseSensitive={false}
                        minLength={2}
                        onClick={ () => { if(!this.state.open){
                                            this.setState({ open: true });
                                        } }}
                        onToggle={()=>{}}
                        busy={busy} />
                </div>
            );
        }
    }
});
