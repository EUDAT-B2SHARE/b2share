import React from 'react/lib/ReactWithAddons';

import { Error } from '../data/server';



export function renderSmallCommunity(community, selected, onClickFn) {
    const klass = selected ? "active": "inactive";
    if (!community || community instanceof Error) {
        return false;
    }
    return (
        <a href="#" key={community.get('id')}
                className={"community-small " + klass}
                title={community.get('description')}
                onClick={onClickFn ? onClickFn : ()=>{}}>
            <p className="name">{community.get('name')}</p>
            <img className="logo" src={community.get('logo')}/>
        </a>
    );
}

export const FocusManager = React.createClass({
    getInitialState() {
        return {
            onBlur: () => null,
            onFocus: () => null
        }
    },

    canBlur: true,

    handleMouseDown() {
        this.canBlur = false
    },

    handleMouseUp() {
        this.canBlur = true
    },

    handleBlur(event) {
        if (this.canBlur) {
            this.props.onBlur(event)
        }
    },

    handleKeyDown(event) {
        if (event.key === 'Escape') {
            this.props.onBlur(event)
        }
    },

    render() {
        return this.props.children({
            onBlur: this.handleBlur,
            onFocus: this.props.onFocus,
            onMouseDown: this.handleMouseDown,
            onMouseUp: this.handleMouseUp,
            onKeyDown: this.handleKeyDown,
        })
    }
});
