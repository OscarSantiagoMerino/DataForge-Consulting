"""Reproduce the documented red/green example without changing branches."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[1]
REVISIONS = [('red', 'c90a3258b3fbc296b8ca0ae5b875eaf603b86492', 1),
             ('green', 'd9d2b5287d0f9d6974956b28a5255d207884192e', 0)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=REPO / 'reports/tdd')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8')
    results = []
    with tempfile.TemporaryDirectory(prefix='finbank-tdd-') as temp:
        base = Path(temp).resolve()
        if base.parent != Path(tempfile.gettempdir()).resolve():
            raise RuntimeError('La copia temporal debe permanecer en el directorio temporal previsto')
        for label, revision, expected in REVISIONS:
            archive = base / (label + '.zip')
            subprocess.run(['git', 'archive', '--format=zip', f'--output={archive}', revision, 'src', 'tests', 'pyproject.toml'], cwd=REPO, check=True)
            snap = base / label
            snap.mkdir()
            with zipfile.ZipFile(archive) as z:
                z.extractall(snap)
            run = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider'], cwd=snap, env=env, capture_output=True, text=True, encoding='utf-8')
            output = run.stdout + run.stderr
            log = '\n'.join(line.rstrip() for line in output.splitlines()) + '\n'
            (out / (label + '.txt')).write_text(log, encoding='utf-8')
            ok = run.returncode == expected and ('1 failed, 11 passed' in output if label == 'red' else '12 passed' in output)
            results.append({'phase':label, 'commit':revision, 'exit_code':run.returncode, 'expected_exit_code':expected, 'verified':ok, 'log':label+'.txt'})
            print(label, revision[:7], 'verified' if ok else 'UNEXPECTED RESULT')
    (out / 'summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not all(row['verified'] for row in results):
        raise SystemExit('El ejemplo histórico difiere del resultado documentado')


if __name__ == '__main__':
    main()
