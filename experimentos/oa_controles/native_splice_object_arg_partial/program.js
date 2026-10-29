var a = [0];
a[0] = 1;
a.splice({valueOf: function () { return 0; }}, 0);
a[0] = 2;
