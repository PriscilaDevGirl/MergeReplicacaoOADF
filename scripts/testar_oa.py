"""Casos sinteticos independentes de dados empiricos: regressao do nucleo OA."""
import hashlib
import itertools
import json
import os
import subprocess
from pathlib import Path
from executar_oa import ROOT, run_oa
from mapear_origens_oa import build_map

OUT = ROOT / 'resultados/oa_validacao'
FIXTURES = ROOT / 'experimentos/oa_controles'
OUT.mkdir(parents=True, exist_ok=True)
FIXTURES.mkdir(parents=True, exist_ok=True)


def fixture(name, lines, expected, warning=None, rejected=False):
    folder = FIXTURES / name
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / 'program.js'
    raw = ('\n'.join(line[0] for line in lines) + '\n').encode()
    source.write_bytes(raw)
    mapping = dict(runtime_path=str(source), source_sha256=hashlib.sha256(raw).hexdigest(),
                   lines={str(i):dict(origin=branch) for i, (_, branch) in enumerate(lines, 1)})
    result = run_oa([mapping], source, OUT / name)
    if rejected:
        assert result['status'] == 'unsupported_source', (name, result)
        actual = None
    else:
        assert result['status'] == 'success', (name, result, (OUT / name / 'stderr.txt').read_text())
        report = result['report']
        actual = report['event_count']
        assert actual == expected, (name, expected, actual, report)
        if warning:
            assert warning in report['warnings'], (name, report)
            assert report['completeness'] == 'partial'
        else:
            assert not report['warnings'], (name, report['warnings'])
    return dict(name=name, expected_events=expected, actual_events=actual,
                expected_rejection=rejected, expected_warning=warning, passed=True)


CASES = [
 ('variable_overwrite', [('var x = 0;', 'BASE'), ('x = 1;', 'L'), ('x = 2;', 'R')], 1),
 ('same_value_is_write', [('var x = 0;', 'BASE'), ('x = 1;', 'L'), ('x = 1;', 'R')], 1),
 ('same_branch', [('var x = 0;', 'BASE'), ('x = 1;', 'L'), ('x = 2;', 'L')], 0),
 ('base_reset', [('var x = 0;', 'BASE'), ('x = 1;', 'L'), ('x = 7;', 'BASE'), ('x = 2;', 'R')], 0),
 ('different_variables', [('var x = 0, y = 0;', 'BASE'), ('x = 1;', 'L'), ('y = 2;', 'R')], 0),
 ('alias_object', [('var o = {}, alias = o;', 'BASE'), ('o.x = 1;', 'L'), ('alias.x = 2;', 'R')], 1),
 ('different_objects', [('var a = {}, b = {};', 'BASE'), ('a.x = 1;', 'L'), ('b.x = 2;', 'R')], 0),
 ('different_fields', [('var o = {};', 'BASE'), ('o.x = 1;', 'L'), ('o.y = 2;', 'R')], 0),
 ('same_index_coercion', [('var a = [];', 'BASE'), ('a[0] = 1;', 'L'), ('a["0"] = 2;', 'R')], 1),
 ('different_indices', [('var a = [];', 'BASE'), ('a[0] = 1;', 'L'), ('a[1] = 2;', 'R')], 0),
 ('reference_not_field', [('var o = {}, a;', 'BASE'), ('a = o;', 'L'), ('o.x = 2;', 'R')], 0),
 ('indirect_call', [('var o = {};', 'BASE'), ('function f() { o.x = 1; }', 'BASE'), ('f();', 'L'), ('f();', 'R')], 1),
 ('nested_indirect_call', [('var o = {};', 'BASE'), ('function f() { o.x = 1; }', 'BASE'), ('function g() { f(); }', 'BASE'), ('g();', 'L'), ('g();', 'R')], 1),
 ('fresh_local_scopes', [('function f() { var x = 0; x = 1; }', 'BASE'), ('f();', 'L'), ('f();', 'R')], 0),
 ('same_name_different_scopes', [('function f() { var x = 0;', 'BASE'), ('x = 1; }', 'L'), ('function g() { var x = 0;', 'BASE'), ('x = 2; }', 'R'), ('f(); g();', 'BASE')], 0),
 ('closure_shared_binding', [('function make() { var x = 0; return function () { x = 1; }; }', 'BASE'), ('var f = make();', 'BASE'), ('f();', 'L'), ('f();', 'R')], 1),
 ('closures_different_instances', [('function make() { var x = 0; return function () { x = 1; }; }', 'BASE'), ('var f = make(), g = make();', 'BASE'), ('f();', 'L'), ('g();', 'R')], 0),
 ('exception_context_cleanup', [('var o = {};', 'BASE'), ('function f() { o.x = 1; throw new Error("expected"); }', 'BASE'), ('try { f(); } catch (e) {}', 'L'), ('o.x = 7;', 'BASE'), ('o.x = 2;', 'R')], 0),
 ('alternating_writes', [('var x = 0;', 'BASE'), ('x = 1;', 'L'), ('x = 2;', 'R'), ('x = 3;', 'L')], 2),
 ('unexecuted_branch', [('var x = 0;', 'BASE'), ('if (false) {', 'BASE'), ('x = 1;', 'L'), ('}', 'BASE'), ('x = 2;', 'R')], 0),
 ('ambiguous_resets', [('var x = 0;', 'BASE'), ('x = 1;', 'L'), ('x = 7;', 'SHARED'), ('x = 2;', 'R')], 0, 'ambiguous_write_origin'),
 ('native_sort_comparator_partial', [('var a = [0];', 'BASE'), ('a[0] = 1;', 'L'), ('a.sort(function (a, b) { return a - b; });', 'BASE'), ('a[0] = 2;', 'R')], 0, 'native_array_mutator_not_modeled'),
 ('native_property_partial', [('var o = {};', 'BASE'), ('o.x = 1;', 'L'), ('Object.defineProperty(o, "x", {value: 7, writable: true});', 'BASE'), ('o.x = 2;', 'R')], 0, 'native_property_writer_not_modeled'),
 ('array_truncation_deletes_state', [('var a = [];', 'BASE'), ('a[0] = 1;', 'L'), ('a.length = 0;', 'BASE'), ('a[0] = 2;', 'R')], 0),
 ('delete_removes_state', [('var o = {};', 'BASE'), ('o.x = 1;', 'L'), ('delete o.x;', 'BASE'), ('o.x = 2;', 'R')], 0),
 ('native_mutator_via_call', [('var a = [0, 0];', 'BASE'), ('a[0] = 1;', 'L'), ('Array.prototype.reverse.call(a);', 'BASE'), ('a[0] = 2;', 'R')], 0),
 ('native_push_disjoint_indices', [('var a = [];', 'BASE'), ('a.push(1);', 'L'), ('a.push(2);', 'R')], 0),
 ('native_push_then_explicit', [('var a = [];', 'BASE'), ('a.push(1);', 'L'), ('a[0] = 2;', 'R')], 1),
 ('native_unshift_overwrites_index', [('var a = [0];', 'BASE'), ('a[0] = 1;', 'L'), ('a.unshift(2);', 'R')], 1),
 ('native_pop_deletes_state', [('var a = [];', 'BASE'), ('a[0] = 1;', 'L'), ('a.pop();', 'BASE'), ('a[0] = 2;', 'R')], 0),
 ('native_reverse_singleton_no_write', [('var a = [0];', 'BASE'), ('a[0] = 1;', 'L'), ('a.reverse();', 'BASE'), ('a[0] = 2;', 'R')], 1),
 ('native_shift_writes_index', [('var a = [0, 2];', 'BASE'), ('a[0] = 1;', 'L'), ('a.shift();', 'R')], 1),
 ('native_splice_replaces_index', [('var a = [0];', 'BASE'), ('a[0] = 1;', 'L'), ('a.splice(0, 1, 2);', 'R')], 1),
 ('native_splice_noop', [('var a = [0];', 'BASE'), ('a[0] = 1;', 'L'), ('a.splice(0, 0);', 'BASE'), ('a[0] = 2;', 'R')], 1),
 ('native_splice_object_arg_partial', [('var a = [0];', 'BASE'), ('a[0] = 1;', 'L'), ('a.splice({valueOf: function () { return 0; }}, 0);', 'BASE'), ('a[0] = 2;', 'R')], 0, 'native_array_mutator_not_modeled'),
 ('native_sort_default', [('var a = [0, 2];', 'BASE'), ('a[0] = 1;', 'L'), ('a.sort();', 'R')], 1),
 ('native_length_tracking_partial', [('var a = [];', 'BASE'), ('a.length = 1;', 'L'), ('a.push(2);', 'BASE'), ('a.length = 3;', 'R')], 0, 'implicit_native_array_length_not_modeled'),
]
results = []
for case in CASES:
    result = fixture(*case)
    results.append(result)
    print('PASS', result['name'])
results.append(fixture('reject_with', [('var o = {}; with (o) {}', 'BASE')], None, rejected=True))
results.append(fixture('reject_es6_let', [('let x = 0;', 'BASE')], None, rejected=True))
results.append(fixture('reject_accessor', [('var o = {get x() { return 1; }};', 'BASE')], None, rejected=True))

# A real synthetic Git DAG verifies provenance mapping independently of manual maps.
repo = FIXTURES / 'mapping_git'
repo.mkdir(exist_ok=True)
subprocess.run(['git', 'init', str(repo)], capture_output=True, check=True)
env = os.environ.copy()
commit_sequence = itertools.count()
for key in ['GIT_AUTHOR_NAME', 'GIT_COMMITTER_NAME']:
    env[key] = 'Synthetic OA validation'
for key in ['GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_EMAIL']:
    env[key] = 'synthetic@example.invalid'
for key in ['GIT_AUTHOR_DATE', 'GIT_COMMITTER_DATE']:
    env[key] = '2020-01-01T00:00:00+00:00'


def commit(content, parents=()):
    blob = subprocess.check_output(['git', '-C', str(repo), 'hash-object', '-w', '--stdin'], input=content.encode()).decode().strip()
    tree = subprocess.check_output(['git', '-C', str(repo), 'mktree'], input=('100644 blob ' + blob + '\tcase.js\n').encode()).decode().strip()
    command = ['git', '-C', str(repo), 'commit-tree', tree]
    for p in parents:
        command += ['-p', p]
    message = ('SYNTHETIC control ' + str(next(commit_sequence)) + '\n').encode()
    return subprocess.check_output(command, input=message, env=env).decode().strip()


base_text = 'var x = 0;\nvar anchor = 1;\n'
left_text = 'var x = 0;\nx = 1;\nvar anchor = 1;\n'
right_text = 'var x = 0;\nvar anchor = 1;\nx = 2;\n'
merged_text = 'var x = 0;\nx = 1;\nvar anchor = 1;\nx = 2;\n'
b = commit(base_text)
l = commit(left_text, [b])
r = commit(right_text, [b])
m = commit(merged_text, [l, r])
source = repo / 'case.js'
source.write_bytes(merged_text.encode('utf-8'))
mapping = build_map(repo, m, 'case.js', source)
assert [v['origin'] for v in mapping['lines'].values()] == ['BASE', 'L', 'BASE', 'R'], mapping
execution = run_oa([mapping], source, OUT / 'git_map_to_detector')
assert execution['status'] == 'success' and execution['report']['event_count'] == 1
results.append(dict(name='git_map_to_detector', passed=True, expected_events=1, actual_events=1))

shared = 'var x = 0;\nx = 8;\nvar anchor = 1;\n'
sl, sr = commit(shared, [b]), commit(shared, [b])
sm = commit(shared + 'x = 9;\n', [sl, sr])
mapping2 = build_map(repo, sm, 'case.js', source)
assert mapping2['lines']['2']['origin'] == 'SHARED'
assert mapping2['lines']['4']['origin'] == 'MERGE_ONLY'
results.append(dict(name='git_shared_and_merge_only', passed=True))

# Reject a map if source bytes no longer match the frozen merge.
source.write_bytes(merged_text.encode('utf-8') + b'// modified after mapping\n')
tampered = run_oa([mapping], source, OUT / 'source_hash_mismatch')
assert tampered['status'] == 'execution_error'
assert 'source hash mismatch' in (OUT / 'source_hash_mismatch/stderr.txt').read_text(encoding='utf-8')
results.append(dict(name='source_hash_mismatch_rejected', passed=True))

# Insertion offsets are mapped using preserved ranges, not original line numbers.
offset_base = commit('var a = 0;\nvar b = 0;\nvar c = 0;\n')
offset_l = commit('var addedL = 1;\nvar a = 0;\nvar b = 0;\nvar c = 0;\n', [offset_base])
offset_r = commit('var a = 0;\nvar b = 0;\nvar c = 0;\nvar addedR = 2;\n', [offset_base])
offset_m = commit('var addedL = 1;\nvar a = 0;\nvar b = 0;\nvar c = 0;\nvar addedR = 2;\n', [offset_l, offset_r])
offset_map = build_map(repo, offset_m, 'case.js', source)
assert [r['origin'] for r in offset_map['lines'].values()] == ['L', 'BASE', 'BASE', 'BASE', 'R']
results.append(dict(name='git_insertions_change_line_offsets', passed=True))

summary = dict(synthetic_controls=True, not_original_69_case_suite=True,
               tests=len(results), passed=sum(r['passed'] for r in results), results=results)
(OUT / 'resumo.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
print('TOTAL', summary['passed'], '/', summary['tests'])
