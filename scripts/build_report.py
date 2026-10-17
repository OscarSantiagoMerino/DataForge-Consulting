"""Build the three-page report using the supplied LaTeX reference design."""
from pathlib import Path
import argparse
import re
import shutil
import subprocess
import tempfile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/report/Reporte_Sprints_Corte2.tex'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=SOURCE.with_suffix('.pdf'))
    args = parser.parse_args()
    engine = shutil.which('pdflatex')
    if engine is None:
        raise SystemExit('Instala una distribución LaTeX con pdflatex, lmodern y pgfplots (MiKTeX o TeX Live).')
    build = (ROOT / 'reports/pdf-build').resolve()
    if not build.is_relative_to(ROOT.resolve()):
        raise RuntimeError('El directorio de compilación debe permanecer dentro del proyecto')
    build.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='report-', dir=build) as temp:
        work = Path(temp).resolve()
        if work.parent != build:
            raise RuntimeError('Directorio temporal fuera de la carpeta de compilación prevista')
        command = [engine, '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error',
                   '-file-line-error', f'-output-directory={work}', str(SOURCE)]
        for _ in range(2):
            run = subprocess.run(command, cwd=SOURCE.parent, capture_output=True, text=True,
                                 encoding='utf-8', errors='replace')
            if run.returncode:
                raise SystemExit(run.stdout[-9000:] + run.stderr[-3000:])
        log = (work / SOURCE.with_suffix('.log').name).read_text(encoding='utf-8', errors='replace')
        overflows = [float(n) for n in re.findall(r'Overfull \\hbox \(([\d.]+)pt too wide\)', log)]
        if any(n > 1 for n in overflows):
            raise SystemExit(f'Texto fuera de margen: {overflows}. Revisa el archivo TeX.')
        result = work / SOURCE.with_suffix('.pdf').name
        pdf = PdfReader(result)
        if len(pdf.pages) != 3:
            raise SystemExit(f'El diseño requiere tres páginas; la compilación produjo {len(pdf.pages)}.')
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(result, output)
        print(f'Reporte verificado: {len(pdf.pages)} páginas; {output}')


if __name__ == '__main__':
    main()
