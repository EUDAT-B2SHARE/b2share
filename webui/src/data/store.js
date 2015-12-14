import React from 'react';
import Immutable from 'immutable';

export class Store {
    constructor(initialState = {}, onChange = () => {}) {
        this.root = Immutable.fromJS(initialState);
        this.onChange = onChange;
        window.store = this;
    }

    // returns a new branch from the path
    branch(...path) {
        return new Branch(this, path);
    }

    ///////////////////////////////////////////////////////
    // methods that mutate store

    // sets data node at path
    setIn(path, data) {
        if (!path || !path.length) return ;
        this.root = this.root.setIn(path, data);
        this.onChange();
    }

    // updates data node at path via a provided function
    update(path, updateFn) {
        if (!path || !path.length) return ;
        this.root = this.root.updateIn(path, updateFn);
        this.onChange();
    }
};


class Branch {
    constructor(store, path) {
        this.store = store;
        this.path = path;
    }

    // returns a sub-branch of the current branch
    branch(...path) {
        if (!this.path) return new Branch(this.store, null);
        if (!path.length) return this;
        return new Branch(this.store, [...this.path, ...path]);
    }

    // returns a new branch based on the predicate
    find(predicate) {
        if (!this.path) return new Branch(this.store, null);
        const e = this.get().findEntry(predicate);
        return e ? this.branch(e[0]) : new Branch(this.store, null);
    }

    // return true if the branch path exists in the store tree
    valid() {
        return this.path && this.store.root.hasIn(this.path);
    }

    // returns immutable collection or value that the branch (and keys) points to
    get(...keys) {
        if (!this.path) return undefined;
        return this.store.root.getIn(keys ? [...this.path, ...keys] : this.path);
    }

    // how many elements has the data in this branch?
    count() { a
        if (!this.path) return 0;
        return this.get().count();
    }

    // the classical functional map
    map(fn) {
        if (!this.path) return null;
        return this.get().map(fn);
    }

    ///////////////////////////////////////////////////////
    // methods that mutate store

    // sets data at the node this branch points to
    set(data) {
        if (!this.path) return ;
        this.store.setIn(this.path, data);
    }

    // sets data at the node this branch points to and moving down tree
    // on the specified path
    setIn(path, data) {
        if (!this.path) return ;
        this.store.setIn([...this.path, ...path], data);
    }

    // updates data at the node this branch points to
    update(updateFn) {
        if (!this.path) return ;
        this.store.updateIn(this.path, updateFn);
    }
}
