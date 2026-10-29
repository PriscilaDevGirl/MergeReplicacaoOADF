"""Confere o pacote entregue sem depender do Git ou de bibliotecas externas."""
import argparse
import hashlib
import json
from pathlib import Path


def verify(folder):
    root = Path(folder).resolve()
    manifest = json.loads((root / 'MANIFESTO.json').read_text(encoding='utf-8'))
    for relative, expected in manifest['files_sha256'].items():
        target = (root / relative).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Caminho fora do pacote: ' + relative)
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('Checksum diferente: ' + relative)
    versions = pairs = 0
    for merge in manifest['merges']:
        metadata = json.loads((root / merge / 'metadata.json').read_text(encoding='utf-8'))
        for selected in metadata['selected_files']:
            pairs += 1
            for role in ['base', 'left', 'right', 'merge']:
                record = selected['versions'][role]
                target = (root / record['file']).resolve()
                if not target.is_relative_to(root):
                    raise ValueError('Versao fora do pacote')
                if hashlib.sha256(target.read_bytes()).hexdigest() != record['sha256']:
                    raise ValueError('Versao alterada: ' + record['file'])
                versions += 1
    assert len(manifest['merges']) == manifest['merge_count']
    assert pairs == manifest['file_merge_pairs']
    assert versions == manifest['source_versions']
    result = dict(merges=len(manifest['merges']), file_merge_pairs=pairs,
                  source_versions=versions, checksummed_files=len(manifest['files_sha256']),
                  integrity='passed')
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', nargs='?', default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()
    verify(args.folder)
