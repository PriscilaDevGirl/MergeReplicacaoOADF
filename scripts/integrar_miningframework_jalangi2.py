"""Executa Jalangi2 sobre a saida real do MiningFramework.

Preserva erros como erros; nao implementa nem infere a analise OA.
"""
import csv
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "resultados/miningframework/saida_oficial/data/results.csv"
REPO = ROOT / "repositorios/underscore"
TOOL = ROOT / "ferramentas/jalangi2"
OUT = ROOT / "resultados/integracao_oficial"
STAGING = ROOT / "experimentos/integracao_oficial"
OUT.mkdir(parents=True, exist_ok=True)
STAGING.mkdir(parents=True, exist_ok=True)


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args])


rows = list(csv.DictReader(INPUT.open(encoding="utf-8-sig"), delimiter=";"))
results = []
for row in rows:
    sha, path = row["merge commit"], row["file path"]
    sid = sha[:12] + "_" + hashlib.sha256(path.encode()).hexdigest()[:10]
    folder = STAGING / sid
    folder.mkdir(exist_ok=True)
    source = folder / "merge.js"
    raw = git("show", sha + ":" + path)
    source.write_bytes(raw)
    versions = git("rev-list", "--parents", "-n", "1", sha).decode().split()
    assert len(versions) == 3
    base = git("merge-base", versions[1], versions[2]).decode().strip()
    record = dict(sample_id=sid, merge_sha=sha, left_sha=versions[1], right_sha=versions[2],
                  base_sha=base, file_path=path, source_sha256=hashlib.sha256(raw).hexdigest(),
                  miningframework_row=row, semantic_label="unknown", oa_detector_executed=False)
    for mode in ["original", "jalangi2"]:
        cmd = ["node", str(source)] if mode == "original" else ["node",
            str(TOOL / "src/js/commands/jalangi.js"), "--inlineIID", "--inlineSource",
            "--analysis", str(TOOL / "src/js/sample_analyses/tutorial/BranchCoverage.js"), str(source)]
        start = time.perf_counter()
        try:
            proc = subprocess.run(cmd, cwd=folder, capture_output=True, timeout=30)
            stdout, stderr = proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")
            code, status = proc.returncode, "success" if proc.returncode == 0 else "execution_error"
        except subprocess.TimeoutExpired as exc:
            stdout = (exc.stdout or b"").decode("utf-8", "replace")
            stderr = (exc.stderr or b"").decode("utf-8", "replace")
            code, status = None, "timeout"
        duration = time.perf_counter() - start
        (OUT / (sid + "_" + mode + ".stdout.txt")).write_text(stdout, encoding="utf-8")
        (OUT / (sid + "_" + mode + ".stderr.txt")).write_text(stderr, encoding="utf-8")
        locations = re.findall(r"^At location (.*?) 'true' branch", stdout, re.M)
        record[mode] = dict(command=cmd, exit_code=code, status=status, duration_seconds=duration,
                            reported_entries=len(locations), unique_source_ranges=len(set(locations)))
    results.append(record)
    print(sid, path, record["original"]["status"], record["jalangi2"]["status"])
summary = dict(
    source="MiningFramework DynamicAnalysisJsModifiedLinesDetectionModule output",
    selected_merges=len({r["merge_sha"] for r in results}), file_merge_pairs=len(results),
    original_success=sum(r["original"]["status"] == "success" for r in results),
    jalangi2_success=sum(r["jalangi2"]["status"] == "success" for r in results),
    jalangi2_errors=sum(r["jalangi2"]["status"] == "execution_error" for r in results),
    detector="official Jalangi2 tutorial/BranchCoverage.js; NOT Amanda OA detector",
    input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(), results=results,
    note="Arquivos isolados, sem instalar dependencias nem reconstruir todo o projeto; erros de contexto sao limitacao deste piloto. Tempos incluem instrumentacao, nao sao benchmark.")
(OUT / "resumo.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
with (OUT / "execucoes.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=["sample_id", "merge_sha", "file_path", "mode",
                                               "status", "exit_code", "unique_source_ranges"])
    writer.writeheader()
    for record in results:
        for mode in ["original", "jalangi2"]:
            writer.writerow({**{k: record[k] for k in ["sample_id", "merge_sha", "file_path"]},
                             "mode": mode, **{k: record[mode][k] for k in ["status", "exit_code", "unique_source_ranges"]}})
print(json.dumps({k:v for k,v in summary.items() if k != "results"}, ensure_ascii=False, indent=2))
