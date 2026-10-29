var o = {};
o.x = 1;
Object.defineProperty(o, "x", {value: 7, writable: true});
o.x = 2;
