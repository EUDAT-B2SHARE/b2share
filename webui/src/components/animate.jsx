import React from 'react/lib/ReactWithAddons';
const ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;


export const Animate = React.createClass({
    render() {
        const delta = 100;
        return (
            <ReactCSSTransitionGroup component="div" className="animator" transitionName="route"
                    transitionAppear={true} transitionAppearTimeout={delta}
                    transitionEnterTimeout={delta} transitionLeaveTimeout={delta}>
                { this.props.children }
            </ReactCSSTransitionGroup>
        );
    }
});
