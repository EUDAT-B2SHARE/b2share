import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { fromJS, OrderedMap, Map } from 'immutable';
import moment from 'moment';
import { serverCache, Error } from '../data/server';
import { pairs, humanSize } from '../data/misc';
import { Wait, Err } from './waiting.jsx';
import { ReplaceAnimate } from './animate.jsx';

const PT = React.PropTypes;

const LocalDropZone = React.createClass({
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


const B2DropZone = React.createClass({
    propTypes: {
        onFiles: PT.func.isRequired,
    },

    getInitialState: function() {
        return {
            state: 'login',
            username: "",
            password: "",
            files: [],
        }
    },

    onB2DropFiles(parentIndex, data) {
        data.files.sort((a, b) => a.name<b.name ? -1 : a.name==b.name ? 0 : 1);
        const files = [];
        const indent = parentIndex >= 0 ? (this.state.files[parentIndex].indent+1) : 0;
        data.files.forEach(f => { if (f.isdir) files.push(f) });
        data.files.forEach(f => {
            if (!f.isdir) { f.selected = false; files.push(f); }
        });
        if (parentIndex >= 0) {
            this.state.files[parentIndex].children = files.length;
        }
        files.forEach(f => f.indent = indent);
        this.state.files.splice(parentIndex + 1, 0, ...files);
        this.setState({state: 'files', files: this.state.files});
    },

    onB2DropError(xhr) {
        if (xhr.status === 401) {
            this.setState({error:'The username or password is incorrect, please try again.'});
        } else if (xhr.status === 403) {
            this.setState({error:'Forbidden access to the resource.'});
        } else {
            this.setState({error:'Error logging in, please try again.'});
        }
    },

    authenticate() {
        serverCache.b2dropInit(this.state.username, this.state.password,
                               this.onB2DropFiles.bind(this, -1), this.onB2DropError);
    },

    handleFileClick(file, index) {
        if (file.isdir) {
            if (file.children == undefined) {
                serverCache.b2dropList(file.path,
                                       this.onB2DropFiles.bind(this, index),
                                       this.onB2DropError)
            } else {
                const files = this.state.files.splice(index+1, file.children);
                file.children = undefined;
                this.setState({files:this.state.files});
            }
        } else {
            file.selected = !file.selected;
            this.setState({files:this.state.files});
        }
    },

    handleSelectFiles() {
        const files = this.state.files.filter(f => f.selected);
        this.props.onFiles(files);
        this.props.close();
    },

    renderLogin: function() {
        const instyle={
            fontSize: 20,
            margin: 0,
            padding: '11px 10px 9px',
            borderRadius: '3px',
            width: 280,
        };
        const submitstyle={
            position: 'absolute',
            right: 0,
            top: 4,
            border: 'none',
            backgroundColor: 'transparent',
            padding: '10px 20px',
            width: 'auto',
            float: 'right',
            color: '#ddd',
        }
        return (
            <form style={{width:280, margin:'30px auto'}} onSubmit={e => {e.preventDefault(); this.authenticate()}}>
                <input type="text" name="user" id="user" placeholder="Username"
                    style={Object.assign({}, instyle, {borderBottomLeftRadius: 0, borderBottomRightRadius: 0 })}
                    value={this.state.username} onChange={e => this.setState({username: e.target.value})}
                    autofocus="" autocomplete="on" autocapitalize="off" autocorrect="off" required=""/>
                <label for="user" style={{display:'none'}}>Username</label>

                <div style={{position:'relative'}}>
                    <input type="password" name="password" id="password" placeholder="Password"
                        style={Object.assign({}, instyle, {marginTop:-1, borderTopLeftRadius: 0, borderTopRightRadius: 0 })}
                        value={this.state.password} onChange={e => this.setState({password: e.target.value})}
                        autocomplete="on" autocapitalize="off" autocorrect="off" required=""/>
                    <label for="password" style={{display:'none'}}>Password</label>
                    <button type="submit" style={submitstyle}>
                        <i className="glyphicon glyphicon-arrow-right"/>
                    </button>
                </div>
            </form>
        );
    },

    renderFile: function(file, index) {
        const iconClass = !file.isdir ? "glyphicon-file"
                            : file.children == undefined ? "glyphicon-folder-close"
                            : "glyphicon-folder-open";
        const size = file.size ? humanSize(file.size) : "";
        const date = moment(file.date).format('ll');
        const indentStyle = {paddingLeft: (3*file.indent)+'em'};
        const handlerStyle = {width:20, background:'none', border:'none', fontSize:20, padding:0};
        return (
            <li className="row file" key={file.path} style={{lineHeight:2}} onClick={this.handleFileClick.bind(this, file, index)}>
                <div className="col-sm-6">
                    <span style={indentStyle}/>
                    { file.isdir ?
                        file.children == undefined ?
                            <button style={handlerStyle}>+</button> :
                            <button style={handlerStyle}>-</button> :
                        <input type="checkbox" style={{width:20}} checked={file.selected}/> }
                    <span className={"glyphicon "+iconClass} aria-hidden={true} /> {file.name}
                </div>
                <div className="col-sm-3">{size}</div>
                <div className="col-sm-3">{date}</div>
            </li>
        );
    },

    renderFiles: function() {
        return (
            <div style={{margin:'1em'}}>
                <ol className="list-unstyled fileList" style={{textAlign:'left', minHeight:'30em'}}>
                    <li className="heading row" style={{padding:'0.5em 0'}}>
                        <div className="col-sm-6" style={{fontWeight:'bold'}}>File Name</div>
                        <div className="col-sm-3" style={{fontWeight:'bold'}}>Size</div>
                        <div className="col-sm-3" style={{fontWeight:'bold'}}>Date</div>
                    </li>
                    {this.state.files.map(this.renderFile)}
                </ol>
                <div style={{textAlign:'center', margin:'2em'}}>
                    <button className="btn btn-primary" onClick={this.handleSelectFiles}>
                        Copy selected files to B2SHARE
                    </button>
                    {" "}
                    <button className="btn btn-default" onClick={e => this.props.close()}>
                        Cancel
                    </button>
                </div>
            </div>
        );
    },

    render: function() {
        const closeStyle = {
            display:'inline',
            float:'right',
            cursor:'pointer',
            fontSize: 24,
            fontWeight: 'bold',
            marginTop:-8,
        };
        return (
            <div className="row">
                <div className="col-xs-12">
                    <div className="panel panel-default b2droppanel">
                        <div className="panel-heading">
                            <div style={closeStyle} onClick={e => this.props.close()}>×</div>
                            <img src="/img/b2drop.png" style={{display:'inline', float:'left', height:30}}/>
                            <div style={{textAlign:'center'}}>
                                <h3 style={{display:'inline'}}>{" "}
                                    { this.state.state === 'login' ? "Login to B2DROP" : "Select B2DROP files" }
                                </h3>
                            </div>
                        </div>
                        { this.state.state === 'login' ? this.renderLogin() : this.renderFiles() }
                    </div>
                </div>
            </div>
        );
    },
});


export const EditFiles = React.createClass({
    propTypes: {
        files: PT.array.isRequired,
        record: PT.object.isRequired,
        setState: PT.func.isRequired,
        setModal: PT.func.isRequired,
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
            if (file && file.size < 1000 * 1000 && file.type && file.type.indexOf('image/') === 0) {
                file.preview = window.URL.createObjectURL(file);
            }
            file.location = location;
            files.push(file);
        }
        this.setState({files:files});
    },

    removeUploadFile: function(f) {
        if (f.xhr) {
            f.xhr.abort();
        }
        const files = this.state.files.filter(x => x !== f);
        if (files.length !== this.state.files.length) {
            this.setState({files});
            if (!files || !files.length ) {
                this.props.setState('done');
            }
        }
    },

    removeRecordFile: function(f) {
        serverCache.deleteFile(this.props.record, f.key);
    },

    transferFileCallback(file, status, param) {
        if (status === 'uploading') {
            file.progress = param;
            file.error = null;
            this.props.setState('uploading');
            this.forceUpdate();
        } else if (status === 'error') {
            const xhr = param;
            file.error = 'Error: ' + xhr.statusError;
            try {
                const json = JSON.parse(xhr.responseText);
                if (json && json.message) {
                    file.error = 'Error: ' + json.message;
                }
            } catch (SyntaxError) {
            }
            this.props.setState('error', file.error);
            this.forceUpdate();
        } else if (status === 'done') {
            const files = this.state.files.filter(x => x !== file);
            this.setState({files:files});
            if (!files || !files.length ) {
                this.props.setState('done');
            }
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
            if (file.location === 'local') {
                file.xhr = serverCache.putFile(this.props.record, file,
                                               this.transferFileCallback.bind(this, file));
            } else if (file.location === 'b2drop') {
                file.xhr = serverCache.b2dropCopyFile(this.props.record, file.path, file.name,
                                                      this.transferFileCallback.bind(this, file));
            }
        }, 1);
    },

    renderUploadQueue() {
        if (!this.state.files.length) {
            return false;
        }
        return(
            <div className="well" style={{marginTop:'1em'}}>
                <div className="fileList">
                    <FileUploadHeader/>
                    { this.state.files.map(f =>
                        <FileUploadRow key={f.name} file={f} remove={() => this.removeUploadFile(f)} />) }
                </div>
            </div>
        );
    },


    renderRecordFiles() {
        if (!this.props.files.length) {
            return false;
        }
        return(
            <div className="well" style={{marginTop:'1em'}}>
                <div className="fileList">
                    <FileRecordHeader/>
                    { this.props.files.map(f =>
                        <FileRecordRow key={f.key} file={f} remove={()=>this.removeRecordFile(f)} />) }
                </div>
            </div>
        );
    },



    render: function() {
        this.updateNext();
        const b2dropZone = <B2DropZone close={e => this.props.setModal(false)}
                                       onFiles={fs => this.handleAdd(fs, 'b2drop')} />;
        return (
            <div>
                <div className="row" style={{borderBottom:'1px solid #ddd'}}>
                    <h3 className="col-md-3">
                        Add files
                    </h3>
                    <div className="col-md-9" style={{margin:'1em 0'}}>
                        <LocalDropZone onFiles={fs => this.handleAdd(fs, 'local')}/>
                    </div>
                    <div className="col-md-offset-3 col-md-9" style={{marginBottom:'1em'}}>
                        <button className='b2dropbutton' onClick={e => this.props.setModal(b2dropZone)}>
                            <img src="/img/b2drop.png"/>
                            <h3>Add B2DROP files</h3>
                        </button>
                    </div>

                    { !this.state.files.length ? false :
                        <div className="col-md-offset-3 col-md-9">
                            { this.renderUploadQueue() }
                        </div>
                    }
                </div>

                { !this.props.files.length ? false :
                    <div className="row" style={{borderBottom:'1px solid #ddd'}}>
                        <div className="col-md-3">
                            <h3> Uploaded files </h3>
                        </div>
                        <div className="col-md-9" style={{marginBottom:'1em'}}>
                            { this.renderRecordFiles() }
                        </div>
                    </div>
                }
            </div>
        );
    },
});


export const FileUploadHeader = React.createClass({
    mixins: [React.addons.PureRenderMixin],
    render() {
        return (
            <div className="row fileHeader" style={{marginTop:'0.5em', marginBottom:'0.5em'}}>
                <div className="col-sm-6">Name</div>
                <div className="col-sm-3">Size</div>
            </div>
        );
    }
});


const FileUploadRow = React.createClass({
    propTypes: {
        file: PT.object.isRequired,
        remove: PT.func.isRequired,
    },

    getInitialState() {
        return {
            remove: false,
        };
    },

    renderProgress: function(file) {
        const widthPercent = file.progress+'%';
        return (
            <div className="row" style={{margin:'5px 0px'}}>
                <div className="col-md-12">
                    <div className="progress" style={{margin:'10px 0', height: 4}}>
                        <div className="progress-bar" role="progressbar" aria-valuenow={file.progress}
                             aria-valuemin="0" aria-valuemax="100" style={{width:widthPercent, height:4}} />
                    </div>
                </div>
            </div>
        );
    },

    renderError: function(file) {
        return (
            <div className="row" style={{margin:'5px 0px'}}>
                <div className="col-md-12">
                    <div className="alert alert-danger" style={{width:'100%', marginBottom:0}}> {file.error} </div>
                </div>
            </div>
        );
    },

    render() {
        let file = this.props.file;
        file = file.toJS ? file.toJS() : file;
        return (
            <div className="file" onClick={e => this.setState({open:!this.state.open})}>
                <div className="row">
                    <div className="col-sm-6">
                        <a style={{marginLeft:'1em'}}>{file.name}</a>
                    </div>
                    <div className="col-sm-3">{humanSize(file.size)}</div>
                    { this.props.remove ?
                        <button type="button" className="btn btn-sm remove" style={{float:'right', marginRight:'1em'}}
                            onClick={()=>this.setState({remove:true})}> <i className="glyphicon glyphicon-remove"/>
                        </button> : false
                    }
                </div>
                { this.state.remove ?
                    <FileRemoveDialog file={file}
                                      remove={this.props.remove}
                                      cancel={()=>this.setState({remove:false})} />
                    : false }
                { file.progress ? this.renderProgress(file) : false }
                { file.error ? this.renderError(file) : false }
            </div>
        );
    },
});


export const FileRecordHeader = React.createClass({
    mixins: [React.addons.PureRenderMixin],
    render() {
        return (
            <div className="row fileHeader" style={{marginTop:'0.5em', marginBottom:'0.5em'}}>
                <div className="col-sm-6">Name</div>
                <div className="col-sm-3">Date</div>
                <div className="col-sm-3">Size</div>
            </div>
        );
    }
});


export const FileRecordRow = React.createClass({
    mixins: [React.addons.PureRenderMixin],

    propTypes: {
        file: PT.object.isRequired,
        remove: PT.func,
    },

    getInitialState() {
        return {
            open: false,
            remove: false,
        };
    },

    render() {
        let file = this.props.file;
        file = file.toJS ? file.toJS() : file;

        const allowDetails = file.checksum || file.epic_pid;
        const stateMark = allowDetails ? (this.state.open ? "down":"right") : "";

        return (
            <div className="file">
                <div className="row" onClick={e => this.setState({open:!this.state.open})}>
                    <div className="col-sm-6">
                        <span className={"glyphicon glyphicon-chevron-"+stateMark}
                            style={{marginLeft:'0.5em', fontSize:10}} aria-hidden="true"/>
                        <span className={"glyphicon glyphicon-file"}
                            style={{marginLeft:'0.5em', fontSize:10}} aria-hidden="true"/>
                        <a style={{display:'inline-block', marginLeft:'0.5em'}}
                            href={file.url}>{file.key || file.name}</a>
                    </div>
                    <div className="col-sm-3">{moment(file.updated).format('ll')}</div>
                    <div className={"col-sm-"+(this.props.remove? "2":"3")}>{humanSize(file.size)}</div>
                    { this.props.remove ?
                        <button type="button" className="btn btn-sm remove" style={{float:'right', marginRight:'1em'}}
                            onClick={()=>this.setState({remove:true})}> <i className="glyphicon glyphicon-remove"/>
                        </button> : false
                    }
                </div>
                { allowDetails && this.state.open ?
                    <div className="details">
                        { file.checksum ? <div className="row">
                            <div className="col-sm-12"><span style={{marginLeft:'2.5em'}}/>
                                Checksum:
                                <span className="checksum" style={{marginLeft:'0.5em'}}>{file.checksum}</span>
                            </div>
                        </div> : false }
                        { file.epic_pid ? <div className="row">
                            <div className="col-sm-12"><span style={{marginLeft:'2.5em'}}/>
                                PID: <EpicPid style={{marginLeft:'0.2em'}} pid={file.epic_pid} />
                            </div>
                        </div> : false }
                    </div> : false }
                { this.props.remove && this.state.remove ?
                    <FileRemoveDialog file={file}
                                      remove={this.props.remove}
                                      cancel={()=>this.setState({remove:false})} />
                    : false }
            </div>
        );
    },
});


const FileRemoveDialog = React.createClass({
    propTypes: {
        file: PT.object.isRequired,
        remove: PT.func.isRequired,
        cancel: PT.func.isRequired,
    },

    render: function() {
        const file = this.props.file;
        return (
            <div className="row">
                <div className="col-sm-10 col-sm-offset-1"> <p style={{textAlign:'center', padding:'1em 0'}}>
                    { file.progress ? 'Stop uploading and remove this file?' : 'Remove this file?'}
                    { file.key ? ' This operation will change the record.' : false }
                </p> </div>
                <div className="col-sm-4 col-sm-offset-2">
                    <button type="button" className="btn btn-default btn-block btn-sm"
                        onClick={this.props.remove}> Yes </button>
                </div>
                <div className="col-sm-4">
                    <button type="button" className="btn btn-default btn-block btn-sm"
                        onClick={this.props.cancel}> No </button>
                </div>
            </div>
        );
    },
});


export const EpicPid = React.createClass({
    propTypes: {
        pid: PT.string.isRequired,
        style: PT.object,
    },

    HDL_PREFIX: "http://hdl.handle.net/",

    getInitialState() {
        return {
            prefix: "",
            pid: "",
        }
    },

    componentWillMount() {
        this.componentWillReceiveProps(this.props);
    },

    componentWillReceiveProps(props) {
        let prefix = "";
        let pid = props.pid;
        if (pid.indexOf(this.HDL_PREFIX) === 0) {
            prefix = this.HDL_PREFIX;
            pid = pid.substring(this.HDL_PREFIX.length, pid.length);
        }
        this.setState({ prefix, pid });
    },

    copyToClipboard() {
        if (!this.pidref) {
            return;
        }
        this.pidref.value = this.state.prefix+this.state.pid;
        this.pidref.select();
        document.execCommand('copy');
        this.pidref.value = this.state.pid;
    },

    render: function() {
        const style = {
            whiteSpace:"nowrap",
            overflow: "auto",
            border: "none",
            padding:0,
            margin:0,
            width:"24em",
            backgroundColor:"transparent",
        };
        return (
            <span style={this.props.style}>
                <input className="epic_pid" style={style} ref={c => this.pidref = c} defaultValue={this.state.pid} />
                <span><a className="btn btn-xs btn-default" onClick={this.copyToClipboard}>Copy</a></span>
            </span>
        );
    },
});
