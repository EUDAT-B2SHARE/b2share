import React from 'react/lib/ReactWithAddons';
const ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;


export const ReplaceAnimate = React.createClass({
    render() {
        const delta = 100;
        return (<div> { this.props.children } </div>);
        // return (
        //     <ReactCSSTransitionGroup component="div" className="animator" transitionName="route"
        //             transitionAppear={true} transitionAppearTimeout={delta}
        //             transitionEnterTimeout={delta} transitionLeaveTimeout={delta}>

        //     </ReactCSSTransitionGroup>
        // );
    }
});
