"""Confere SHAs, ancestrais e integridade das quatro versoes exportadas."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


def verify(repo, output):
    repo, output = Path(repo).resolve(), Path(output).resolve()
    records = []
    for metadata in sorted((output / "amostras").glob("*/metadata.json")):
        data = json.loads(metadata.read_text(encoding="utf-8"))
        parents = git(repo, "rev-list", "--parents", "-n", "1", data["merge_sha"]).decode().split()[1:]
        assert parents == [data["left_sha"], data["right_sha"]], metadata
        bases = git(repo, "merge-base", "--all", *parents).decode().split()
        assert bases == [data["base_sha"]], metadata
        for name in ["base", "left", "right", "merge"]:
            original = git(repo, "show", f'{data[name + "_sha"]}:{data["file_path"]}')
            local = (metadata.parent / (name + data["extension"])).read_bytes()
            assert original == local, (metadata, name)
            assert hashlib.sha256(local).hexdigest() == data["sha256"][name], (metadata, name)
        syntax = "not_applicable"
        if data["extension"] == ".js":
            result = subprocess.run(["node", "--check", str(metadata.parent / "merge.js")], capture_output=True)
            syntax = "passed" if result.returncode == 0 else "failed"
        records.append(dict(sample_id=data["sample_id"], parents_verified=True,
                            base_verified=True, four_versions_byte_identical=True,
                            sha256_verified=True, node_syntax_check=syntax))
    assert records, "Nenhuma amostra exportada"
    result = dict(samples_verified=len(records), versions_verified=4 * len(records),
                  records=records, note="Checks de integridade e sintaxe; nao verificam conflitos semanticos nem compatibilidade Jalangi2.")
    (output / "verificacao.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    verify(args.repo, args.out)
