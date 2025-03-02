from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from extensions import db
from models.usuario import Usuario
from models.tractocamion import Tractocamion
from models.conductor import Conductor
from models.viajes import Viajes
from models.mantenimiento import Mantenimiento
from models.tanqueo import Tanqueo

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
        data = request.form
        new_usuario = Usuario(
            NOMBRE=data['nombre'],
            EMAIL=data['email'],
            CONTRASEÑA=data['contraseña'],
            TIPO_USUARIO=data['tipo_usuario'],
            ID_EMPRESA=data.get('id_empresa')
        )
        db.session.add(new_usuario)
        db.session.commit()
        return jsonify({'message': 'Usuario added!', 'ID_USUARIO': new_usuario.ID_USUARIO}), 201
    except Exception as e:
        return str(e), 500

@usuario_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'message': 'Usuario deleted!'}), 200
    else:
        return jsonify({'message': 'Usuario not found'}), 404

@usuario_bp.route('/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        data = request.get_json()
        usuario.NOMBRE = data.get('nombre', usuario.NOMBRE)
        usuario.EMAIL = data.get('email', usuario.EMAIL)
        usuario.CONTRASEÑA = data.get('contraseña', usuario.CONTRASEÑA)
        usuario.TIPO_USUARIO = data.get('tipo_usuario', usuario.TIPO_USUARIO)
        usuario.ID_EMPRESA = data.get('id_empresa', usuario.ID_EMPRESA)
        db.session.commit()
        return jsonify({'message': 'Usuario updated!', 'ID_USUARIO': usuario.ID_USUARIO}), 200
    else:
        return jsonify({'message': 'Usuario not found'}), 404

@usuario_bp.route('/login', methods=['GET'])
def login_form():
    return render_template('login_form.html')

@usuario_bp.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    contraseña = request.form['contraseña']
    usuario = Usuario.query.filter_by(EMAIL=email, CONTRASEÑA=contraseña).first()
    if usuario:
        session['usuario_id'] = usuario.ID_USUARIO
        session['id_empresa'] = usuario.ID_EMPRESA
        return redirect(url_for('usuario_bp.inicio'))
    else:
        return 'Login failed', 401

@usuario_bp.route('/inicio', methods=['GET'])
def inicio():
    if 'usuario_id' not in session:
        return redirect(url_for('usuario_bp.login_form'))
    id_empresa = session['id_empresa']
    tractocamiones = Tractocamion.query.filter_by(ID_EMPRESA=id_empresa).all()
    conductores = Conductor.query.filter_by(ID_EMPRESA=id_empresa).all()
    return render_template('inicio.html', tractocamiones=tractocamiones, conductores=conductores)
