import React from 'react/lib/ReactWithAddons';

export const Add = React.createClass( {
    // constructor(props) {
    //   super(props);
      
      // handleAdd = this.handleAdd.bind(this);
      // this.setState({name:""});
    // }

    getInitialState() {
        return {
            name: '',
        }
    },

    handleAdd(e) {
        e.preventDefault();
        this.props.onAdd(this.state.name);
    },



    render() {
      return (
        <form>
          <input
            type="text"
            name="name"
            value={this.state.name}
            onChange={e => this.setState({ name: e.target.value })}
          >
          </input>
          <button onClick={this.handleAdd}>Add</button>
        </form>
      );
    }
});