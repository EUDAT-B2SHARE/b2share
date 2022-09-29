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

export const ListAnimate = React.createClass({
    render() {
        const delta = 1000;
        return (
            <ReactCSSTransitionGroup component="div" className="animator" transitionName="list"
                    transitionAppear={true} transitionAppearTimeout={delta}
                    transitionEnterTimeout={delta} transitionLeaveTimeout={delta}>
                { this.props.children }
            </ReactCSSTransitionGroup>
        );
    }
});

export const HeightAnimate = React.createClass({
    getInitialState() {
        return {
            height: 0,
        }
    },

    onHeight() {
        const h = + (this.wrapper ? this.wrapper.clientHeight : 0)
                  + (this.props.delta || 0);
        if (h != this.state.height) {
            this.setState({height: h});
        }
    },

    componentDidMount() {
        this.onHeight();
    },

    componentDidUpdate() {
        this.onHeight();
    },

    render() {
        return (
            <div style={{ height: this.state.height, overflow: 'visible', transition: 'height .2s' }}>
                <div ref={el => this.wrapper = el} style={{margin:0, padding:0}}>
                    { this.props.children }
                </div>
            </div>
        );
    }
});
