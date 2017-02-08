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
