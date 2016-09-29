import React from 'react/lib/ReactWithAddons';
import { Link, browserHistory } from 'react-router'

import Toggle from 'react-toggle';
import { HeightAnimate, ReplaceAnimate } from './animate.jsx';


export const RequestSent = React.createClass({

    render() {
        return (
            <div>
                <h3> Your requset has been sent. </h3>
            </div>
        );
    }
});


