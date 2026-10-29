var assert = require("assert");
var underscore = require("./merge.js")._;
assert.ok(underscore, "Objeto Underscore exportado");
var resultado = underscore.map([1, 2, 3], function (valor) { return valor * 2; });
assert.deepStrictEqual(resultado, [2, 4, 6]);
var pares = [];
underscore.each({a: 1, b: 2}, function (par) { pares.push(par.key); });
assert.deepStrictEqual(pares.sort(), ["a", "b"]);
console.log("UNDERSCORE_DRIVER_OK " + JSON.stringify(resultado));
