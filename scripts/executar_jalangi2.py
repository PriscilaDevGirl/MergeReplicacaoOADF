"""Executa analise BranchCoverage oficial em exemplo e amostra real.

O driver e uma verificacao adicional de exercitacao, nao um resultado OA.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "ferramentas/jalangi2"
EXPERIMENT = ROOT / "experimentos/jalangi2"
OUT = ROOT / "resultados/jalangi2"
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / "resultados/underscore_pre2015/amostras/8c15ae153aae_246afe7b9e/merge.js"
target = EXPERIMENT / "amostra_underscore/merge.js"
shutil.copyfile(source, target)
assert source.read_bytes() == target.read_bytes()
command = TOOL / "src/js/commands/jalangi.js"
analysis = TOOL / "src/js/sample_analyses/tutorial/BranchCoverage.js"
results = []
for name, script, marker in [
    ("exemplo", EXPERIMENT / "exemplo.js", "EXEMPLO_OK LRLRLRLRLR"),
    ("underscore_direto", target, None),
    ("underscore_driver", target.parent / "driver.js", "UNDERSCORE_DRIVER_OK [2,4,6]"),
]:
    for mode in ["original", "jalangi2"]:
        args = ["node", str(script)] if mode == "original" else [
            "node", str(command), "--inlineIID", "--inlineSource", "--analysis", str(analysis), str(script)]
        start = time.perf_counter()
        proc = subprocess.run(args, cwd=EXPERIMENT, capture_output=True, timeout=60)
        elapsed = time.perf_counter() - start
        stdout = proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr.decode("utf-8", "replace")
        (OUT / (name + "_" + mode + ".stdout.txt")).write_text(stdout, encoding="utf-8")
        (OUT / (name + "_" + mode + ".stderr.txt")).write_text(stderr, encoding="utf-8")
        locations = re.findall(r"^At location (.*?) 'true' branch", stdout, re.M)
        result = dict(case=name, mode=mode, command=args, exit_code=proc.returncode,
                      duration_seconds=elapsed, marker_expected=marker,
                      marker_found=marker in stdout if marker else None,
                      condition_locations_reported=len(locations),
                      unique_source_ranges=len(set(locations)))
        results.append(result)
        print(json.dumps(result, ensure_ascii=False))
        if proc.returncode != 0 or (marker and marker not in stdout):
            print(stderr)
            raise RuntimeError("Falha em " + name + " " + mode)
metadata = dict(
    tool="Samsung/jalangi2", version=json.loads((TOOL / "package.json").read_text())["version"],
    tool_sha=subprocess.check_output(["git", "-C", str(TOOL), "rev-parse", "HEAD"], text=True).strip(),
    node_version=subprocess.check_output(["node", "--version"], text=True).strip(),
    analysis="official tutorial/BranchCoverage.js", source_sample_id="8c15ae153aae_246afe7b9e",
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    results=results,
    note="Validacao de instrumentacao e cobertura; nao e o detector OA da Amanda. Tempos incluem instrumentacao e uma unica execucao, sem inferencia de desempenho.")
(OUT / "resumo.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
