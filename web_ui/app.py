import os
from flask import Flask, render_template, request, redirect, url_for
from servicios.gestion_tareas import GestionTareas
from modelos.tarea import Tarea
from werkzeug.utils import secure_filename  

app = Flask(__name__)
DATA_DIR = os.path.join(os.getcwd(), 'data', 'baules') #ruta donde se alamacenan los baules
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'web_ui', 'static', 'uploads')  # Define la carpeta de carga alli alojare las img
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Extensiones permitidas

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER #carpeta de alojamiento para img
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea la carpeta si no existe

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_vault_files():
    return [f.replace('.json', '') for f in os.listdir(DATA_DIR) if f.endswith('.json')]

def get_gestor_tareas(vault_name):
    return GestionTareas(vault_name)

@app.route('/')
def index():
    vaults = get_vault_files()
    return render_template('index.html', vaults=vaults)

@app.route('/create_vault', methods=['GET', 'POST'])
def create_vault():
    if request.method == 'POST':
        vault_name = request.form['vault_name']
        if vault_name and vault_name not in get_vault_files():
            filename = GestionTareas._asegurar_extension_estatico(vault_name)
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'w') as f:
                f.write('[]')
            return redirect(url_for('index'))
        else:
            error = "El nombre del baúl no puede estar vacío o ya existe."
            return render_template('create_vault.html', error=error)
    return render_template('create_vault.html')

@app.route('/delete_vault/<vault_name>')
def delete_vault(vault_name):
    filename_to_delete = GestionTareas._asegurar_extension_estatico(vault_name)
    filepath_to_delete = os.path.join(DATA_DIR, filename_to_delete)
    try:
        os.remove(filepath_to_delete)
        return redirect(url_for('index'))
    except FileNotFoundError:
        error = f"No se encontró el baúl '{vault_name}'."
    except Exception as e:
        error = f"Error al eliminar el baúl '{vault_name}': {e}"

    vaults = get_vault_files()
    return render_template('index.html', vaults=vaults, delete_error=error)

@app.route('/vault/<vault_name>', methods=['GET'])
def task_list(vault_name):
    gestor = get_gestor_tareas(vault_name)
    tasks = gestor.obtener_tareas()
    estado_filtro = request.args.get('estado')
    grupo_filtro = request.args.get('grupo')

    if estado_filtro:
        tasks = gestor.filtrar_tareas_por_estado(estado_filtro)
    elif grupo_filtro:
        tasks = gestor.filtrar_tareas_por_grupo(grupo_filtro)

    grupos_unicos = sorted(list(set(tarea.get_grupo() for tarea in gestor.obtener_tareas() if tarea.get_grupo())))
    estados_unicos = Tarea.ESTADOS_VALIDOS

    return render_template('task_list.html', vault_name=vault_name, tasks=tasks,
                           estados_unicos=estados_unicos, grupos_unicos=grupos_unicos,
                           estado_seleccionado=estado_filtro, grupo_seleccionado=grupo_filtro)

@app.route('/vault/<vault_name>/create', methods=['GET', 'POST'])
def create_task(vault_name):
    gestor = get_gestor_tareas(vault_name)
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_limite = request.form['fecha_limite']
        grupo = request.form['grupo']
        estado = request.form['estado']
        medio_file = request.files['medio']  # Obtiene el archivo cargado

        medio_path = None
        if medio_file and allowed_file(medio_file.filename):
            filename = secure_filename(medio_file.filename)
            medio_path = os.path.join('/static/uploads', filename)  # Ruta relativa para la plantilla
            medio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        nueva_tarea = Tarea(titulo, descripcion, fecha_limite, grupo, estado, medio_path)
        gestor.agregar_tarea(nueva_tarea)
        return redirect(url_for('task_list', vault_name=vault_name))
    return render_template('create_task.html', vault_name=vault_name, estados_validos=Tarea.ESTADOS_VALIDOS)

@app.route('/vault/<vault_name>/edit/<task_id>', methods=['GET', 'POST'])
def edit_task(vault_name, task_id):
    gestor = get_gestor_tareas(vault_name)
    task_to_edit = None
    for task in gestor.obtener_tareas():
        if task.get_id() == task_id:
            task_to_edit = task
            break

    if not task_to_edit:
        return "Tarea no encontrada", 404

    if request.method == 'POST':
        task_to_edit.set_titulo(request.form['titulo'])
        task_to_edit.set_descripcion(request.form['descripcion'])
        task_to_edit.set_fecha_limite(request.form['fecha_limite'])
        task_to_edit.set_grupo(request.form['grupo'])
        task_to_edit.set_estado(request.form['estado'])

        medio_file = request.files['medio']
        if medio_file and allowed_file(medio_file.filename):
            filename = secure_filename(medio_file.filename)
            medio_path = os.path.join('/static/uploads', filename)
            medio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            task_to_edit.set_medio(medio_path)
        elif request.form.get('keep_medio'): # Si no se sube nuevo archivo, mantener el anterior
            pass
        else:
            task_to_edit.set_medio(None) # Si no se sube y no se pide mantener, eliminar

        gestor.guardar_tareas()
        return redirect(url_for('task_list', vault_name=vault_name))

    return render_template('edit_task.html', vault_name=vault_name, task=task_to_edit, estados_validos=Tarea.ESTADOS_VALIDOS)

@app.route('/vault/<vault_name>/delete/<task_id>')
def delete_task(vault_name, task_id):
    gestor = get_gestor_tareas(vault_name)
    gestor.eliminar_tarea_por_id(task_id)
    return redirect(url_for('task_list', vault_name=vault_name))

@app.route('/vault/<vault_name>/complete/<task_id>', methods=['GET', 'POST'])
def complete_task(vault_name, task_id):
    gestor = get_gestor_tareas(vault_name)
    if request.method == 'POST':
        try:
            gestor.cambiar_estado_tarea(task_id, "completada")
        except ValueError as e:
            return str(e), 400
        return redirect(url_for('task_list', vault_name=vault_name))
    return redirect(url_for('task_list', vault_name=vault_name))

if __name__ == '__main__':
    app.run(debug=True)