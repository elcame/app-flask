from flask import Blueprint, request, jsonify
from extensions import db
from models.conductor import Conductor

conductor_bp = Blueprint('conductor_bp', __name__)

@conductor_bp.route('/conductores', methods=['GET'])
def get_conductores():
    conductores = Conductor.query.all()
    return jsonify([conductor.as_dict() for conductor in conductores])

@conductor_bp.route('/conductores', methods=['POST'])
def add_conductor():
    try:
        data = request.get_json()
        new_conductor = Conductor(
            NOMBRE=data['nombre'],
            CÉDULA=data['cédula'],
            NÚMERO_LICENCIA=data['numero_licencia'],
            FECHA_EXPEDICIÓN_LICENCIA=data['fecha_expedición_licencia'],
            CELULAR=data['celular'],
            ID_EMPRESA=data['id_empresa']
        )
        db.session.add(new_conductor)
        db.session.commit()
        return jsonify({'message': 'Conductor added!', 'ID_CONDUCTOR': new_conductor.ID_CONDUCTOR}), 201
    except Exception as e:
        return str(e), 500

@conductor_bp.route('/conductores/<int:id>', methods=['DELETE'])
def delete_conductor(id):
    conductor = Conductor.query.get(id)
    if conductor:
        db.session.delete(conductor)
        db.session.commit()
        return jsonify({'message': 'Conductor deleted!'}), 200
    else:
        return jsonify({'message': 'Conductor not found'}), 404

@conductor_bp.route('/conductores/<int:id>', methods=['PUT'])
def update_conductor(id):
    conductor = Conductor.query.get(id)
    if conductor:
        data = request.get_json()
        conductor.NOMBRE = data.get('nombre', conductor.NOMBRE)
        conductor.CÉDULA = data.get('cédula', conductor.CÉDULA)
        conductor.NÚMERO_LICENCIA = data.get('número_licencia', conductor.NÚMERO_LICENCIA)
        conductor.FECHA_EXPEDICIÓN_LICENCIA = data.get('fecha_expedición_licencia', conductor.FECHA_EXPEDICIÓN_LICENCIA)
        conductor.CELULAR = data.get('celular', conductor.CELULAR)
        conductor.ID_EMPRESA = data.get('id_empresa', conductor.ID_EMPRESA)
        db.session.commit()
        return jsonify({'message': 'Conductor updated!', 'ID_CONDUCTOR': conductor.ID_CONDUCTOR}), 200
    else:
        return jsonify({'message': 'Conductor not found'}), 404