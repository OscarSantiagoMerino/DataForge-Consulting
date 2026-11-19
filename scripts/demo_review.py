"""Run the three prepared Sprint Review demonstrations from any checkout."""
from pathlib import Path
import argparse
import os
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--auto', action='store_true', help='Run without presentation pauses')
    parser.add_argument('--output-dir', type=Path, default=REPO / 'reports' / 'demo')
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8')

    def pause(text):
        print('\n' + text, flush=True)
        if not args.auto:
            input('Pulsa Enter para continuar...')

    print('FINBANK | SPRINT REVIEW DEL CORTE 2', flush=True)
    print('Muestra sintética; incremento de preparación de datos.', flush=True)
    pause('1. Ejecutar las pruebas de reglas y casos de borde.')
    subprocess.run([sys.executable, '-m', 'pytest', '-v', '-p', 'no:cacheprovider'], cwd=REPO, env=env, check=True)
    pause('2. Generar calidad y diccionario; calcular etiquetas de mora.')
    subprocess.run([sys.executable, str(REPO / 'scripts/run_pipeline.py'), str(args.output_dir.resolve())], cwd=REPO, env=env, check=True)
    pause('3. Comprobar el rechazo de una entrada inválida.')
    sys.path.insert(0, str(REPO / 'src'))
    from finbank.sample import generate_sample
    from finbank.validation import assert_valid
    table = generate_sample()
    table['bureau_score'][0] = 1200
    table['cedula'] = table['age'].copy()
    try:
        assert_valid(table)
    except ValueError as error:
        message = str(error)
        if 'above_maximum' not in message or 'personal_data_column' not in message:
            raise RuntimeError('El rechazo carece de alguna de las dos reglas esperadas') from error
        print('Entrada rechazada por las dos reglas esperadas:', message)
    else:
        raise RuntimeError('La entrada inválida pasó la validación')
    print('\nIncremento técnico integrado mediante PR #8; resultados reproducibles.')
    print('Aceptación del cliente y evidencia del evento: docs/SPRINT_REVIEW_ACCEPTANCE.md')
    print('Salidas de la demostración:', args.output_dir.resolve())


if __name__ == '__main__':
    main()
