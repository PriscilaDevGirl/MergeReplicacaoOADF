var o = {};
function f() { o.x = 1; throw new Error("expected"); }
try { f(); } catch (e) {}
o.x = 7;
o.x = 2;
