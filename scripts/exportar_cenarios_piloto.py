"""Exporta o lote oficial como quatro versoes, patches e metadados portateis.

Le apenas o Git local. Nao executa os arquivos minerados nem repete a mineracao.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from verificar_pacote_mineracao import verify

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / 'resultados/miningframework/saida_oficial/data/results.csv'
REPO = ROOT / 'repositorios/underscore'
PROJECT = 'https://github.com/jashkenas/underscore'
COMPARISONS = [('base_left', 'base', 'left'), ('base_right', 'base', 'right'),
               ('base_merge', 'base', 'merge'), ('left_merge', 'left', 'merge'),
               ('right_merge', 'right', 'merge')]


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def safe_output(base, relative):
    posix = PurePosixPath(relative)
    if posix.is_absolute() or '..' in posix.parts:
        raise ValueError('Caminho de arquivo invalido')
    result = base.joinpath(*posix.parts)
    result.parent.mkdir(parents=True, exist_ok=True)
    return result


def main(out, archive):
    out, archive = Path(out).resolve(), Path(archive).resolve()
    if not out.is_relative_to(ROOT) or not archive.is_relative_to(ROOT):
        raise ValueError('Saidas devem ficar dentro deste projeto')
    if out.exists() or archive.exists():
        raise ValueError('Escolha nomes de saida novos para preservar entregas anteriores')
    rows = list(csv.DictReader(CSV.open(encoding='utf-8-sig'), delimiter=';'))
    assert len(rows) == 6
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['merge commit']].append(row)
    assert len(grouped) == 5
    tmp = ROOT / 'tmp'
    tmp.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='export-mineracao-', dir=tmp) as work:
        work = Path(work).resolve()
        assert work.is_relative_to(tmp.resolve())
        package = work / 'pacote'
        package.mkdir()
        index = []
        source_count = 0
        patch_count = 0
        for merge, candidates in sorted(grouped.items()):
            assert re.fullmatch('[0-9a-f]{40}', merge)
            parents = git('rev-list', '--parents', '-n', '1', merge).decode().split()[1:]
            assert len(parents) == 2
            bases = git('merge-base', '--all', *parents).decode().split()
            assert len(bases) == 1
            commits = dict(base=bases[0], left=parents[0], right=parents[1], merge=merge)
            detail = git('show', '-s', '--format=%cI%n%s', merge).decode('utf-8').splitlines()
            date, subject = detail[0], detail[1]
            folder = package / merge
            folder.mkdir()
            metadata = dict(project_url=PROJECT, commits=commits,
                            merge_committer_date=date, merge_subject=subject,
                            parent_convention='left=first parent; right=second parent',
                            snapshot_scope='only the six file-merge pairs from the official mining output',
                            selected_files=[])
            for row in sorted(candidates, key=lambda r:r['file path']):
                path = row['file path']
                versions = {}
                for role, sha in commits.items():
                    data = git('show', sha + ':' + path)
                    relative = f'{merge}/{role}/{path}'
                    safe_output(package, relative).write_bytes(data)
                    versions[role] = dict(file=relative, commit_sha=sha, sha256=digest(data),
                                          bytes=len(data), lines=len(data.splitlines()))
                    source_count += 1
                diffs = {}
                for label, before, after in COMPARISONS:
                    data = git('diff', '--no-ext-diff', '--no-textconv', '--no-renames',
                               '--unified=3', commits[before], commits[after], '--', path)
                    relative = f'{merge}/diffs/{label}/{path}.diff'
                    safe_output(package, relative).write_bytes(data)
                    diffs[label] = dict(file=relative, from_sha=commits[before], to_sha=commits[after])
                    patch_count += 1
                metadata['selected_files'].append(dict(path=path, versions=versions, diffs=diffs,
                                                       miningframework_row=row))
                index.append(dict(project='underscore', merge_sha=merge, base_sha=commits['base'],
                                  left_sha=commits['left'], right_sha=commits['right'],
                                  committer_date=date, file_path=path, case_folder=merge))
            # Project-wide patches provide context beyond the selected paths.
            for label, before, after in COMPARISONS[:3]:
                data = git('diff', '--no-ext-diff', '--no-textconv', '--no-renames', '--binary',
                           commits[before], commits[after])
                safe_output(folder, 'mudancas_projeto/' + label + '.patch').write_bytes(data)
                patch_count += 1
            save_json(folder / 'metadata.json', metadata)
            paths = ', '.join('`' + r['file path'] + '`' for r in candidates)
            readme = f'''# Cenário {merge[:12]}

Projeto: {PROJECT}

Data do committer: {date}

Mensagem original: {subject}

Arquivos selecionados: {paths}.

| Papel | SHA completo |
| --- | --- |
| Base comum | `{commits['base']}` |
| Left, primeiro pai | `{commits['left']}` |
| Right, segundo pai | `{commits['right']}` |
| Merge original | `{merge}` |

As pastas `base/`, `left/`, `right/` e `merge/` preservam os caminhos originais dos arquivos selecionados. `merge/` contém a versão gravada no histórico, sem simular uma nova junção.

Em `diffs/base_left/` estão as alterações da contribuição Left em relação à base. `diffs/base_right/` mostra Right em relação à base. As outras comparações permitem conferir o resultado integrado.

Em `mudancas_projeto/`, os três patches mostram as mudanças do projeto inteiro entre os commits, incluindo caminhos fora da seleção. As quatro pastas de código contêm somente os arquivos selecionados, não snapshots completos do projeto.

Consulte `metadata.json` para checksums, linhas originais do coletor e localização das cinco comparações por arquivo. Left e Right indicam a ordem dos pais, não nomes históricos de branches ou autoria individual.
'''
            (folder / 'README.md').write_text(readme, encoding='utf-8', newline='\n')
        with (package / 'indice.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(index[0]))
            writer.writeheader()
            writer.writerows(index)
        top = '''# Arquivos do piloto oficial para análise

Este pacote contém 5 cenários de merge do Underscore, 6 pares arquivo–merge e 24 versões de código. Ele deriva da saída preservada do MiningFramework oficial.

## Comece aqui

1. Abra `indice.csv` para localizar um arquivo e seu merge.
2. Entre na pasta identificada pelo SHA completo do merge.
3. Compare `base/` com `left/` para entender a primeira contribuição.
4. Compare `base/` com `right/` para entender a segunda contribuição.
5. Leia `merge/` e as comparações com os pais para analisar o resultado original.

Há 30 diffs dos arquivos selecionados e 15 patches de contexto do projeto. Os patches usam o formato padrão Git: linhas com `-` saem da versão anterior e linhas com `+` entram na seguinte. Os cabeçalhos `@@` informam as posições nas duas versões.

## Estrutura de cada cenário

```text
SHA_DO_MERGE/
  base/caminho/original.js
  left/caminho/original.js
  right/caminho/original.js
  merge/caminho/original.js
  diffs/base_left/caminho/original.js.diff
  diffs/base_right/caminho/original.js.diff
  diffs/base_merge/caminho/original.js.diff
  diffs/left_merge/caminho/original.js.diff
  diffs/right_merge/caminho/original.js.diff
  mudancas_projeto/base_left.patch
  mudancas_projeto/base_right.patch
  mudancas_projeto/base_merge.patch
  metadata.json
  README.md
```

O cenário `a2aab7c6996835d453972b22999b80dbfe125db5` contém dois arquivos selecionados. Os demais contêm um cada. Os caminhos distintos são `underscore.js` e `test/utility.js`.

## Conferir integridade sem clonar o projeto original

Com Python 3, execute dentro desta pasta:

```text
python verificar_pacote.py
```

O verificador confere os checksums e a presença das 24 versões. Não instala dependências nem executa o JavaScript. O arquivo `MANIFESTO.json` registra as contagens e os checksums. `metadata.json` de cada cenário registra os SHAs e as comparações.

## Escopo

Base é o ancestral comum único. Left é o primeiro pai e Right o segundo. As contribuições são diferenças acumuladas da base até cada pai, podendo envolver vários commits.

As pastas de código preservam somente os arquivos selecionados. Os patches de projeto ampliam o contexto, mas não substituem o checkout completo para executar testes. Para recuperar todo o projeto, use os SHAs completos registrados e o repositório https://github.com/jashkenas/underscore.

Os cenários foram selecionados por conveniência para validar a coleta. Sua inclusão não confirma defeito. Os critérios detalhados estão em `CRITERIOS_DE_MINERACAO.md` na raiz do repositório de entrega.

Fontes históricas do Underscore sob licença MIT, preservada em `LICENSE_UNDERSCORE.txt`.
'''
        (package / 'README.md').write_text(top, encoding='utf-8', newline='\n')
        (package / 'LICENSE_UNDERSCORE.txt').write_bytes((ROOT / 'licenses/underscore-LICENSE.txt').read_bytes())
        (package / 'verificar_pacote.py').write_bytes((ROOT / 'scripts/verificar_pacote_mineracao.py').read_bytes())
        # Include the criteria in the standalone ZIP, so it needs no other files.
        (package / 'CRITERIOS_DE_MINERACAO.md').write_bytes((ROOT / 'CRITERIOS_DE_MINERACAO.md').read_bytes())
        checksums = {p.relative_to(package).as_posix():digest(p.read_bytes())
                     for p in sorted(package.rglob('*')) if p.is_file()}
        manifest = dict(schema_version=1, project_url=PROJECT, merge_count=len(grouped),
                        file_merge_pairs=len(index), source_versions=source_count,
                        selected_file_diffs=5*len(index), project_context_patches=3*len(grouped),
                        input_csv='resultados/miningframework/saida_oficial/data/results.csv',
                        input_csv_sha256=digest(CSV.read_bytes()), merges=sorted(grouped),
                        files_sha256=checksums)
        save_json(package / 'MANIFESTO.json', manifest)
        assert source_count == 24 and patch_count == 45
        verify(package)
        # Destinations were checked above and stay inside the workspace.
        out.parent.mkdir(parents=True, exist_ok=True)
        package.rename(out)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, 'x') as zipped:
        for file in sorted(out.rglob('*')):
            if file.is_file():
                item = ZipInfo('piloto_oficial/' + file.relative_to(out).as_posix(), (1980,1,1,0,0,0))
                item.compress_type = ZIP_DEFLATED
                item.external_attr = 0o100644 << 16
                zipped.writestr(item, file.read_bytes())
    print(json.dumps(dict(package=str(out), archive=str(archive),
                         merges=5, file_merge_pairs=6, source_versions=24,
                         diffs=30, project_patches=15, zip_sha256=digest(archive.read_bytes())), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(ROOT / 'cenarios/piloto_oficial'))
    parser.add_argument('--zip', default=str(ROOT / 'entrega/cenarios_merge_piloto.zip'))
    args = parser.parse_args()
    main(args.out, args.zip)
