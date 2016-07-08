import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import moment from 'moment';
import { serverCache, Error } from '../data/server';
import { pairs, humanSize } from '../data/misc';
import { Wait, Err } from './waiting.jsx';
import { ReplaceAnimate } from './animate.jsx';

const PT = React.PropTypes;

export const DropZone = React.createClass({
    propTypes: {
        onFiles: PT.func.isRequired,
    },

    getInitialState: function() {
        return {
            hovering: 0,
        }
    },

    onDragEnter(e) {
        e.preventDefault();
        this.setState({hovering: this.state.hovering+1});
    },

    onDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        return false
    },

    onDragLeave(e) {
        e.preventDefault();
        this.setState({hovering: Math.max(this.state.hovering-1,0)})
    },

    onDrop(e) {
        e.preventDefault();
        this.setState({hovering: 0});
        const files = e.dataTransfer ? e.dataTransfer.files : e.target.files;
        this.props.onFiles(files);
    },

    render: function() {
        const noshow = {width:0, height:0, margin:0, border:'none'};
        const input = this.props.single ?
                <input ref={r=>this.fileinput=r} name="file" type="file" style={noshow} onChange={this.onDrop} tabIndex={-1}/> :
                <input ref={r=>this.fileinput=r} name="file" type="file" style={noshow} onChange={this.onDrop} tabIndex={-1} multiple />;
        return (
            <button className={'dropzone' + (this.state.hovering?' active':'')}
                    onClick={() => {if (this.fileinput) this.fileinput.click()}}
                    onDragEnter={this.onDragEnter} onDragOver={this.onDragOver} onDragLeave={this.onDragLeave} onDrop={this.onDrop}>
                <h3 style={{color:'gray', margin:'2em 2em'}}>Drop files here, or click to select files</h3>
                {input}
            </button>
        );
    },
});

export const B2DropZone = React.createClass({
    propTypes: {
        onFiles: PT.func.isRequired,
    },

    onDrop(e) {
        e.preventDefault();
        this.setState({hovering: 0});
        const files = e.dataTransfer ? e.dataTransfer.files : e.target.files;
        this.props.onFiles(files);
    },

    render: function() {
        return (
            <button className='b2dropzone' onClick={this.open}>
                <img src="/img/b2drop.png"/>
                <h3>Add B2DROP files</h3>
            </button>
        );
    },
});

export const Files = React.createClass({
    propTypes: {
        files: PT.array.isRequired,
        setState: PT.func.isRequired,
        putFile: PT.func.isRequired,
        deleteFile: PT.func.isRequired,
    },

    getInitialState: function() {
        return {
            files: [],
        }
    },

    handleAdd: function(fs, location) {
        const files = this.state.files;
        for (let i = 0; i < fs.length; ++i) {
            const file = fs[i];
            if (file && file.size < 1000 * 1000 && file.type.indexOf('image/') === 0) {
                file.preview = window.URL.createObjectURL(file);
            }
            file.location = location;
            files.push(file);
        }
        this.setState({files:files});
    },

    handleRemove: function(f) {
        if (f.xhr) {
            f.xhr.abort();
        }
        const files = this.state.files.filter(x => x !== f);
        if (files.length !== this.state.files.length) {
            this.setState({files:files});
            if (!files || !files.length ) {
                this.props.setState('done');
            }
        } else if (f.uuid) {
            this.props.deleteFile(f.uuid);
        }
    },

    updateNext() {
        let file = this.state.files.length ? this.state.files[0] : null;
        if (file === null || file.hasOwnProperty('progress')) {
            return;
        }
        file.progress = -1;
        setTimeout(() => {
            // we cannot run this synchronously, because it's called from render and can change state
            file.xhr = this.props.putFile(file, (status, param) => {
                if (status === 'uploading') {
                    file.progress = param;
                    file.error = null;
                    this.props.setState('uploading');
                    this.forceUpdate();
                } else if (status === 'error') {
                    const xhr = param;
                    file.error = xhr.statusText;
                    this.props.setState('error', xhr.statusText);
                    this.forceUpdate();
                } else if (status === 'done') {
                    const files = this.state.files.filter(x => x !== file);
                    this.setState({files:files});
                    if (!files || !files.length ) {
                        this.props.setState('done');
                    }
                }
            });
        }, 1);
    },

    renderProgress: function(f) {
        const widthPercent = f.progress+'%';
        return (
            <div className="row" style={{margin:'5px 0px'}}>
                <div className="col-md-12">
                    <div className="progress" style={{margin:'10px 0', height: 4}}>
                        <div className="progress-bar" role="progressbar" aria-valuenow={f.progress}
                             aria-valuemin="0" aria-valuemax="100" style={{width:widthPercent, height:4}} />
                    </div>
                </div>
            </div>
        );
    },

    renderFile: function(f, i) {
        return (
            <div key={f.name || f.key} className="file">
                <div className="row" style={{}}>
                    <div className="col-sm-12">
                        <dl className="dl-horizontal">
                            <dt>Name</dt>
                            <div>
                                <dd><a href={f.url}>{f.name || f.key}</a></dd>
                                <button type="button" className="btn btn-sm remove" style={{float:'right'}}
                                    onClick={()=>{f.remove=true; this.forceUpdate()}}> <i className="glyphicon glyphicon-remove"/>
                                </button>
                            </div>
                            { f.PID ? <div><dt>PID</dt><dd>{f.PID}</dd></div> : false }
                            { f.mimetype ? <div><dt>Media Type</dt><dd>{f.mimetype}</dd></div> : false }
                            <dt>Size</dt><dd>{humanSize(f.size)}</dd>
                            { f.checksum ? <div><dt>Checksum</dt><dd>{f.checksum}</dd></div> : false }
                            { f.updated ? <div><dt>Updated</dt><dd>{moment(f.updated).format('ll')}</dd></div> : false }
                        </dl>
                    </div>
                </div>
                { f.remove ?
                    <div className="row" style={{borderTop:'2px solid white'}}>
                        <div className="col-sm-10 col-sm-offset-1"> <p style={{textAlign:'center', padding:'1em 0'}}>
                            {f.progress ? 'Stop uploading and remove this file?' : 'Remove this file?'}
                            { f.uuid ? ' This operation will change the record.' : false }
                        </p> </div>
                        <div className="col-sm-4 col-sm-offset-2">
                            <button type="button" className="btn btn-default btn-block btn-sm" onClick={this.handleRemove.bind(this, f)}> Yes </button>
                        </div>
                        <div className="col-sm-4">
                            <button type="button" className="btn btn-default btn-block btn-sm" onClick={()=>{f.remove=false; this.forceUpdate()}}> No </button>
                        </div>
                    </div> : false}
                { f.progress ? this.renderProgress(f) : false }
            </div>
        );
    },

    render: function() {
        this.updateNext();
        return (
            <div>
                { this.props.files.length ?
                    <div className="row">
                        <div className="col-md-12">
                            <h3> Record files </h3>
                        </div>
                    </div> : false }
                <div style={{marginTop:'1em'}} className="fileList">
                    { this.props.files.map(this.renderFile) }
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <h3> { this.props.files.length ? 'Add more files' : 'Add files'} </h3>
                    </div>
                </div>
                <DropZone onFiles={fs => this.handleAdd(fs, 'local')}/>
                <div style={{marginTop:'1em'}}/>
                <B2DropZone onFiles={fs => this.handleAdd(fs, 'b2drop')}/>
                <div className="fileList">
                    { this.state.files.map(this.renderFile) }
                </div>
            </div>
        );
    },
});
