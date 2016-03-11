import {fromJS} from 'immutable';
import {ajax} from './ajax'

function countProps(o) {
    let n = 0;
    for (let p in o) {
        if (o.hasOwnProperty(p)) {
            n++;
        }
    }
    return n;
};

export function objEquals(o1, o2) {
    if (typeof(o1) !== typeof(o2)) {
        return false;
    } else if (typeof(o1) === "function") {
        return o1.toString() === o2.toString();
    } else if (o1 instanceof Object && o2 instanceof Object) {
        if (countProps(o1) !== countProps(o2)) {
            return false;
        }
        for (let p in o1) {
            if (!objEquals(o1[p], o2[p])) {
                return false;
            }
        }
        return true;
    } else {
        return o1 === o2;
    }
}

export function timestamp2str(ts) {
    const date = new Date(ts);
    const y = date.getFullYear().toString();
    const month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const m = month[date.getMonth()]
    const d = date.getDate().toString();
    return d + " " + m + " " + y;
}

export function objToArray(o) {
    const a = [];
    for (const x in o) {
        if (o.hasOwnProperty(x)) {
            a.push(x);
        }
    }
    return a;
}
