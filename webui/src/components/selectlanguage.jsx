import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { DropdownList } from 'react-widgets';
import { serverCache, Error } from '../data/server';
import { Wait, Err } from './waiting.jsx';

export const SelectLanguage = React.createClass({
    getInitialState: function(){
        return{
            value: '',
            lastLangSearch: '',
            langNum: 0,
            maxLang: 10,
        };
    },

    handleLangChange: function (val) {
        this.setState({value: val.id});
        this.props.onSelectLanguage(val.id);
    },

    filterLanguage: function (languageName, search){
        // rendering all (>7000) languages is slow, so limit number of responses.

        var ret = false;
        if(search != this.state.lastLangSearch){
            this.state.langNum = 0;
        }

        // search for either language name or iso 639-3 code
        if((languageName.name.toLowerCase().indexOf(search.toLowerCase()) != -1 
            || languageName.id.toLowerCase().indexOf(search.toLowerCase()) != -1)
            && this.state.langNum < this.state.maxLang)
        {
            this.state.langNum = this.state.langNum+1;
            ret = true
        }
        return ret;
    },

    componentWillMount() {
        var def = this.props.defValue || 'eng'; 
        this.setState({value:def});
    },

    render() {
        const languages = serverCache.getLanguages();
        if (!languages) {
            return <Wait/>;
        }
        else{
            return (
                <div >
                    <DropdownList 
                        ref='dropdown'
                        data={languages} 
                        valueField='id'
                        textField={item => item.name}
                        caseSensitive={false} 
                        filter={this.filterLanguage}
                        value={this.state.value}
                        onChange={this.handleLangChange} />
                </div>            
            );
        }
        return (<div ></div>);
    }
});