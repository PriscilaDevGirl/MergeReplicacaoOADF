"""Runner do analisador OA independente para Jalangi2."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / 'analisador_oa/analysis.js'
JALANGI = ROOT / 'ferramentas/jalangi2/src/js/commands/jalangi.js'


def run_oa(files, script, output_dir, timeout=30):
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = dict(schema_version=1, implementation='independent-oa-v0.2',
                  files=files, output_path=str(output_dir / 'oa_report.json'), max_events=1000)
    config_path = output_dir / 'oa_config.json'
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    # Never read a stale report from an earlier attempt.
    report_path = Path(config['output_path'])
    if report_path.exists():
        report_path.unlink()
    preflight = subprocess.run(['node', str(ROOT / 'analisador_oa/preflight.js'), str(config_path)],
                               capture_output=True, timeout=timeout)
    (output_dir / 'preflight.stdout.txt').write_bytes(preflight.stdout)
    (output_dir / 'preflight.stderr.txt').write_bytes(preflight.stderr)
    if preflight.returncode:
        result = dict(status='unsupported_source', exit_code=preflight.returncode, report=None)
    else:
        cmd = ['node', str(JALANGI), '--inlineIID', '--inlineSource', '--analysis', str(ANALYZER), str(Path(script).resolve())]
        env = os.environ.copy()
        env['OA_CONFIG'] = str(config_path)
        try:
            proc = subprocess.run(cmd, cwd=Path(script).resolve().parent, env=env,
                                  capture_output=True, timeout=timeout)
            (output_dir / 'stdout.txt').write_bytes(proc.stdout)
            (output_dir / 'stderr.txt').write_bytes(proc.stderr)
            report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else None
            status = 'success' if proc.returncode == 0 and report else 'execution_error'
            result = dict(status=status, exit_code=proc.returncode, report=report, command=cmd)
        except subprocess.TimeoutExpired as exc:
            (output_dir / 'stdout.txt').write_bytes(exc.stdout or b'')
            (output_dir / 'stderr.txt').write_bytes(exc.stderr or b'')
            result = dict(status='timeout', exit_code=None, report=None, command=cmd)
    serializable = {k:v for k,v in result.items() if k != 'report'}
    serializable['analyzer_sha256'] = hashlib.sha256(ANALYZER.read_bytes()).hexdigest()
    (output_dir / 'execution.json').write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding='utf-8')
    return result
