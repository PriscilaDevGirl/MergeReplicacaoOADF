// Validation of the explicitly supported ES5 synchronous subset.
var acorn = require('../ferramentas/jalangi2/node_modules/acorn');
var fs = require('fs');
var path = require('path');
var config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
var warnings = [];
config.files.forEach(function (file) {
    var ast = acorn.parse(fs.readFileSync(file.runtime_path, 'utf8'), {ecmaVersion: 5, locations: true});
    function visit(node) {
        if (!node || typeof node !== 'object') return;
        if (node.type === 'WithStatement' || (node.type === 'Property' && node.kind !== 'init')) {
            throw new Error('Unsupported dynamic scope/accessor at ' + file.runtime_path + ':' + node.loc.start.line);
        }
        if (node.type === 'Identifier' && ['eval', 'Proxy', 'Promise', 'setTimeout', 'setInterval', 'setImmediate'].indexOf(node.name) >= 0) {
            warnings.push({file: file.runtime_path, line: node.loc.start.line, feature: node.name});
        }
        Object.keys(node).forEach(function (key) {
            if (key === 'loc') return;
            if (Array.isArray(node[key])) node[key].forEach(visit);
            else if (node[key] && typeof node[key] === 'object') visit(node[key]);
        });
    }
    visit(ast);
});
if (warnings.length) {
    console.log(JSON.stringify({static_feature_warnings: warnings}, null, 2));
}
console.log('PREFLIGHT_OK');
