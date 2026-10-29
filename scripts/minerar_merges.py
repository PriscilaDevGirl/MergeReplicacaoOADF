"""Piloto de mineracao local com Git; nao executa analise semantica.

Somente biblioteca padrao. Nao altera checkout, nao instala dependencias dos
projetos e nao faz chamadas de rede. Pais seguem a ordem armazenada no commit.
"""
import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def git(repo, *args, check=True):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    return proc


def txt(repo, *args):
    return git(repo, *args).stdout.decode("utf-8", "replace").strip()


def changed(repo, base, parent):
    raw = git(repo, "diff", "--name-only", "--no-renames", "-z", base, parent).stdout
    return {p.decode("utf-8") for p in raw.split(b"\0") if p}


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def mine(repo, out, extensions, until=None, export_limit=5):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    if out.exists():
        raise ValueError(f"Escolha uma pasta de saida nova: {out}")
    out.mkdir(parents=True)
    origin = txt(repo, "remote", "get-url", "origin")
    head = txt(repo, "rev-parse", "HEAD")
    if txt(repo, "rev-parse", "--is-shallow-repository") != "false":
        raise ValueError("Historico raso nao e aceito neste piloto")
    if until:
        datetime.strptime(until, "%Y-%m-%d")
    log = txt(repo, "log", "HEAD", "--merges", "--reverse", "--topo-order",
              "--format=%H%x09%P%x09%cI%x09%s")
    merges, files = [], []
    exports = []
    cutoff_excluded = 0
    for line in log.splitlines():
        sha, parents, date, subject = line.split("\t", 3)
        if until and date[:10] > until:
            cutoff_excluded += 1
            continue
        parents = parents.split()
        row = dict(merge_sha=sha, left_sha=parents[0], right_sha=parents[1],
                   base_sha="", committer_date=date, subject=subject,
                   parent_count=len(parents), common_files=0, candidate_files=0,
                   status="")
        merges.append(row)
        if len(parents) != 2:
            row["status"] = "excluded_not_two_parents"
            continue
        bases = txt(repo, "merge-base", "--all", *parents).splitlines()
        if len(bases) != 1:
            row["status"] = "excluded_no_unique_base"
            continue
        base = bases[0]
        row["base_sha"] = base
        if base in parents:
            row["status"] = "excluded_ancestor_parent"
            continue
        common = changed(repo, base, parents[0]) & changed(repo, base, parents[1])
        row["common_files"] = len(common)
        selected = sorted(p for p in common if Path(p).suffix in extensions)
        row["candidate_files"] = len(selected)
        row["status"] = "candidate" if selected else "no_common_selected_extension"
        for path in selected:
            sid = sha[:12] + "_" + hashlib.sha256(path.encode()).hexdigest()[:10]
            versions = dict(base=base, left=parents[0], right=parents[1], merge=sha)
            missing = [name for name, ref in versions.items()
                       if git(repo, "cat-file", "-e", f"{ref}:{path}", check=False).returncode]
            record = dict(sample_id=sid, project_url=origin, merge_sha=sha,
                          left_sha=parents[0], right_sha=parents[1], base_sha=base,
                          committer_date=date, file_path=path, extension=Path(path).suffix,
                          four_versions_present=not missing,
                          missing_versions="|".join(missing), exported=False,
                          semantic_label="unknown", dynamic_analysis="not_run")
            files.append(record)
            if not missing and len(exports) < export_limit:
                folder = out / "amostras" / sid
                folder.mkdir(parents=True)
                checksums = {}
                for name, ref in versions.items():
                    data = git(repo, "show", f"{ref}:{path}").stdout
                    (folder / (name + Path(path).suffix)).write_bytes(data)
                    checksums[name] = hashlib.sha256(data).hexdigest()
                for label, before, after in [
                    ("base_to_left", base, parents[0]),
                    ("base_to_right", base, parents[1]),
                    ("base_to_merge", base, sha),
                    ("left_to_merge", parents[0], sha),
                    ("right_to_merge", parents[1], sha),
                ]:
                    (folder / (label + ".diff")).write_bytes(git(
                        repo, "diff", "--no-ext-diff", "--no-textconv", "--no-renames",
                        "--unified=3", before, after, "--", path).stdout)
                record["exported"] = True
                (folder / "metadata.json").write_text(json.dumps(
                    {**record, "sha256": checksums}, ensure_ascii=False, indent=2), encoding="utf-8")
                exports.append(sid)
    summary = dict(
        repository=origin, head_sha=head, history_scope="ancestors of frozen HEAD",
        shallow=False, git_version=txt(repo, "--version"),
        executed_at_utc=datetime.now(timezone.utc).isoformat(),
        extensions=sorted(extensions), until_inclusive_committer_calendar_date=until,
        cutoff_note="Conservative pilot cutoff; not asserted to be Amanda's exact cutoff",
        all_merges_reachable_from_head=len(log.splitlines()),
        excluded_after_cutoff=cutoff_excluded, merges_in_scope=len(merges),
        merge_status_counts=dict(Counter(r["status"] for r in merges)),
        candidate_merges=len({r["merge_sha"] for r in files}), candidate_files=len(files),
        files_by_extension=dict(Counter(r["extension"] for r in files)),
        candidate_files_with_four_versions=sum(r["four_versions_present"] for r in files),
        exported_samples=len(exports), export_policy="first available in reverse topological log; convenience sample",
        original_miningframework_executed=False, semantic_detector_executed=False,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    write_csv(out / "merges.csv", merges, ["merge_sha", "left_sha", "right_sha", "base_sha",
              "committer_date", "subject", "parent_count", "common_files", "candidate_files", "status"])
    write_csv(out / "arquivos_candidatos.csv", files, ["sample_id", "project_url", "merge_sha",
              "left_sha", "right_sha", "base_sha", "committer_date", "file_path", "extension",
              "four_versions_present", "missing_versions", "exported", "semantic_label", "dynamic_analysis"])
    (out / "resumo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--extensions", nargs="+", default=[".js"])
    parser.add_argument("--until", help="Data inclusiva YYYY-MM-DD do committer; sem filtro por padrao")
    parser.add_argument("--export-limit", type=int, default=5)
    args = parser.parse_args()
    mine(args.repo, args.out, set(args.extensions), args.until, args.export_limit)
