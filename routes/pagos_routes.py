from flask import Blueprint, request, jsonify
from extensions import db
from models.pago import Pago

pagos_bp = Blueprint('pagos_bp', __name__)

@pagos_bp.route('/pagos', methods=['POST'])
def agregar_pago():
    data = request.get_json()
    try:
        # Crear un nuevo pago
        nuevo_pago = Pago(
            
            tipo_pago=data['tipo_pago'],
            id_referencia=data['id_referencia'],
            monto=data['monto'],
            fecha_pago=data['fecha_pago'],
            descripcion=data.get('descripcion', '')
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        return jsonify({'message': 'Pago agregado correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al agregar el pago: {e}")
        return jsonify({'error': str(e)}), 500

@pagos_bp.route('/pagos/tipo/<string:tipo_pago>', methods=['GET'])
def obtener_pagos_por_tipo(tipo_pago):
    try:
        pagos = Pago.query.filter_by(tipo_pago=tipo_pago).all()
        return jsonify([{
            'id_pago': pago.id_pago,
            'placa': pago.placa,
            'tipo_pago': pago.tipo_pago,
            'id_referencia': pago.id_referencia,
            'monto': pago.monto,
            'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d'),
            'descripcion': pago.descripcion
        } for pago in pagos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pagos_bp.route('/pagos/<int:id_pago>', methods=['DELETE'])
def eliminar_pago(id_pago):
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({'error': 'Pago no encontrado'}), 404

        db.session.delete(pago)
        db.session.commit()
        return jsonify({'message': 'Pago eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500