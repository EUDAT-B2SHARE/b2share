import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'
import { fromJS, OrderedMap, Map } from 'immutable';
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
        const iconClass = !file.isdir ? "glyphicon-file" :
                            file.children == undefined ? "glyphicon-folder-close" : "glyphicon-folder-open";
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
                        Select Files
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

export const Files = React.createClass({
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
            serverCache.deleteFile(this.props.record, f.uuid);
        }
    },

    transferFileCallback(file, status, param) {
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

    renderB2DropButton: function() {
        const b2dropZone = <B2DropZone close={e => this.props.setModal(false)}
                                       onFiles={fs => this.handleAdd(fs, 'b2drop')} />;
        return (
            <button className='b2dropbutton' onClick={e => this.props.setModal(b2dropZone)}>
                <img src="/img/b2drop.png"/>
                <h3>Add B2DROP files</h3>
            </button>
        );
    },

    render: function() {
        this.updateNext();
        return (
            <div>
                { this.props.files.length ?
                    <div className="row" style={{marginBottom:'1em'}} >
                        <div className="col-md-12">
                            <h3> Record files </h3>
                        </div>
                    </div> : false }
                <div className="fileList">
                    { this.props.files.map(this.renderFile) }
                </div>
                <div className="row">
                    <h3 className="col-md-12" style={{marginBottom:'1em'}}>
                        { this.props.files.length ? 'Add more files' : 'Add files'}
                    </h3>
                </div>
                <DropZone onFiles={fs => this.handleAdd(fs, 'local')}/>
                <div style={{marginTop:'1em'}}/>
                { this.renderB2DropButton() }
                <div className="fileList">
                    { this.state.files.map(this.renderFile) }
                </div>
            </div>
        );
    },
});
