from flask import Blueprint, request, jsonify
from extensions import db
from models.pago import Pago

pago_bp = Blueprint('pago_bp', __name__)

@pago_bp.route('/pagos', methods=['GET'])
def get_pagos():
    pagos = Pago.query.all()
    return jsonify([pago.as_dict() for pago in pagos])

@pago_bp.route('/pagos', methods=['POST'])
def add_pago():
    try:
        data = request.get_json()
        new_pago = Pago(
            MONTO=data['monto'],
            FECHA=data['fecha'],
            ID_USUARIO=data['id_usuario']
        )
        db.session.add(new_pago)
        db.session.commit()
        return jsonify({'message': 'Pago added!', 'ID_PAGO': new_pago.ID_PAGO}), 201
    except Exception as e:
        return str(e), 500

@pago_bp.route('/pagos/<int:id>', methods=['DELETE'])
def delete_pago(id):
    pago = Pago.query.get(id)
    if pago:
        db.session.delete(pago)
        db.session.commit()
        return jsonify({'message': 'Pago deleted!'}), 200
    else:
        return jsonify({'message': 'Pago not found'}), 404

@pago_bp.route('/pagos/<int:id>', methods=['PUT'])
def update_pago(id):
    pago = Pago.query.get(id)
    if pago:
        data = request.get_json()
        pago.MONTO = data.get('monto', pago.MONTO)
        pago.FECHA = data.get('fecha', pago.FECHA)
        pago.ID_USUARIO = data.get('id_usuario', pago.ID_USUARIO)
        db.session.commit()
        return jsonify({'message': 'Pago updated!', 'ID_PAGO': pago.ID_PAGO}), 200
    else:
        return jsonify({'message': 'Pago not found'}), 404