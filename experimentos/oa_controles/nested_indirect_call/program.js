var o = {};
function f() { o.x = 1; }
function g() { f(); }
g();
g();
