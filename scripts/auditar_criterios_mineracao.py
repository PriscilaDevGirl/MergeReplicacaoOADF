"""Audita no Git os criterios verificaveis do lote oficial preservado."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / 'repositorios/underscore'
OUT = ROOT / 'resultados/miningframework'
INPUT = ROOT / 'experimentos/miningframework/commits_piloto.csv'
RESULTS = OUT / 'saida_oficial/data/results.csv'


def git(*args, check=True):
    result = subprocess.run(['git', '-C', str(REPO), *args], capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', 'replace'))
    return result


def main():
    selected = list(csv.DictReader(INPUT.open(encoding='utf-8-sig')))
    records = list(csv.DictReader(RESULTS.open(encoding='utf-8-sig'), delimiter=';'))
    assert len(selected) == 5 and len(records) == 6
    assert {r['merge'] for r in selected} == {r['merge commit'] for r in records}
    exported = {json.loads(p.read_text(encoding='utf-8'))['merge_sha'] for p in
                (ROOT / 'resultados/underscore_pre2015/amostras').glob('*/metadata.json')}
    assert exported == {r['merge'] for r in selected}
    refs = {}
    for record in selected:
        sha = record['merge']
        parents = git('rev-list', '--parents', '-n', '1', sha).stdout.decode().split()[1:]
        assert parents == [record['left'], record['right']]
        bases = git('merge-base', '--all', *parents).stdout.decode().split()
        assert len(bases) == 1 and bases[0] not in parents
        date = git('show', '-s', '--format=%cI', sha).stdout.decode().strip()
        assert date[:10] <= '2014-12-31'
        refs[sha] = (parents, bases[0], date)
    audited = []
    for record in records:
        sha, path = record['merge commit'], record['file path']
        parents, base, date = refs[sha]
        statuses = []
        for parent in parents:
            lines = git('diff-tree', '--no-commit-id', '--name-status', '-r', base, parent, '--', path).stdout.decode().splitlines()
            assert len(lines) == 1 and lines[0].split('\t', 1)[0] == 'M', (sha, path, lines)
            statuses.append('M')
        assert path.endswith('.js')
        present = all(git('cat-file', '-e', f'{ref}:{path}', check=False).returncode == 0
                      for ref in [base, *parents, sha])
        assert present
        audited.append(dict(merge_sha=sha, file_path=path, committer_date=date,
                            left_sha=parents[0], right_sha=parents[1], base_sha=base,
                            left_status=statuses[0], right_status=statuses[1],
                            two_parents=True, unique_base=True, ancestor_not_parent=True,
                            before_2015=True, javascript=True, four_versions_present=present))
    with (OUT / 'criterios_verificados.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(audited[0]))
        writer.writeheader()
        writer.writerows(audited)
    summary = dict(scope='mining_only', project='https://github.com/jashkenas/underscore',
                   official_selected_merges=len(selected), official_file_merge_pairs=len(audited),
                   unique_file_paths=sorted({r['file_path'] for r in audited}),
                   all_six_records_meet_checked_criteria=True,
                   selection='convenience: merges from first five complete exported exploratory pairs',
                   random_seed_role='processing order, not random selection of the pilot',
                   original_output_sha256=hashlib.sha256(RESULTS.read_bytes()).hexdigest(),
                   source_input='experimentos/miningframework/commits_piloto.csv',
                   source_output='resultados/miningframework/saida_oficial/data/results.csv')
    (OUT / 'resumo_mineracao.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
