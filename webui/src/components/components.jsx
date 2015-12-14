import React from 'react';
import ReactDOM from 'react-dom';

const PT = React.PropTypes;

const ReactCSSTransitionGroup = React.addons.ReactCSSTransitionGroup;
const ReactTransitionGroup = React.addons.TransitionGroup;

///////////////////////////////////////////////////////////////////////////////

function setState(state) {
    var t = this;
    if (t && t != window && t.setState) {
        t.setState(state);
    }
}

function humanSize(sz) {
    let K = 1000, M = K*K, G = K*M, T = K*G;

    if (sz < K) {
        return [sz,'B '];
    } else if (sz < M) {
        return [(sz/K).toFixed(1), 'KB'];
    } else if (sz < G) {
        return [(sz/M).toFixed(1), 'MB'];
    } else if (sz < T) {
        return [(sz/G).toFixed(1), 'GB'];
    } else {
        return [(sz/T).toFixed(1), 'TB'];
    }
}

function pairs(o) {
    var a = []
    for (var k in o) {
        if (o.hasOwnProperty(k)) {
            a.push([k, o[k]]);
        }
    }
    return a;
}

///////////////////////////////////////////////////////////////////////////////
// Slides

let JQuerySlide = React.createClass({
	componentWillEnter: function(callback){
		var el = jQuery(this.getDOMNode());
		el.css("display", "none");
		el.slideDown(500, callback);
		$el.slideDown(function(){
			callback();
		});
	},
	componentWillLeave: function(callback){
		var $el = jQuery(this.getDOMNode());
		$el.slideUp(function(){
			callback();
		});
	},
	render: function(){
		return this.transferPropsTo(this.props.component({style: {display: 'none'}}));
	}
});

let JQueryFade = React.createClass({
	componentWillEnter: function(callback){
		var el = jQuery(this.getDOMNode());
		el.css("display", "none");
		el.fadeIn(500, callback);
	},
	componentWillLeave: function(callback){
		jQuery(this.getDOMNode()).fadeOut(500, callback);
	},
	render: function() {
		return this.props.children;
	}
});


///////////////////////////////////////////////////////////////////////////////
// Error Pane

let ErrorPane = React.createClass({
	propTypes: {
		errorMessages: PT.array.isRequired,
	},

	renderErrorMessage: function(errorMessage, index) {
		return errorMessage ?
			<JQueryFade key={index}>
				<div key={index} className="errorMessage">{errorMessage}</div>
			</JQueryFade> :
			false;
	},

	render: function() {
		return	<div className="container errorDiv">
					<div className="row errorRow">
						<ReactTransitionGroup component="div">
							{this.props.errorMessages.map(this.renderErrorMessage)}
						</ReactTransitionGroup>
					</div>
				</div>;
	}
});

///////////////////////////////////////////////////////////////////////////////
// Modal


let Modal = React.createClass({
	propTypes: {
		title: PT.string.isRequired,
	},
	componentDidMount: function() {
		$(this.getDOMNode()).modal({background: true, keyboard: true, show: false});
	},
	componentWillUnmount: function() {
		$(this.getDOMNode()).off('hidden');
	},
	handleClick: function(e) {
		e.stopPropagation();
	},
	render: function() {
		return (
			<div onClick={this.handleClick} className="modal fade" role="dialog" aria-hidden="true">
				<div className="modal-dialog">
					<div className="modal-content">
						<div className="modal-header">
							<button type="button" className="close" data-dismiss="modal">
								<span aria-hidden="true">&times;</span>
								<span className="sr-only">Close</span>
							</button>
							<h2 className="modal-title">{this.props.title}</h2>
						</div>
						<div className="modal-body">
							{this.props.children}
						</div>
						<div className="modal-footer">
							<button type="button" className="btn btn-default" data-dismiss="modal">Close</button>
						</div>
					</div>
				</div>
			</div>
		);
	}
});


///////////////////////////////////////////////////////////////////////////////
// Media

let Media = React.createClass({
    propTypes: {
        src: PT.string.isRequired,
        type: PT.string.isRequired,
        name: PT.string.isRequired,
        size: PT.string.isRequired,
    },

    renderByType: function(src, type) {
        if (type.startsWith("image/")) {
            return <img className='img-thumbnail img-responsive' src={src}/>;
        } else {
            return (
                <div className='img-thumbnail img-empty' src={src}>
                    <div className='fa fa-file-text fa-3x'/>
                </div>
            );
        }
    },

    render: function() {
        return  (
            <div className='media-wrapper'>
                <div className="media-img col-sm-4">
                    {this.renderByType(this.props.src, this.props.type)}
                </div>
                <div className='media-body col-sm-8'>
                    <p className='file-name' style={{wordWrap: 'break-word'}}>{this.props.name}</p>
                    <p className='file-type'>{this.props.type}</p>
                    <p className='file-size'>{this.props.size}</p>
                </div>
            </div>
        )
    }
});
