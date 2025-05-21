from flask import Blueprint, request, jsonify, session
from extensions import db
from models.trabajadores import Trabajadores
from models.tipo_trabajador import TipoTrabajador
from models.detalles_conductores import DetallesConductores
from models.detalles_administrativos import DetallesAdministrativos

trabajadores_bp = Blueprint('trabajadores_bp', __name__)

@trabajadores_bp.route('/trabajadores', methods=['GET'])
def get_trabajadores():
    trabajadores = Trabajadores.query.all()
    return jsonify([trabajador.as_dict() for trabajador in trabajadores])

@trabajadores_bp.route('/trabajadores', methods=['POST'])
def add_trabajador():
    try:
        data = request.get_json()
        id_tipo = data['ID_TIPO']
        fecha_expedicion_licencia = data.get('FECHA_EXPEDICION_LICENCIA')

        # Validar que FECHA_EXPEDICION_LICENCIA sea NULL si ID_TIPO es 2
        if id_tipo == 2:
            fecha_expedicion_licencia = None

        new_trabajador = Trabajadores(
            NOMBRE=data['NOMBRE'],
            CEDULA=data['CEDULA'],
            FECHA_DE_PAGO=data['FECHA_DE_PAGO'],
            SUELDO=data['SUELDO'],
            ID_TIPO=id_tipo,
            ID_EMPRESA=session['id_empresa']
        )
        db.session.add(new_trabajador)
        db.session.commit()

        # Agregar detalles específicos según el tipo de trabajador
        if id_tipo == 1:  # Conductor
            new_detalles_conductores = DetallesConductores(
                ID_TRABAJADOR=new_trabajador.ID_TRABAJADOR,
                FECHA_EXPEDICION_LICENCIA=data['FECHA_EXPEDICION_LICENCIA'],
                ID_TRACTO=data['ID_TRACTO']
            )
            db.session.add(new_detalles_conductores)
        elif id_tipo == 2:  # Administrativo
            new_detalles_administrativos = DetallesAdministrativos(
                ID_TRABAJADOR=new_trabajador.ID_TRABAJADOR,
                DEPARTAMENTO=data['DEPARTAMENTO']
            )
            db.session.add(new_detalles_administrativos)

        db.session.commit()
        return jsonify({'message': 'Trabajador added!', 'ID_TRABAJADOR': new_trabajador.ID_TRABAJADOR}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'data': data}), 500

@trabajadores_bp.route('/trabajadores/<int:id>', methods=['DELETE'])
def delete_trabajador(id):
    trabajador = Trabajadores.query.get(id)
    if trabajador:
        # Eliminar detalles específicos según el tipo de trabajador
        if trabajador.ID_TIPO == 1:  # Conductor
            detalles_conductores = DetallesConductores.query.get(id)
            if detalles_conductores:
                db.session.delete(detalles_conductores)
        elif trabajador.ID_TIPO == 2:  # Administrativo
            detalles_administrativos = DetallesAdministrativos.query.get(id)
            if detalles_administrativos:
                db.session.delete(detalles_administrativos)

        db.session.delete(trabajador)
        db.session.commit()
        return jsonify({'message': 'Trabajador deleted!'}), 200
    else:
        return jsonify({'message': 'Trabajador not found'}), 404