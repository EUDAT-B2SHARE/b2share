import React from 'react/lib/ReactWithAddons';
const ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;


export const Animate = React.createClass({
    render() {
        return (
            <ReactCSSTransitionGroup component="div" transitionName="route"
                    transitionAppear={true} transitionAppearTimeout={200}
                    transitionEnterTimeout={200} transitionLeaveTimeout={200}>
                { this.props.children }
            </ReactCSSTransitionGroup>
        );
    }
});
