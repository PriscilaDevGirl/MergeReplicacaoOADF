"""Aplica o mapeador e o analisador OA independente aos registros oficiais."""
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from executar_oa import ROOT, run_oa
from mapear_origens_oa import build_map

REPO = ROOT / 'repositorios/underscore'
INPUT = ROOT / 'resultados/miningframework/saida_oficial/data/results.csv'
OUT = ROOT / 'resultados/oa_coleta'
STAGING = ROOT / 'experimentos/oa_coleta'
OUT.mkdir(parents=True, exist_ok=True)
STAGING.mkdir(parents=True, exist_ok=True)
results = []
for row in csv.DictReader(INPUT.open(encoding='utf-8-sig'), delimiter=';'):
    sha, path = row['merge commit'], row['file path']
    sid = sha[:12] + '_' + hashlib.sha256(path.encode()).hexdigest()[:10]
    folder, output = STAGING / sid, OUT / sid
    folder.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    source = folder / 'merge.js'
    source.write_bytes(subprocess.check_output(['git', '-C', str(REPO), 'show', sha + ':' + path]))
    mapping = build_map(REPO, sha, path, source)
    (output / 'line_to_branch_map.json').write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding='utf-8')
    annotated = '\n'.join(f'{i:5} {mapping["lines"][str(i)]["origin"]:10} {line}'
                          for i, line in enumerate(source.read_text(encoding='utf-8').splitlines(), 1))
    (output / 'merge_annotated.txt').write_text(annotated + '\n', encoding='utf-8')
    execution = run_oa([mapping], source, output)
    report = execution['report']
    result = dict(sample_id=sid, merge_sha=sha, file_path=path,
                  map_origin_counts=dict(Counter(v['origin'] for v in mapping['lines'].values())),
                  status=execution['status'], exit_code=execution['exit_code'],
                  event_count=report['event_count'] if report and execution['status'] == 'success' else None,
                  completeness=report['completeness'] if report else None,
                  executed_branch_lines={k:len(v) for k,v in report['executed_branch_lines'].items()} if report else None,
                  warnings=report['warnings'] if report else {}, semantic_label='unverified')
    results.append(result)
    print(sid, execution['status'], 'OA', result['event_count'], result['completeness'])
summary = dict(implementation='independent-oa-v0.2', original_amanda_analyzer=False,
               file_merge_pairs=len(results), status_counts=dict(Counter(r['status'] for r in results)),
               total_events_successful=sum(r['event_count'] or 0 for r in results),
               complete_within_declared_subset=sum(r['status']=='success' and r['completeness']=='within_declared_subset' for r in results),
               confirmed_semantic_conflicts=None, results=results,
               cautions=['Not the original 69-case validation suite', 'No recall or accuracy estimate',
                         'Native mutators/accessors/async outside declared subset',
                         'Line map is conservative and requires review', 'Zero events is not proof of no semantic conflict'])
(OUT / 'resumo.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
with (OUT / 'resultados.csv').open('w', encoding='utf-8-sig', newline='') as stream:
    columns = ['sample_id', 'merge_sha', 'file_path', 'status', 'exit_code', 'event_count', 'completeness', 'semantic_label']
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(results)
print(json.dumps({k:v for k,v in summary.items() if k != 'results'}, indent=2, ensure_ascii=False))
