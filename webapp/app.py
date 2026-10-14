from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import csv
import time
import threading
import sys
import re
from pathlib import Path

# Configurar PATH para YOSYS y Graphviz
YOSYS_PATH = r'C:\msys64\mingw64\bin'
GRAPHVIZ_PATH = r'C:\Program Files\Graphviz\bin'
os.environ['PATH'] = YOSYS_PATH + ';' + GRAPHVIZ_PATH + ';' + os.environ.get('PATH', '')
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Agregar el directorio raíz del proyecto al sys.path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

app = Flask(__name__, static_folder='static')
CORS(app)

OUTPUT_DIR = BASE_DIR / 'output'
TEMP_DIR = Path(__file__).parent / 'temp'
UCF_DIR = BASE_DIR / 'library' / 'constraints'
VERILOG_DIR = BASE_DIR / 'library' / 'verilogs'
LIBRARY_DIR = BASE_DIR / 'library'

TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

tasks = {}

UCF_LIST = ['Bth1C1G1T1', 'Eco1C1G1T1', 'Eco1C2G2T2', 'Eco2C1G3T1', 'Eco2C1G5T1', 'Eco2C1G6T1', 'SC1C1G1T1']


def get_ucf_configs():
    configs = set()
    for f in UCF_DIR.glob('*.UCF.json'):
        configs.add(f.stem.replace('.UCF', ''))
    return sorted(configs)


def get_verilogs():
    return sorted([f.stem for f in VERILOG_DIR.glob('*.v')])


def run_cello_task(task_id, verilog_name, ucf_name):
    try:
        tasks[task_id]['status'] = 'running'
        tasks[task_id]['message'] = 'Ejecutando YOSYS y scoring...'

        # Cambiar al directorio raíz para que logs/ funcione correctamente
        original_cwd = os.getcwd()
        os.chdir(BASE_DIR)
        
        try:
            from core_algorithm.celloAlgo import cello_initializer

            in_path = str(LIBRARY_DIR)
            out_path = str(OUTPUT_DIR)

            ucf_base = ucf_name
            ucf_file = ucf_base + '.UCF'
            in_file = ucf_base + '.input'
            out_file = ucf_base + '.output'

            options = {
                'yosys_cmd_choice': 1,
                'verbose': False,
                'log_overwrite': True,
                'print_iters': False,
                'exhaustive': False,
                'test_configs': False
            }

            result = cello_initializer(
                verilog_name, ucf_file, in_file, out_file,
                in_path, out_path, options
            )
        finally:
            os.chdir(original_cwd)

        if result and result.get('status') == 'FAILURE':
            tasks[task_id]['status'] = 'error'
            tasks[task_id]['message'] = result.get('msg', 'Error desconocido')
            return

        score_file = OUTPUT_DIR / verilog_name / f'{verilog_name}_{ucf_base}_circuit-score.csv'
        table_file = OUTPUT_DIR / verilog_name / f'{verilog_name}_{ucf_base}_activity-table.csv'

        score = None
        table = []
        labels = []

        if score_file.exists():
            with open(score_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                if rows:
                    score = float(rows[0][-1])

        if table_file.exists():
            with open(table_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) > 1:
                    labels = rows[0]
                    table = rows[1:]

        vdir = OUTPUT_DIR / verilog_name
        
        def find_png(pattern):
            pngs = list(vdir.glob(f'{pattern}.png'))
            return pngs[0].name if pngs else None
        
        def find_csv(pattern):
            csvs = list(vdir.glob(f'{pattern}.csv'))
            return csvs[0].name if csvs else None
            
        def find_zip(pattern):
            zips = list(vdir.glob(f'{pattern}.zip'))
            return zips[0].name if zips else None

        tasks[task_id]['status'] = 'done'
        tasks[task_id]['score'] = score
        tasks[task_id]['table'] = {'labels': labels, 'rows': table}
        tasks[task_id]['images'] = {
            'response_plots': find_png(f'{verilog_name}_{ucf_base}_response-plots'),
            'sbol_plot': find_png(f'{verilog_name}_{ucf_base}_dpl-sbol'),
            'tech_mapping': find_png(f'{verilog_name}_{ucf_base}_tech-mapping'),
        }
        tasks[task_id]['files'] = {
            'dna_designs': find_csv(f'{verilog_name}_{ucf_base}_dpl-dna-designs'),
            'sequences': find_csv(f'{verilog_name}_{ucf_base}_dna-sequences'),
            'zip': find_zip(f'{verilog_name}_{ucf_base}_all-files'),
        }
        tasks[task_id]['message'] = 'Completado'
        tasks[task_id]['ucf'] = ucf_base

    except Exception as e:
        import traceback
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['message'] = f'{str(e)}\n{traceback.format_exc()}'


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/configs')
def api_configs():
    return jsonify({'configs': get_ucf_configs(), 'verilogs': get_verilogs()})


@app.route('/api/run', methods=['POST'])
def api_run():
    verilog_name = request.form.get('verilog_name')
    ucf_name = request.form.get('ucf')
    uploaded_file = request.files.get('verilog_file')

    if not ucf_name:
        return jsonify({'error': 'Selecciona una configuración UCF'}), 400

    if uploaded_file and uploaded_file.filename:
        verilog_name = Path(uploaded_file.filename).stem
        # Sanitizar nombre: reemplazar espacios y caracteres especiales
        verilog_name = re.sub(r'[^\w\-]', '_', verilog_name).strip('_')
        verilog_path = VERILOG_DIR / f'{verilog_name}.v'
        uploaded_file.save(str(verilog_path))
    elif verilog_name:
        verilog_path = VERILOG_DIR / f'{verilog_name}.v'
    else:
        return jsonify({'error': 'Sube un archivo .v o selecciona uno de la librería'}), 400

    if not verilog_path.exists():
        return jsonify({'error': f'Archivo {verilog_path.name} no encontrado'}), 404

    task_id = f'{verilog_name}_{ucf_name}_{int(time.time())}'
    tasks[task_id] = {'status': 'running', 'message': 'Iniciando...', 'verilog': verilog_name, 'ucf': ucf_name}

    thread = threading.Thread(target=run_cello_task, args=(task_id, verilog_name, ucf_name))
    thread.start()

    return jsonify({'task_id': task_id})


@app.route('/api/status/<task_id>')
def api_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)


@app.route('/api/download/<task_id>/<file_type>')
def api_download(task_id, file_type):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    verilog_name = task['verilog']
    ucf = task.get('ucf', '')
    vdir = OUTPUT_DIR / verilog_name

    files = {
        'zip': f'{verilog_name}_{ucf}_all-files.zip',
        'dna': f'{verilog_name}_{ucf}_dpl-dna-designs.csv',
        'sequences': f'{verilog_name}_{ucf}_dna-sequences.csv',
        'score': f'{verilog_name}_{ucf}_circuit-score.csv',
        'table': f'{verilog_name}_{ucf}_activity-table.csv',
    }

    filename = files.get(file_type)
    if not filename:
        return jsonify({'error': 'Unknown file type'}), 400

    filepath = vdir / filename
    if not filepath.exists():
        return jsonify({'error': 'File not found'}), 404

    return send_file(str(filepath), as_attachment=True)


@app.route('/api/image/<task_id>/<image_type>')
def api_image(task_id, image_type):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    verilog_name = task['verilog']
    ucf = task.get('ucf', '')
    vdir = OUTPUT_DIR / verilog_name

    image_files = {
        'response': [f'{verilog_name}_{ucf}_response-plots.png', f'{verilog_name}_{ucf}_response-plots.pdf'],
        'sbol': [f'{verilog_name}_{ucf}_dpl-sbol.png'],
        'tech': [f'{verilog_name}_{ucf}_tech-mapping.png'],
    }

    candidates = image_files.get(image_type, [])
    for filename in candidates:
        filepath = vdir / filename
        if filepath.exists():
            return send_file(str(filepath))

    return jsonify({'error': 'Image not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
