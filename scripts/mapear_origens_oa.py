"""Mapa conservador de linhas preservadas: base/pais -> merge.

Usa hunks do Git, sem heuristicas de rename/move e sem correspondencia por
texto avulso. Linhas compartilhadas ou editadas no merge ficam explicitas.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def align(repo, before, after, path):
    old = git(repo, "show", f"{before}:{path}").splitlines()
    new = git(repo, "show", f"{after}:{path}").splitlines()
    diff = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--no-renames",
               "--unified=0", before, after, "--", path).decode("utf-8")
    if "Binary files" in diff:
        raise ValueError("Arquivo binario nao suportado")
    pattern = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", re.M)
    matches = list(pattern.finditer(diff))
    kept, changed = {}, set()
    oi = ni = 0
    for match in matches:
        os, oc, ns, nc = match.groups()
        os, ns = int(os), int(ns)
        oc = int(oc) if oc is not None else 1
        nc = int(nc) if nc is not None else 1
        ob = os - 1 if oc else os
        nb = ns - 1 if nc else ns
        assert ob - oi == nb - ni, (before, after, path, match.group())
        while oi < ob:
            assert old[oi] == new[ni]
            kept[oi + 1] = ni + 1
            oi += 1
            ni += 1
        changed.update(range(nb + 1, nb + nc + 1))
        oi, ni = ob + oc, nb + nc
    while oi < len(old) and ni < len(new):
        assert old[oi] == new[ni]
        kept[oi + 1] = ni + 1
        oi += 1
        ni += 1
    assert oi == len(old) and ni == len(new), (before, after, path)
    return kept, changed


def build_map(repo, merge, path, runtime_path):
    repo = Path(repo).resolve()
    parents = git(repo, "rev-list", "--parents", "-n", "1", merge).decode().split()
    if len(parents) != 3:
        raise ValueError("Exige merge de dois pais")
    merge, left, right = parents
    bases = git(repo, "merge-base", "--all", left, right).decode().split()
    if len(bases) != 1:
        raise ValueError("Exige ancestral comum unico")
    base = bases[0]
    raw = git(repo, "show", f"{merge}:{path}")
    raw.decode("utf-8")
    _, merge_changes = align(repo, base, merge, path)
    candidates = {i: [] for i in range(1, len(raw.splitlines()) + 1)}
    for branch, parent in [("L", left), ("R", right)]:
        _, parent_changes = align(repo, base, parent, path)
        preserved, _ = align(repo, parent, merge, path)
        for parent_line in sorted(parent_changes):
            merged_line = preserved.get(parent_line)
            if merged_line is not None:
                candidates[merged_line].append(dict(branch=branch, parent_line=parent_line))
    lines = {}
    for number, evidence in candidates.items():
        origins = {e["branch"] for e in evidence}
        if number not in merge_changes:
            origin = "BASE"
        elif origins == {"L"}:
            origin = "L"
        elif origins == {"R"}:
            origin = "R"
        elif origins == {"L", "R"}:
            origin = "SHARED"
        else:
            origin = "MERGE_ONLY"
        lines[str(number)] = dict(origin=origin, evidence=evidence)
    return dict(
        runtime_path=str(Path(runtime_path).resolve()), source_path=path,
        source_sha256=hashlib.sha256(raw).hexdigest(), merge_sha=merge,
        left_sha=left, right_sha=right, base_sha=base, lines=lines,
        method="Git zero-context hunks; changed parent lines preserved in merge",
        cautions=["Heuristic diff alignment, not semantic provenance", "No move/rename inference",
                  "SHARED and MERGE_ONLY require review; removed lines have no merge location",
                  "Line-level map does not separate operations on the same line"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ["repo", "merge", "path", "runtime-path", "out"]:
        parser.add_argument("--" + arg, required=True)
    args = parser.parse_args()
    result = build_map(args.repo, args.merge, args.path, args.runtime_path)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
