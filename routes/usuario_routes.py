from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
from extensions import db
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.trabajadores import Trabajadores
from models.tipo_trabajador import TipoTrabajador
from models.manifiesto import Manifiesto
from models.pago import Pago
from flask_login import login_user, logout_user, login_required, current_user

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([usuario.as_dict() for usuario in usuarios])

@usuario_bp.route('/usuarios/new', methods=['GET'])
def new_usuario_form():
    return render_template('usuario_form.html')

@usuario_bp.route('/usuarios', methods=['POST'])
def add_usuario():
    try:
        data = request.get_json()
        new_usuario = Usuario(
            NOMBRE=data['NOMBRE'],
            EMAIL=data['EMAIL'],
            CONTRASEÑA=data['CONTRASEÑA'],
            TIPO_USUARIO=data['TIPO_USUARIO'],
            ID_EMPRESA=data.get('ID_EMPRESA')
        )
        db.session.add(new_usuario)
        db.session.commit()
        return jsonify({'message': 'Usuario added!', 'ID_USUARIO': new_usuario.ID_USUARIO}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'data': data}), 500

@usuario_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'message': 'Usuario deleted!'}), 200
    else:
        return jsonify({'message': 'Usuario not found'}), 404

@usuario_bp.route('/usuarios/<int:id>', methods=['GET'])
@login_required
def get_usuario(id):
    usuario = db.session.get(Usuario, id)
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict())

@usuario_bp.route('/usuarios/<int:id>', methods=['PUT'])
@login_required
def update_usuario(id):
    usuario = db.session.get(Usuario, id)
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    else:
        data = request.get_json()
        usuario.NOMBRE = data.get('NOMBRE', usuario.NOMBRE)
        usuario.EMAIL = data.get('EMAIL', usuario.EMAIL)
        usuario.CONTRASEÑA = data.get('CONTRASEÑA', usuario.CONTRASEÑA)
        usuario.TIPO_USUARIO = data.get('TIPO_USUARIO', usuario.TIPO_USUARIO)
        usuario.ID_EMPRESA = data.get('ID_EMPRESA', usuario.ID_EMPRESA)
        db.session.commit()
        return jsonify({'message': 'Usuario updated!', 'ID_USUARIO': usuario.ID_USUARIO}), 200

@usuario_bp.route('/login', methods=['GET'])
def login_form():
    return render_template('login_form.html')

@usuario_bp.route('/login', methods=['POST'])
def login():
    try:
        email = request.form['email']
        contraseña = request.form['contraseña']
        usuario = Usuario.query.filter_by(EMAIL=email, CONTRASEÑA=contraseña).first()
        if usuario:
            login_user(usuario)
            session['user_id'] = usuario.ID_USUARIO
            session['id_empresa'] = usuario.ID_EMPRESA
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('usuario_bp.inicio'))
        else:
            flash('Credenciales inválidas. Por favor intente nuevamente.', 'error')
            return redirect(url_for('usuario_bp.login_form'))
    except Exception as e:
        flash(f'Error al iniciar sesión: {str(e)}', 'error')
        return redirect(url_for('usuario_bp.login_form'))

@usuario_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('usuario_bp.login_form'))

@usuario_bp.route('/inicio', methods=['GET'])
@login_required
def inicio():
    id_empresa = current_user.ID_EMPRESA
    tractocamiones = Tractocamion.query.filter_by(ID_EMPRESA=id_empresa).all()
    trabajadores = db.session.query(Trabajadores, TipoTrabajador).join(TipoTrabajador, Trabajadores.ID_TIPO == TipoTrabajador.ID_TIPO).filter(Trabajadores.ID_EMPRESA == id_empresa).all()
    manifiestos = Manifiesto.query.all()
    tipos_trabajador = TipoTrabajador.query.all()
    pagos = Pago.query.all()
    return render_template('inicio.html', tractocamiones=tractocamiones, trabajadores=trabajadores, manifiestos=manifiestos, tipos_trabajador=tipos_trabajador, pagos=pagos)

@usuario_bp.route('/upload_folder', methods=['POST'])
@login_required
def upload_folder():
    if 'folder' not in request.files:
        return jsonify({'error': 'No folder part in the request'}), 400

    files = request.files.getlist('folder')
    if not files:
        return jsonify({'error': 'No files found in the folder'}), 400

    # Obtener el nombre de la carpeta desde el primer archivo
    first_file = files[0]
    folder_name = os.path.basename(os.path.dirname(first_file.filename))

    # Crear el directorio con el nombre de la carpeta
    upload_folder = os.path.join('uploads', str(session['id_empresa']), folder_name)
    os.makedirs(upload_folder, exist_ok=True)

    # Guardar los archivos en el directorio creado
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_folder, filename))

    return jsonify({'message': f'Folder "{folder_name}" uploaded successfully!'}), 200

@usuario_bp.route('/tractocamiones', methods=['GET'])
@login_required
def tractocamiones():
    id_empresa = current_user.ID_EMPRESA
    tractocamiones = Tractocamion.query.filter_by(ID_EMPRESA=id_empresa).all()
    return render_template('tractocamiones.html', tractocamiones=tractocamiones)

@usuario_bp.route('/trabajadores', methods=['GET'])
@login_required
def trabajadores():
    id_empresa = current_user.ID_EMPRESA
    trabajadores = db.session.query(Trabajadores, TipoTrabajador).join(TipoTrabajador, Trabajadores.ID_TIPO == TipoTrabajador.ID_TIPO).filter(Trabajadores.ID_EMPRESA == id_empresa).all()
    return render_template('trabajadores.html', trabajadores=trabajadores)

@usuario_bp.route('/manifiestos', methods=['GET'])
@login_required
def manifiestos():
    id_empresa = current_user.ID_EMPRESA
    trabajadores = Trabajadores.query.filter_by(ID_EMPRESA=id_empresa).all()
    tractocamiones = Tractocamion.query.filter_by(ID_EMPRESA=id_empresa).all()
    return render_template('manifiesto.html', trabajadores=trabajadores, tractocamiones=tractocamiones)

@usuario_bp.route('/listar_carpetas', methods=['GET'])
@login_required
def listar_carpetas():
    try:
        # Obtener el ID de la empresa desde la sesión
        id_empresa = current_user.ID_EMPRESA
        if not id_empresa:
            return jsonify({'error': 'No se encontró el ID de la empresa en la sesión'}), 400

        # Ruta de la carpeta de uploads para la empresa
        uploads_path = os.path.join('uploads', str(id_empresa))

        # Verificar si la carpeta existe
        if not os.path.exists(uploads_path):
            return jsonify({'carpetas': []}), 200

        # Listar las carpetas dentro de uploads/<id_empresa>
        carpetas = [nombre for nombre in os.listdir(uploads_path) if os.path.isdir(os.path.join(uploads_path, nombre))]
        return jsonify({'carpetas': carpetas}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


