import Immutable from 'immutable';

export class Store {
    constructor(initialState = {}, onChange = () => {}) {
        this.root = Immutable.fromJS(initialState);
        this.onChange = onChange;
        window.store = this;
    }

    // returns a new branch from the path
    branch(path) {
        if (!Array.isArray(path)) {
            console.error("Store.branch: array expected, instead got: ", typeof path, path);
        }
        return new Branch(this, path);
    }

    getIn(keys) {
        if (!Array.isArray(keys)) {
            console.error("Store.getIn: array expected, instead got: ", typeof keys, keys);
        }
        return this.root.getIn(keys);
    }

    findIn(keys, findFn) {
        const coll = this.getIn(keys);
        if (!coll) {
            return null;
        }
        return coll.find(findFn);
    }


    ///////////////////////////////////////////////////////
    // methods that mutate store

    // sets data node at path
    setIn(path, data) {
        if (!path || !path.length) return ;
        const obj = this.root.getIn(path);
        if (obj && obj.equals && obj.equals(data) || (obj === data)) return;
        this.root = this.root.setIn(path, data);
        this.onChange();
    }

    // updates data node at path via a provided function
    updateIn(path, updateFn) {
        if (!path || !path.length) return ;
        const x = this.root.getIn(path);
        const y = updateFn(x);
        if (x && x.equals && x.equals(y) || (x === y)) return;
        this.root = this.root.setIn(path, y);
        this.onChange();
    }

    // deletes data node at path
    deleteIn(path) {
        if (!path || !path.length) return ;
        if (this.root.hasIn(path)) {
            this.root = this.root.deleteIn(path);
            this.onChange();
        }
    }
};


class Branch {
    constructor(store, path) {
        this.store = store;
        this.path = path;
    }

    // returns a sub-branch of the current branch
    branch([path]) {
        if (!Array.isArray(path)) {
            console.error("Branch.branch: array expected, instead got: ", typeof path, path);
        }
        return new Branch(this.store, [...this.path, ...path]);
    }

    // return true if the branch path exists in the store tree
    exists() {
        return this.store.root.hasIn(this.path);
    }

    // returns a new branch based on the predicate
    find(predicate) {
        return this.store.findIn(this.path, predicate);
    }

    // returns immutable collection or value that the branch (and keys) points to
    get() {
        return this.store.getIn(this.path);
    }

    ///////////////////////////////////////////////////////
    // methods that mutate store

    // sets data at the node this branch points to
    set(data) {
        return this.store.setIn(this.path, data);
    }

    // updates data at the node this branch points to
    update(updateFn) {
        return this.store.updateIn(this.path, updateFn);
    }
}
