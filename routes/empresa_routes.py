from flask import Blueprint, request, jsonify
from extensions import db
from models.empresa import Empresa

empresa_bp = Blueprint('empresa_bp', __name__)

@empresa_bp.route('/empresas', methods=['GET'])
def get_empresas():
    empresas = Empresa.query.all()
    return jsonify([empresa.as_dict() for empresa in empresas])

@empresa_bp.route('/empresas/<nombre>', methods=['GET'])
def get_empresa_by_nombre(nombre):
    empresa = Empresa.query.filter_by(NOMBRE=nombre).first()
    if empresa:
        return jsonify(empresa.as_dict())
    else:
        return jsonify({'message': 'Empresa not found'}), 404

@empresa_bp.route('/empresas', methods=['POST'])
def add_empresa():
    try:
        data = request.get_json()
        new_empresa = Empresa(
            NOMBRE=data['nombre']
        )
        db.session.add(new_empresa)
        db.session.commit()
        return jsonify({'message': 'Empresa added!', 'ID_EMPRESA': new_empresa.ID_EMPRESA}), 201
    except Exception as e:
        return str(e), 500

@empresa_bp.route('/empresas/<nombre>', methods=['DELETE'])
def delete_empresa(nombre):
    empresa = Empresa.query.filter_by(NOMBRE=nombre).first()
    if empresa:
        db.session.delete(empresa)
        db.session.commit()
        return jsonify({'message': 'Empresa deleted!'}), 200
    else:
        return jsonify({'message': 'Empresa not found'}), 404


@empresa_bp.route('/empresas/<int:id>', methods=['PUT'])
def update_empresa(id):
    empresa = Empresa.query.get(id)
    if empresa:
        data = request.get_json()
        empresa.NOMBRE = data.get('nombre', empresa.NOMBRE)
        db.session.commit()
        return jsonify({'message': 'Empresa updated!', 'ID_EMPRESA': empresa.ID_EMPRESA}), 200
    else:
        return jsonify({'message': 'Empresa not found'}), 404