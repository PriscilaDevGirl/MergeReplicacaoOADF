"""Conta commits de um clone completo em SHA congelado; nao seleciona projetos.

A janela opcional usa data UTC do committer, inclusiva, sem pruning temporal.
Nao faz rede, checkout, mineracao de arquivos ou classificacao de linguagem.
"""
import argparse
import json
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode('utf-8').strip()


def inventory(repo, revision='HEAD', since=None, until=None):
    repo = Path(repo).resolve()
    if git(repo, 'rev-parse', '--is-shallow-repository') != 'false':
        raise ValueError('Historico raso nao permite a contagem deste protocolo')
    start = date.fromisoformat(since) if since else None
    end = date.fromisoformat(until) if until else None
    if start and end and start > end:
        raise ValueError('Data inicial posterior a final')
    sha = git(repo, 'rev-parse', '--verify', revision + '^{commit}')
    all_count = int(git(repo, 'rev-list', '--count', sha))
    two_parent_count = int(git(repo, 'rev-list', '--count', '--min-parents=2', '--max-parents=2', sha))
    period_count = period_merges = 0
    lines = git(repo, 'log', sha, '--format=%H%x09%ct%x09%P').splitlines()
    for line in lines:
        fields = line.split('\t')
        committed = datetime.fromtimestamp(int(fields[1]), timezone.utc).date()
        parents = fields[2].split() if len(fields) > 2 else []
        if (not start or committed >= start) and (not end or committed <= end):
            period_count += 1
            period_merges += len(parents) == 2
    assert len(lines) == all_count
    return dict(frozen_sha=sha, supplied_revision=revision,
                history_scope='all ancestors reachable from the frozen SHA; not all server branches',
                shallow=False, git_version=git(repo, '--version'),
                collected_at_utc=datetime.now(timezone.utc).isoformat(),
                commits_all_history=all_count, two_parent_merges_all_history=two_parent_count,
                period_since_utc=since, period_until_utc=until,
                commits_in_period=period_count, two_parent_merges_in_period=period_merges,
                counts_include_merge_commits=True,
                note='Inventory only. No global ranking, candidate selection, or language eligibility claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--since')
    parser.add_argument('--until')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    if output.exists():
        raise ValueError('Escolha uma saida nova para preservar inventarios anteriores')
    result = inventory(args.repo, args.revision, args.since, args.until)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
