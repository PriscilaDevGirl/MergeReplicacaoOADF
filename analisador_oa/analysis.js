// JALANGI DO NOT INSTRUMENT
// Independent OA reimplementation, not Amanda Moraes's original implementation.
(function (sandbox) {
    'use strict';
    var fs = require('fs');
    var path = require('path');
    var crypto = require('crypto');
    var config = JSON.parse(fs.readFileSync(process.env.OA_CONFIG, 'utf8'));
    var maps = new Map();
    function canonical(p) {
        p = path.resolve(p);
        return process.platform === 'win32' ? p.toLowerCase() : p;
    }
    config.files.forEach(function (file) {
        var hash = crypto.createHash('sha256').update(fs.readFileSync(file.runtime_path)).digest('hex');
        if (hash !== file.source_sha256) throw new Error('OA source hash mismatch: ' + file.runtime_path);
        maps.set(canonical(file.runtime_path), file);
    });
    var nextId = 1;
    var globalEnv = {id: nextId++, parent: null, names: new Set(), writes: new Map()};
    var env = globalEnv;
    var environments = [];
    var scripts = new Map();
    var closures = new WeakMap();
    var objects = new WeakMap();
    var calls = [];
    var functions = [];
    var events = [];
    var eventCount = 0;
    var warningCounts = Object.create(null);
    var warningExamples = [];
    var counts = {writes: 0, L: 0, R: 0, BASE: 0, UNKNOWN: 0, base_resets: 0};
    var covered = {L: new Set(), R: new Set()};
    var scriptErrors = 0;
    var nativeArrays = {};
    ['push', 'pop', 'shift', 'unshift', 'splice', 'reverse', 'sort', 'fill', 'copyWithin'].forEach(function (name) {
        nativeArrays[name] = Array.prototype[name];
    });
    var nativeCallsModeled = 0;
    function warn(code, location) {
        warningCounts[code] = (warningCounts[code] || 0) + 1;
        if (warningExamples.length < 30) warningExamples.push({code: code, location: location});
    }
    function loc(iid) {
        var smap = sandbox.smap && sandbox.smap[sandbox.sid];
        var range = smap && smap[iid];
        return {file: smap ? smap.originalCodeFileName : '', line: range ? range[0] : null,
                column: range ? range[1] : null, endLine: range ? range[2] : null,
                iid: sandbox.sid + ':' + iid};
    }
    function direct(location) {
        var file = location.file && maps.get(canonical(location.file));
        if (!file) return 'UNMAPPED';
        var line = file.lines[String(location.line)];
        if (!line) { warn('unmapped_line', location); return 'UNKNOWN'; }
        var origin = line.origin;
        if (origin === 'L' || origin === 'R') covered[origin].add(canonical(location.file) + ':' + location.line);
        return origin;
    }
    function currentBranch() {
        if (calls.length) return calls[calls.length - 1].branch;
        if (functions.length) return functions[functions.length - 1].branch;
        return 'BASE';
    }
    function origin(location) {
        var own = direct(location);
        if (own === 'L' || own === 'R') return own;
        if (own === 'SHARED' || own === 'MERGE_ONLY' || own === 'UNKNOWN') return 'UNKNOWN';
        return currentBranch();
    }
    function snapshotStack() {
        return functions.map(function (f) { return {branch: f.branch, invocation: f.invocation}; });
    }
    function write(target, storage, key, location) {
        var branch = origin(location);
        counts.writes++;
        counts[branch]++;
        var previous = storage.get(key);
        if (branch !== 'L' && branch !== 'R') {
            if (previous && branch === 'BASE') counts.base_resets++;
            storage.delete(key);
            if (branch === 'UNKNOWN') warn('ambiguous_write_origin', location);
            return;
        }
        var event = {branch: branch, location: location, functionCallStack: snapshotStack()};
        if (previous && previous.branch !== branch) {
            eventCount++;
            if (events.length < (config.max_events || 1000)) {
                events.push({type: 'OVERRIDING_ASSIGNMENT', targetIdentifier: target,
                             previousAssignment: previous, currentAssignment: event,
                             interpretation: 'runtime OA candidate; semantic conflict requires review'});
            }
        }
        storage.set(key, event);
    }
    function objectState(obj) {
        if (!obj || (typeof obj !== 'object' && typeof obj !== 'function')) return null;
        var state = objects.get(obj);
        if (!state) { state = {id: nextId++, writes: new Map()}; objects.set(obj, state); }
        return state;
    }
    function propertyKey(key) {
        if (typeof key === 'object' && key !== null || typeof key === 'function' || typeof key === 'symbol') return null;
        return String(key);
    }
    function isIndex(key) {
        var n = Number(key);
        return String(n) === key && n >= 0 && n < 4294967295 && Math.floor(n) === n;
    }
    function arrayModel(name, array, args, location) {
        if (['push', 'pop', 'shift', 'unshift', 'splice', 'reverse', 'sort'].indexOf(name) < 0 || array.length > 100000) return null;
        if (name === 'sort' && args.length && args[0] !== undefined) return null;
        var names = Object.getOwnPropertyNames(array);
        for (var i = 0; i < names.length; i++) {
            var descriptor = Object.getOwnPropertyDescriptor(array, names[i]);
            if ((isIndex(names[i]) || names[i] === 'length') &&
                (!Object.prototype.hasOwnProperty.call(descriptor, 'value') || !descriptor.writable)) return null;
            if (name === 'sort' && isIndex(names[i]) && descriptor.value !== null &&
                ['object', 'function', 'symbol'].indexOf(typeof descriptor.value) >= 0) return null;
        }
        var proto = Object.getPrototypeOf(array);
        while (proto) {
            if (Object.getOwnPropertyNames(proto).some(isIndex)) return null;
            proto = Object.getPrototypeOf(proto);
        }
        var start = 0, removed = 0;
        if (name === 'splice') {
            if (args.length && (typeof args[0] === 'object' && args[0] !== null || typeof args[0] === 'function')) return null;
            if (args.length > 1 && (typeof args[1] === 'object' && args[1] !== null || typeof args[1] === 'function')) return null;
            function integer(value) {
                var n = Number(value);
                return isNaN(n) || n === 0 ? 0 : (n < 0 ? -1 : 1) * Math.floor(Math.abs(n));
            }
            start = args.length ? integer(args[0]) : 0;
            start = start < 0 ? Math.max(array.length + start, 0) : Math.min(start, array.length);
            removed = args.length === 0 ? 0 : args.length === 1 ? array.length - start : Math.min(Math.max(integer(args[1]), 0), array.length - start);
        }
        return {name: name, array: array, oldLength: array.length, count: args.length,
                start: start, removed: removed, location: location};
    }
    function finishArray(model) {
        var array = model.array, length = array.length, old = model.oldLength;
        var state = objectState(array);
        if (['push', 'pop', 'shift', 'unshift', 'splice'].indexOf(model.name) >= 0 && state.writes.has('length')) {
            state.writes.delete('length');
            warn('implicit_native_array_length_not_modeled', model.location);
        }
        state.writes.forEach(function (value, key) {
            if (isIndex(key) && !Object.prototype.hasOwnProperty.call(array, key)) state.writes.delete(key);
        });
        var indices = [];
        var begin = 0, end = 0;
        if (model.name === 'push') { begin = old; end = length; }
        if (model.name === 'shift') { begin = 0; end = Math.max(old - 1, 0); }
        if (model.name === 'unshift' && model.count > 0) { begin = 0; end = length; }
        if (model.name === 'sort') { begin = 0; end = length; }
        if (model.name === 'splice') {
            begin = model.start;
            var inserted = Math.max(model.count - 2, 0);
            end = inserted === model.removed ? begin + inserted : length;
        }
        if (model.name === 'reverse') {
            for (var pair = 0; pair < Math.floor(old / 2); pair++) {
                indices.push(pair, old - pair - 1);
            }
        } else {
            for (var index = begin; index < end; index++) indices.push(index);
        }
        indices.forEach(function (index) {
            var key = String(index);
            if (Object.prototype.hasOwnProperty.call(array, key)) {
                write('object:' + state.id + ':' + key, state.writes, key, model.location);
            }
        });
        nativeCallsModeled++;
    }
    function binding(name, isGlobal, isScriptLocal) {
        if (isGlobal) return globalEnv;
        if (isScriptLocal && scripts.has(sandbox.sid)) return scripts.get(sandbox.sid);
        var cursor = env;
        while (cursor) {
            if (cursor.names.has(name)) return cursor;
            cursor = cursor.parent;
        }
        warn('unresolved_variable_binding', null);
        return globalEnv;
    }
    sandbox.analysis = {
        scriptEnter: function () {
            environments.push(env);
            env = {id: nextId++, parent: globalEnv, names: new Set(), writes: new Map()};
            scripts.set(sandbox.sid, env);
        },
        scriptExit: function (iid, error) {
            if (error) scriptErrors++;
            env = environments.pop() || globalEnv;
        },
        literal: function (iid, val) {
            if (typeof val === 'function' && !closures.has(val)) closures.set(val, env);
        },
        declare: function (iid, name, val, isArgument, argumentIndex, isCatchParam) {
            env.names.add(name);
            if (isCatchParam) {
                while (calls.length && calls[calls.length - 1].depth >= functions.length) calls.pop();
            }
        },
        functionEnter: function (iid, f) {
            var invocation = calls.length ? calls[calls.length - 1] : null;
            var ownCall = invocation && invocation.f === f ? invocation : null;
            functions.push({branch: currentBranch(), invocation: invocation ? invocation.location : null,
                            ownCall: ownCall, previousEnv: env});
            env = {id: nextId++, parent: closures.get(f) || scripts.get(sandbox.sid) || globalEnv,
                   names: new Set(), writes: new Map()};
        },
        functionExit: function () {
            var frame = functions.pop();
            if (!frame) { warn('unbalanced_function_exit', null); return; }
            env = frame.previousEnv;
            if (frame.ownCall) {
                var index = calls.indexOf(frame.ownCall);
                if (index >= 0) calls.splice(index);
            }
            while (calls.length && calls[calls.length - 1].depth > functions.length) calls.pop();
        },
        invokeFunPre: function (iid, f, receiver, args) {
            var location = loc(iid);
            var call = {f: f, iid: location.iid, location: location, branch: origin(location), depth: functions.length};
            calls.push(call);
            // Native mutators need explicit index models; unmodeled operations
            // invalidate tracking and mark the execution partial.
            var nativeFunction = f;
            var nativeReceiver = receiver;
            var nativeArgs = args;
            if (f === Function.prototype.call || f === Function.prototype.apply) {
                nativeFunction = receiver;
                nativeReceiver = args[0];
                nativeArgs = f === Function.prototype.call ? Array.prototype.slice.call(args, 1) : (args[1] || []);
            }
            if (Array.isArray(nativeReceiver)) {
                Object.keys(nativeArrays).some(function (name) {
                    if (nativeFunction !== nativeArrays[name]) return false;
                    call.arrayModel = arrayModel(name, nativeReceiver, nativeArgs, location);
                    if (!call.arrayModel) {
                        objectState(nativeReceiver).writes.clear();
                        warn('native_array_mutator_not_modeled', location);
                    }
                    return true;
                });
            }
            if (nativeFunction === Object.defineProperty || nativeFunction === Object.defineProperties || nativeFunction === Object.assign) {
                var target = objectState(nativeArgs[0]);
                if (target) target.writes.clear();
                warn('native_property_writer_not_modeled', location);
            }
            if (f === Function || f === eval ||
                ['setTimeout', 'setInterval', 'setImmediate', 'queueMicrotask'].some(function (name) {
                    return typeof global[name] === 'function' && f === global[name];
                })) warn('dynamic_code_or_async_not_modeled', location);
        },
        invokeFun: function (iid, f) {
            var location = loc(iid);
            for (var i = calls.length - 1; i >= 0; i--) {
                if (calls[i].f === f && calls[i].iid === location.iid) {
                    if (calls[i].arrayModel) finishArray(calls[i].arrayModel);
                    calls.splice(i);
                    break;
                }
            }
        },
        write: function (iid, name, val, lhs, isGlobal, isScriptLocal) {
            var frame = binding(name, isGlobal, isScriptLocal);
            write('var:' + frame.id + ':' + name, frame.writes, name, loc(iid));
        },
        putField: function (iid, obj, offset) {
            var state = objectState(obj);
            if (!state) return;
            var location = loc(iid);
            var key = propertyKey(offset);
            if (key === null) { state.writes.clear(); warn('dynamic_property_key_not_modeled', location); return; }
            var descriptor = Object.getOwnPropertyDescriptor(obj, key);
            if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, 'value')) {
                state.writes.delete(key); warn('accessor_or_inherited_write_not_modeled', location); return;
            }
            if (!descriptor.writable) {
                state.writes.delete(key); warn('nonwritable_property', location); return;
            }
            if (Array.isArray(obj) && key === 'length') {
                state.writes.forEach(function (value, oldKey) {
                    var index = Number(oldKey);
                    if (String(index) === oldKey && index >= obj.length && index >= 0 && index < 4294967295) {
                        state.writes.delete(oldKey);
                    }
                });
            }
            write('object:' + state.id + ':' + key, state.writes, key, location);
        },
        binary: function (iid, op, obj, offset, result) {
            if (op === 'delete' && result) {
                var state = objectState(obj);
                var key = propertyKey(offset);
                if (state && key !== null) state.writes.delete(key);
                else if (state) { state.writes.clear(); warn('dynamic_delete_key_not_modeled', loc(iid)); }
            }
        },
        endExecution: function () {
            var report = {implementation: 'independent-oa-v0.2', original_author_tool: false,
                scope: 'ES5 synchronous explicit writes and seven restricted plain-array native index models',
                native_array_models: ['push', 'pop', 'shift', 'unshift', 'splice', 'reverse', 'sort_without_comparator_primitive_values'],
                native_array_calls_modeled: nativeCallsModeled,
                analysis_finished: true, script_errors: scriptErrors,
                completeness: Object.keys(warningCounts).length ? 'partial' : 'within_declared_subset',
                assignments: counts, executed_branch_lines: {L: Array.from(covered.L), R: Array.from(covered.R)},
                event_count: eventCount, reported_event_count: events.length, events: events,
                warnings: warningCounts, warning_examples: warningExamples};
            fs.writeFileSync(config.output_path, JSON.stringify(report, null, 2));
            console.log('OA_REPORT ' + config.output_path);
        }
    };
}(J$));
