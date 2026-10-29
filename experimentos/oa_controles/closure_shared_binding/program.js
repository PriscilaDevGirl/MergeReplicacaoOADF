function make() { var x = 0; return function () { x = 1; }; }
var f = make();
f();
f();
