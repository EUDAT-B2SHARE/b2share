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

export function countProps(o) {
    let n = 0;
    for (let p in o) {
        if (o.hasOwnProperty(p)) {
            n++;
        }
    }
    return n;
};


export function humanSize(sz) {
    let K = 1000, M = K*K, G = K*M, T = K*G;

    if (sz < K) {
        return [sz,'B '];
    } else if (sz < M) {
        return [(sz/K).toFixed(2), 'KB'];
    } else if (sz < G) {
        return [(sz/M).toFixed(2), 'MB'];
    } else if (sz < T) {
        return [(sz/G).toFixed(2), 'GB'];
    } else {
        return [(sz/T).toFixed(2), 'TB'];
    }
}

export function keys(o) {
    const a = [];
    for (const x in o) {
        if (o.hasOwnProperty(x)) {
            a.push(x);
        }
    }
    return a;
}

export function pairs(o) {
    var a = []
    for (var k in o) {
        if (o.hasOwnProperty(k)) {
            a.push([k, o[k]]);
        }
    }
    return a;
}

export function expect(condition) {
    if (console.assert) {
        console.assert(condition);
    } else if (!condition) {
        if (console.error) {
            console.error("Expectation failed: ", condition);
        } else {
            console.log("Expectation failed: ", condition);
        }
    }
}

// useful for react handlers
export function stateSetter(obj, state) {
    return function() {
        obj.setState(state);
    }
}
