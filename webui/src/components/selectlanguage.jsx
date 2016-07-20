import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { DropdownList, Combobox } from 'react-widgets';
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

    handleLangChange: function (value) {
        this.setState({
            value
        });
        this.props.onSelectLanguage(value.id); 
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

    render() {
        const langgg = serverCache.getLanguages();
        if (!langgg) {
            return <Wait/>;
        }
        else{
            var def = this.props.defValue;      
            if (!def){
                var defaultVal = langgg[1833].id;  
            }
            else{
                const loc = langgg.filter(i => i.id === def);
                var defaultVal = loc[0].id;
            }

            this.state.value = defaultVal;
         
            return (
                <div >
                    <DropdownList 
                        ref='dropdown'
                        data={langgg} 
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